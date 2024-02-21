from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Expense, Income, Category
from datetime import datetime, timedelta


class ExpenseModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test_user', password='test_password')
        self.category = Category.objects.create(name='Test Category')
        self.expense = Expense.objects.create(
            user=self.user,
            category=self.category,
            amount=100.00,
            date=datetime.now().date()
        )

    def test_expense_creation(self):
        self.assertEqual(self.expense.user, self.user)
        self.assertEqual(self.expense.category, self.category)
        self.assertEqual(self.expense.amount, 100.00)
        self.assertEqual(self.expense.date, datetime.now().date())


class ViewsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test_user', password='test_password')
        self.client.login(username='test_user', password='test_password')

    def test_add_expense(self):
        response = self.client.post(reverse('add_expenses'), {
            'amount': 50.00,
            'category': 'Test Category',
            'date': datetime.now().date(),
        })
        self.assertEqual(response.status_code, 302)

        expenses = Expense.objects.filter(user=self.user)
        self.assertEqual(len(expenses), 1)

    def test_fetch_expenses(self):
        response = self.client.get(reverse('fetch_expenses'))
        self.assertEqual(response.status_code, 200)

    def test_add_income(self):
        response = self.client.post(reverse('add_income'), {
            'amount': 200.00,
            'category': 'Test Category',
            'date': datetime.now().date(),
        })
        self.assertEqual(response.status_code, 302)

        incomes = Income.objects.filter(user=self.user)
        self.assertEqual(len(incomes), 1)

    def test_fetch_incomes(self):
        response = self.client.get(reverse('fetch_incomes'))
        self.assertEqual(response.status_code, 200)

    def test_budget_summary(self):
        response = self.client.get(reverse('budget_summary'))
        self.assertEqual(response.status_code, 200)

    def test_user_login(self):
        response = self.client.post(reverse('login'), {'username': 'test_user', 'password': 'test_password'})
        self.assertEqual(response.status_code, 302)

    def test_user_logout(self):
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)

    def test_register_user(self):
        response = self.client.post(reverse('register'),
                                    {'username': 'new_user', 'password1': 'new_password', 'password2': 'new_password'})
        self.assertEqual(response.status_code, 302)

        new_user = User.objects.get(username='new_user')
        self.assertIsNotNone(new_user)


class ModelsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test_user', password='test_password')
        self.category = Category.objects.create(name='Test Category')

    def test_expense_creation(self):
        expense = Expense.objects.create(user=self.user, category=self.category, amount=50.0, date='2024-02-16')
        self.assertEqual(expense.user.username, 'test_user')
        self.assertEqual(expense.amount, 50.0)
        self.assertEqual(expense.category.name, 'Test Category')

    def test_income_creation(self):
        income = Income.objects.create(user=self.user, category=self.category, amount=100.0, date='2024-02-16')
        self.assertEqual(income.user.username, 'test_user')
        self.assertEqual(income.amount, 100.0)
        self.assertEqual(income.category.name, 'Test Category')


class IntegrationTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test_user', password='test_password')
        self.client.login(username='test_user', password='test_password')

    def test_expenses_list_view(self):
        response = self.client.get(reverse('expenses_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'expenses_list.html')

    def test_add_expenses_view(self):
        response = self.client.get(reverse('add_expenses'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'add_expenses.html')

        data = {
            'amount': 50.0,
            'category': 'Test Category',
            'date': '2024-02-16'
        }
        response = self.client.post(reverse('add_expenses'), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Expense.objects.count(), 1)
