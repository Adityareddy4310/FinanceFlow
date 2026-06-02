# from django.db import models
from django.db import models
from django.contrib.auth.models import User


class FinanceGroup(models.Model):
    """Each finance group belongs to a user (e.g., Vizag Finance, Eluru Finance)"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)  # e.g., "Vizag Finance"
    day = models.CharField(max_length=20)     # e.g., "Sunday"
    location = models.CharField(max_length=100)  # e.g., "Vizag"
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']


class Borrower(models.Model):
    """Each borrower belongs to a finance group"""
    finance_group = models.ForeignKey(FinanceGroup, on_delete=models.CASCADE, related_name='borrowers')
    name = models.CharField(max_length=100)
    amount_given = models.DecimalField(max_digits=10, decimal_places=2)  # Principal amount
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.finance_group.name}"

    class Meta:
        ordering = ['created_at']

    @property
    def total_paid(self):
        """Calculate total amount paid so far"""
        payments = self.weekly_payments.all()
        total = sum(float(p.amount_paid) for p in payments)
        return total

    @property
    def balance(self):
        """Calculate remaining balance"""
        return float(self.amount_given) - self.total_paid


class WeeklyPayment(models.Model):
    """Each payment record for a borrower on a specific date"""
    borrower = models.ForeignKey(Borrower, on_delete=models.CASCADE, related_name='weekly_payments')
    payment_date = models.DateField()  # e.g., 2026-02-06
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.borrower.name} - {self.payment_date}: ₹{self.amount_paid}"

    class Meta:
        ordering = ['payment_date']
        unique_together = ('borrower', 'payment_date')  # One payment per borrower per date