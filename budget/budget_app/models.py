from django.db import models
from django.contrib.auth.models import User


# Category model
class Category(models.Model):
    name = models.CharField(max_length=100)  # Represents a category such as 'Paycheck', 'Transport', etc.
    type = models.CharField(max_length=10,
                            default='expense')  # Indicates whether the category is for expenses or incomes


# Transaction model
class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Refers to the user who made the transaction
    category = models.ForeignKey(Category, on_delete=models.CASCADE)  # Refers to the category of the transaction
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Represents the amount of the transaction
    date = models.DateField()  # Indicates the date of the transaction
    type = models.CharField(max_length=10)  # Indicates whether the transaction is an income or an expense


# Budget model
class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Refers to the user for whom the budget is set
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)  # Refers to the category of the budget
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Represents the budgeted amount for the category


# Spending model
class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Refers to the user who made the expense
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='expense_category')
    # Refers to the category of the expense
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Represents the amount of the expense
    date = models.DateField()  # Indicates the date of the expense
    comment = models.TextField(blank=True,
                               null=True)  # Allows adding additional comments or description for the expense


# Revenue model
class Income(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Refers to the user who earned the income
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='income_category')
    # Refers to the category of the income
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Represents the amount of the income
    date = models.DateField()  # Indicates the date of the income
    comment = models.TextField(blank=True, null=True)  # Allows adding additional comments or description for the income
