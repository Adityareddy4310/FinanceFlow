from django.db import models
from django.contrib.auth.models import User
from datetime import date


class FinanceGroup(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    day = models.CharField(max_length=20)
    location = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']


class Borrower(models.Model):
    finance_group = models.ForeignKey(FinanceGroup, on_delete=models.CASCADE, related_name='borrowers')
    name = models.CharField(max_length=100)
    amount_given = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    date_of_loan = models.DateField(default=date.today)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.finance_group.name}"

    class Meta:
        ordering = ['created_at']

    @property
    def total_paid(self):
        weekly_payments = self.weekly_payments.all()
        weekly_total = sum(float(p.amount_paid) for p in weekly_payments)
        return float(self.amount_paid) + weekly_total

    @property
    def balance(self):
        return float(self.amount_given) - self.total_paid


class WeeklyPayment(models.Model):
    borrower = models.ForeignKey(Borrower, on_delete=models.CASCADE, related_name='weekly_payments')
    payment_date = models.DateField()
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.borrower.name} - {self.payment_date}: ₹{self.amount_paid}"

    class Meta:
        ordering = ['payment_date']
        unique_together = ('borrower', 'payment_date')