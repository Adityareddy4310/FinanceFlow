from django.db import models
from django.contrib.auth.models import User
from datetime import date


class FinanceGroup(models.Model):
    FINANCE_TYPE_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
    ]

    COLLECTION_DAY_CHOICES = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    day = models.CharField(max_length=50)
    location = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    finance_type = models.CharField(
        max_length=10,
        choices=FINANCE_TYPE_CHOICES,
        default='daily'
    )

    collection_day = models.CharField(
        max_length=10,
        choices=COLLECTION_DAY_CHOICES,
        default='monday'
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']


class Borrower(models.Model):
    finance_group = models.ForeignKey(FinanceGroup, on_delete=models.CASCADE, related_name='borrowers')
    serial_number = models.IntegerField()
    name = models.CharField(max_length=100, blank=True, default='')
    amount_given = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    date_of_loan = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Blocker 1 — soft delete. Deleting a borrower from active records no
    # longer hard-deletes them (and cascades away their WeeklyPayment
    # history); it archives them instead. Historical cash-flow/reporting
    # queries must NOT filter on this field — only "active borrower list"
    # views should.
    is_archived = models.BooleanField(default=False)

    # Blocker 2 — same-day old-loan-clear + new-loan. Incremented once per
    # Give New Loan call. WeeklyPayment rows are stamped with the borrower's
    # loan_cycle at the moment they're saved, so a payment made under the
    # old cycle is never reinterpreted as belonging to the new one, even if
    # both happen on the same calendar date.
    loan_cycle = models.IntegerField(default=1)

    def __str__(self):
        if self.name:
            return f"#{self.serial_number}. {self.name}"
        return f"#{self.serial_number}. [Empty]"

    class Meta:
        ordering = ['serial_number']
        unique_together = ('finance_group', 'serial_number')

    @property
    def is_empty(self):
        return not self.name

    @property
    def total_paid(self):
        """
        Sums only WeeklyPayment rows stamped with this borrower's CURRENT
        loan_cycle. A previous cycle's payments (including a same-day final
        payment that closed the old loan) are excluded here without being
        deleted or modified — they remain permanently queryable via
        weekly_payments.filter(loan_cycle=<old cycle number>).
        """
        if self.is_empty:
            return 0
        weekly_total = sum(
            float(p.amount_paid)
            for p in self.weekly_payments.filter(loan_cycle=self.loan_cycle)
        )
        return float(self.amount_paid) + weekly_total

    @property
    def balance(self):
        if self.is_empty:
            return 0
        return float(self.amount_given) - self.total_paid


class WeeklyPayment(models.Model):
    borrower = models.ForeignKey(Borrower, on_delete=models.CASCADE, related_name='weekly_payments')
    payment_date = models.DateField()
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    loan_cycle = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.borrower.name} - {self.payment_date}: ₹{self.amount_paid} (cycle {self.loan_cycle})"

    class Meta:
        ordering = ['payment_date']
        unique_together = ('borrower', 'payment_date', 'loan_cycle')


class DailyExpense(models.Model):
    finance_group = models.ForeignKey(FinanceGroup, on_delete=models.CASCADE, related_name='daily_expenses')
    date = models.DateField()
    category = models.CharField(max_length=20, choices=[
        ('petrol', 'Petrol'), ('food', 'Food'), ('room_rent', 'Room Rent'),
        ('salaries', 'Employee Salaries'), ('misc', 'Miscellaneous'),
    ])
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)


class DailyInterest(models.Model):
    finance_group = models.ForeignKey(FinanceGroup, on_delete=models.CASCADE, related_name='daily_interests')
    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        unique_together = ('finance_group', 'date')


class Employee(models.Model):
    """
    Collection staff, scoped to the account owner (not per-group) since the
    same person may collect for multiple finance groups. Add more via
    Django admin — no code change needed.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='employees')
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class LoanHistory(models.Model):
    """
    Append-only snapshot of a CLOSED loan cycle, written by give_new_loan
    right before it resets Borrower for the new cycle. Borrower.amount_given/
    amount_paid/date_of_loan remain single mutable fields describing only the
    CURRENT cycle (unchanged) — this table is the only place prior cycles
    are recoverable from, since overwriting those fields would otherwise
    lose that information permanently.
    """
    borrower = models.ForeignKey(Borrower, on_delete=models.CASCADE, related_name='loan_history')
    loan_amount = models.DecimalField(max_digits=10, decimal_places=2)
    total_paid = models.DecimalField(max_digits=10, decimal_places=2)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    started_on = models.DateField(null=True, blank=True)
    closed_on = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-closed_on', '-created_at']


class CollectionStaffEntry(models.Model):
    """
    One row per (finance_group, date, employee). Multiple collectors on the
    same date = multiple rows, not duplicated cash-flow dates.
    """
    finance_group = models.ForeignKey(FinanceGroup, on_delete=models.CASCADE, related_name='collection_staff_entries')
    date = models.DateField()
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='collection_entries')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('finance_group', 'date', 'employee')