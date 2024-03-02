from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    '''
    Model representing a category, such as 'Paycheck', 'Transport', etc.
    '''
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=10, default='expense')


class Transaction(models.Model):
    '''
    Model representing a transaction.
    '''
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    type = models.CharField(max_length=10)


class Budget(models.Model):
    '''
    Model representing a budget.
    '''
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)


class Expense(models.Model):
    '''
    Model representing an expense.
    '''
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='expense_category')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    comment = models.TextField(blank=True, null=True)


class Income(models.Model):
    '''
    Model representing an income.
    '''
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='income_category')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    comment = models.TextField(blank=True, null=True)
