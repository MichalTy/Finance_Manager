import datetime
import json

from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from django.http import HttpResponseRedirect
from django.test import TestCase
from django.test.client import RequestFactory, Client
from django.urls import reverse

from .views import user_logout, fetch_expenses, fetch_data, charts_view, get_data
from .models import Budget, Expense, Income, Category
from .forms import ExpenseForm


class HomeViewTestCase(TestCase):
    def setUp(self):
        # Create a test user and log in
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

    def test_authenticated_user_with_data(self):
        # Test case for an authenticated user with existing data
        # Create a budget, expense, and income for the test user
        budget = Budget.objects.create(user=self.user, amount=1000)
        Expense.objects.create(user=self.user, category=self.create_category(), amount=500, date='2024-02-28')
        Income.objects.create(user=self.user, category=self.create_category(), amount=1500, date='2024-02-28')

        # Get the response from the home page
        response = self.client.get(reverse('home'))

        # Check if the response status code is 200 OK
        self.assertEqual(response.status_code, 200)
        # Check if the correct template is used
        self.assertTemplateUsed(response, 'home.html')
        # Check if the budget in the context matches the created budget
        self.assertEqual(response.context['budget'], budget)
        # Check if expenses and incomes exist in the context
        self.assertTrue(response.context['expenses'].exists())
        self.assertTrue(response.context['incomes'].exists())

    def test_authenticated_user_without_data(self):
        # Test case for an authenticated user without existing data
        # Get the response from the home page
        response = self.client.get(reverse('home'))

        # Check if the response status code is 200 OK
        self.assertEqual(response.status_code, 200)
        # Check if the correct template is used
        self.assertTemplateUsed(response, 'home.html')
        # Check if budget is None and there are no expenses or incomes in the context
        self.assertIsNone(response.context['budget'])
        self.assertFalse(response.context['expenses'].exists())
        self.assertFalse(response.context['incomes'].exists())

    def test_unauthenticated_user(self):
        # Test case for an unauthenticated user
        # Log out the user
        self.client.logout()
        # Get the response from the home page
        response = self.client.get(reverse('home'))

        # Check if the response status code is 200 OK
        self.assertEqual(response.status_code, 200)
        # Check if the correct template is used
        self.assertTemplateUsed(response, 'home.html')

    def create_category(self):
        # Helper function to create a category
        return Category.objects.create(name='Test Category', type='expense')


class UserLoginTestCase(TestCase):
    def setUp(self):
        # Set up test environment
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='test_user', email='test@example.com', password='test_password')

    def test_user_login(self):
        # Test user login with valid credentials
        request = self.factory.post(reverse('login'), {'username': 'test_user', 'password': 'test_password'})
        form = AuthenticationForm(request, data=request.POST)
        self.assertTrue(form.is_valid())
        response = self.client.post(reverse('login'), {'username': 'test_user', 'password': 'test_password'})
        self.assertTrue(response.status_code, 302)

    def test_invalid_user_login(self):
        # Test user login with invalid password
        request = self.factory.post(reverse('login'), {'username': 'test_user', 'password': 'wrong_password'})
        form = AuthenticationForm(request, data=request.POST)
        self.assertFalse(form.is_valid())

    def test_redirect_after_login(self):
        # Test redirection after successful login
        request = self.factory.post(reverse('login'), {'username': 'test_user', 'password': 'test_password'})
        form = AuthenticationForm(request, data=request.POST)
        self.assertTrue(form.is_valid())
        response = self.client.post(reverse('login'), {'username': 'test_user', 'password': 'test_password'})
        self.assertRedirects(response, reverse('home'))

    def test_login_form_rendering(self):
        # Test rendering of login form
        request = self.factory.get(reverse('login'))
        response = self.client.get(reverse('login'))
        self.assertTemplateUsed(response, 'login.html')
        self.assertIsInstance(response.context['form'], AuthenticationForm)

    def test_empty_password_login(self):
        # Test user login with empty password
        request = self.factory.post(reverse('login'), {'username': 'test_user', 'password': ''})
        form = AuthenticationForm(request, data=request.POST)
        self.assertFalse(form.is_valid())

    def test_empty_username_login(self):
        # Test user login with empty username
        request = self.factory.post(reverse('login'), {'username': '', 'password': 'test_password'})
        form = AuthenticationForm(request, data=request.POST)
        self.assertFalse(form.is_valid())

    def test_invalid_credentials_login(self):
        # Test user login with invalid credentials
        request = self.factory.post(reverse('login'), {'username': 'test_user', 'password': 'invalid_password'})
        form = AuthenticationForm(request, data=request.POST)
        self.assertFalse(form.is_valid())

    def test_invalid_http_method_login(self):
        # Test user login with invalid HTTP method
        request = self.factory.get(reverse('login'))
        form = AuthenticationForm(request, data={'username': 'test_user', 'password': 'test_password'})
        self.assertTrue(form.is_valid())


class RegisterTestCase(TestCase):
    def test_register_GET(self):
        # Test GET request to register page
        response = self.client.get(reverse('register'))
        # Check if the response status code is 200 OK
        self.assertEqual(response.status_code, 200)
        # Check if the correct template is used
        self.assertTemplateUsed(response, 'register.html')
        # Check if the form in the context is an instance of UserCreationForm
        self.assertIsInstance(response.context['form'], UserCreationForm)

    def test_register_POST_valid_form(self):
        # Test POST request to register page with valid form data
        data = {
            'username': 'testuser',
            'password1': 'testpassword123',
            'password2': 'testpassword123'
        }
        response = self.client.post(reverse('register'), data)
        # Check if the response status code is 302 Found (redirect)
        self.assertEqual(response.status_code, 302)
        # Check if a user is created
        self.assertEqual(User.objects.count(), 1)
        # Check if the created user exists in the database
        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_register_POST_invalid_form(self):
        # Test POST request to register page with empty form data
        data = {}
        response = self.client.post(reverse('register'), data)
        # Check if the response status code is 200 OK
        self.assertEqual(response.status_code, 200)
        # Check if no user is created
        self.assertFalse(User.objects.exists())

    def test_register_POST_password_mismatch(self):
        # Test POST request to register page with password mismatch
        data = {
            'username': 'testuser',
            'password1': 'testpassword123',
            'password2': 'differentpassword'
        }
        response = self.client.post(reverse('register'), data)
        # Check if the response status code is 200 OK
        self.assertEqual(response.status_code, 200)
        # Check if no user is created
        self.assertFalse(User.objects.exists())


class UserLogoutTestCase(TestCase):
    def setUp(self):
        # Set up test environment
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='password')

    def test_user_logged_out(self):
        # Test user logout functionality
        request = self.factory.get(reverse('home'))
        request.user = self.user

        # Simulate session middleware
        middleware = SessionMiddleware(lambda x: None)
        middleware.process_request(request)
        request.session.save()

        # Call user_logout function
        response = user_logout(request)

        # Check if response is a redirect to home page
        self.assertTrue(isinstance(response, HttpResponseRedirect))
        self.assertEqual(response.url, reverse('home'))
        # Check if user is anonymous after logout
        self.assertTrue(request.user.is_anonymous)

    def test_redirect_to_home(self):
        # Test redirection to home page after logout
        request = self.factory.get(reverse('home'))
        request.user = self.user

        # Simulate session middleware
        middleware = SessionMiddleware(lambda x: None)
        middleware.process_request(request)
        request.session.save()

        # Call user_logout function
        response = user_logout(request)

        # Check if response is a redirect to home page with status code 302
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('home'))


class BudgetSummaryTestCase(TestCase):
    def setUp(self):
        # Set up test environment
        self.user = User.objects.create_user(username='testuser', password='12345')

        # Create expense and income categories
        self.expense_category = Category.objects.create(name='Expense Category', type='expense')
        self.income_category = Category.objects.create(name='Income Category', type='income')

        # Create expense and income entries for the user
        Expense.objects.create(user=self.user, category=self.expense_category, amount=100, date='2024-02-01')
        Income.objects.create(user=self.user, category=self.income_category, amount=200, date='2024-02-02')

    def test_budget_summary(self):
        # Test budget summary functionality
        # Log in the user
        self.client.login(username='testuser', password='12345')

        # Make a GET request to the budget summary page
        response = self.client.get(reverse('budget_summary'))

        # Check if the response status code is 200 OK
        self.assertEqual(response.status_code, 200)

        # Check if the total income, total expense, and balance in the context match the expected values
        self.assertEqual(response.context['total_income'], 200)
        self.assertEqual(response.context['total_expense'], 100)
        self.assertEqual(response.context['balance'], 100)


class ExpensesListTestCase(TestCase):
    def setUp(self):
        # Set up test environment
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        # Log in the test user
        self.client.login(username='testuser', password='testpassword')

    def test_redirect_when_not_logged_in(self):
        # Test redirection when user is not logged in
        # Log out the user
        self.client.logout()
        # Make a GET request to the expenses list page
        response = self.client.get(reverse('expenses_list'))
        # Check if the response status code is 302 Found (redirect)
        self.assertEqual(response.status_code, 302)

    def test_expenses_list_authenticated_user(self):
        # Test expenses list for authenticated user
        # Create an expense category
        category = Category.objects.create(name='Test Category', type='expense')
        # Create an expense entry for the user
        Expense.objects.create(user=self.user, category=category, amount=100, date='2024-02-28')
        # Make a GET request to the expenses list page
        response = self.client.get(reverse('expenses_list'))
        # Check if the response status code is 200 OK
        self.assertEqual(response.status_code, 200)
        # Check if the correct template is used
        self.assertTemplateUsed(response, 'expenses_list.html')
        # Check if the response contains the test category
        self.assertContains(response, 'Test Category')

    def test_expenses_list_no_expenses(self):
        # Test expenses list when user has no expenses
        # Make a GET request to the expenses list page
        response = self.client.get(reverse('expenses_list'))
        # Check if the response status code is 200 OK
        self.assertEqual(response.status_code, 200)
        # Check if the correct template is used
        self.assertTemplateUsed(response, 'expenses_list.html')
        # Check if the response does not contain the test category
        self.assertNotContains(response, 'Test Category')


class AddExpenseViewTest(TestCase):
    def setUp(self):
        # Set up test environment
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        # Log in the test user
        self.client.login(username='testuser', password='testpassword')
        # Create an expense category
        self.category = Category.objects.create(name='Test Category', type='expense')
        # Define URL for adding expenses
        self.url = reverse('add_expenses')

    def test_get_request(self):
        # Test GET request to add expense page
        response = self.client.get(self.url)
        # Check if the response status code is 200 OK
        self.assertEqual(response.status_code, 200)
        # Check if the correct template is used
        self.assertTemplateUsed(response, 'add_expenses.html')
        # Check if the form in the context is an instance of ExpenseForm
        form = response.context['form']
        self.assertIsInstance(form, ExpenseForm)
        # Check if 'expense_categories' is in the response context
        self.assertTrue('expense_categories' in response.context)

    def test_post_valid_data(self):
        # Test POST request with valid expense data
        data = {
            'amount': 100,
            'category': self.category.id,
            'date': '2024-02-28',
            'comment': 'Test expense'
        }
        response = self.client.post(self.url, data)
        # Check if the response is a redirect to the expenses list page
        self.assertRedirects(response, reverse('expenses_list'))
        # Check if the expense is created and associated with the correct user
        self.assertTrue(Expense.objects.filter(user=self.user, amount=100, category=self.category).exists())

    def test_post_no_data(self):
        # Test POST request with no data
        response = self.client.post(self.url, {})
        # Check if the response status code is 200 OK
        self.assertEqual(response.status_code, 200)
        # Check if no expense is created
        self.assertFalse(Expense.objects.filter(user=self.user).exists())


class FetchDataTestCase(TestCase):
    def setUp(self):
        # Set up test environment
        self.factory = RequestFactory()
        # Create a test user
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        # Create a test category
        self.category = Category.objects.create(name='Test Category', type='expense')
        # Create a test expense
        self.expense = Expense.objects.create(user=self.user, category=self.category, amount=100,
                                              date=datetime.date.today())

    def test_fetch_data_all(self):
        # Test fetching all data
        # Create a GET request
        request = self.factory.get('/')
        # Set the user for the request
        request.user = self.user
        # Call the fetch_data function to fetch all expenses
        response = fetch_data(request, Expense, 'expenses_partial.html')
        # Check if the response status code is 200 OK
        self.assertEqual(response.status_code, 200)


class FetchExpensesTestCase(TestCase):
    def setUp(self):
        # Set up test environment
        self.factory = RequestFactory()
        # Create a test user
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        # Create a test category
        self.category = Category.objects.create(name='Test Category', type='expense')
        # Create a test expense
        self.expense = Expense.objects.create(user=self.user, category=self.category, amount=100,
                                              date=datetime.date.today())

    def test_fetch_expenses(self):
        # Test fetching expenses
        # Create a GET request
        request = self.factory.get('/')
        # Set the user for the request
        request.user = self.user
        # Call the fetch_expenses function to fetch expenses
        response = fetch_expenses(request)
        # Check if the response status code is 200 OK
        self.assertEqual(response.status_code, 200)


class IncomeListViewTests(TestCase):
    def setUp(self):
        # Set up test environment
        self.client = Client()
        # Create a test user and log them in
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

    def test_income_list_view_for_logged_in_user(self):
        # Test income list view for a logged-in user
        # Make a GET request to the incomes list page
        response = self.client.get(reverse('incomes_list'))
        # Check if the response status code is 200 OK
        self.assertEqual(response.status_code, 200)
        # Check if the correct template is used
        self.assertTemplateUsed(response, 'incomes_list.html')

    def test_income_list_view_queryset(self):
        # Test income list view queryset
        # Create a category and an income entry for the user
        category = Category.objects.create(name='Salary', type='income')
        income = Income.objects.create(user=self.user, category=category, amount=1000, date='2024-02-28')
        # Make a GET request to the incomes list page
        response = self.client.get(reverse('incomes_list'))
        # Check if the queryset in the response context contains the created income entry
        self.assertQuerysetEqual(
            response.context['incomes'],
            [income]
        )


class AddIncomeViewTests(TestCase):
    def setUp(self):
        # Set up test environment
        self.client = Client()
        # Create a test user and log them in
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

    def test_add_income_view_for_logged_in_user(self):
        # Test add income view for a logged-in user
        # Make a GET request to the add income page
        response = self.client.get(reverse('add_income'))
        # Check if the response status code is 200 OK
        self.assertEqual(response.status_code, 200)
        # Check if the correct template is used
        self.assertTemplateUsed(response, 'add_incomes.html')

    def test_add_income_redirects_on_successful_submission(self):
        # Test redirection after successful income submission
        # Create a category
        category = Category.objects.create(name='Salary', type='income')
        # Make a POST request to add income with valid data
        response = self.client.post(reverse('add_income'), {
            'amount': 1000,
            'category': category.pk,
            'date': '2024-02-28',
            'comment': 'Test income'
        })
        # Check if the response redirects to the income list page
        self.assertRedirects(response, reverse('incomes_list'))

    def test_add_income_creates_new_income_object(self):
        # Test creation of new income object
        # Create a category
        category = Category.objects.create(name='Salary', type='income')
        # Make a POST request to add income
        self.client.post(reverse('add_income'), {
            'amount': 1000,
            'category': category.pk,
            'date': '2024-02-28',
            'comment': 'Test income'
        })
        # Check if the number of income objects is now 1
        self.assertEqual(Income.objects.count(), 1)


class ChartsViewTestCase(TestCase):
    def setUp(self):
        # Set up test environment
        self.factory = RequestFactory()
        # Create a test user
        self.user = User.objects.create_user(username='test_user', email='test@example.com', password='test_password')
        # Create test expense and income categories
        self.category_expense = Category.objects.create(name='Test Expense Category', type='expense')
        self.category_income = Category.objects.create(name='Test Income Category', type='income')

    def test_page_accessibility(self):
        # Test accessibility of the charts page
        # Set URL for charts page
        url = reverse('charts')
        # Create a GET request for the charts page
        request = self.factory.get(url)
        # Set the user for the request
        request.user = self.user
        # Call the charts_view function
        response = charts_view(request)
        # Check if the response status code is 200 OK
        self.assertEqual(response.status_code, 200)

    def test_available_years(self):
        # Test availability of years on the charts page
        # Create an expense entry for the user
        Expense.objects.create(user=self.user, category=self.category_expense, amount=100, date='2023-01-01')
        # Set URL for charts page
        url = reverse('charts')
        # Create a GET request for the charts page
        request = self.factory.get(url)
        # Set the user for the request
        request.user = self.user
        # Call the charts_view function
        response = charts_view(request)
        # Check if the year 2023 is present in the response content
        years_available = False
        if '2023' in response.content.decode():
            years_available = True
        self.assertTrue(years_available)


class GetDataTest(TestCase):
    class GetDataTest(TestCase):
        def setUp(self):
            self.user = User.objects.create_user(username='testuser', password='testpassword')

            self.category_income = Category.objects.create(name='Income', type='income')
            self.category_expense = Category.objects.create(name='Expense', type='expense')

            self.income1 = Income.objects.create(user=self.user, category=self.category_income, amount=100,
                                                 date='2024-01-15')
            self.income2 = Income.objects.create(user=self.user, category=self.category_income, amount=200,
                                                 date='2024-01-20')
            self.expense1 = Expense.objects.create(user=self.user, category=self.category_expense, amount=25,
                                                   date='2024-01-10')
            self.expense2 = Expense.objects.create(user=self.user, category=self.category_expense, amount=100,
                                                   date='2024-01-25')

        def test_get_data(self):
            request = RequestFactory().get(reverse('get_data'), {'year': 2024})
            request.user = self.user

            response = get_data(request)
            self.assertEqual(response.status_code, 200)

            data = json.loads(response.content.decode('utf-8'))
            self.assertEqual(len(data), 12)
            self.assertEqual(int(data[0]['income']), 300)
            self.assertEqual(int(data[0]['expense']), 125)
            self.assertEqual(int(data[0]['balance']), 175)

        def test_get_data_missing_year(self):
            request = RequestFactory().get(reverse('get_data'))
            request.user = self.user

            response = get_data(request)
            self.assertEqual(response.status_code, 400)


class CategoriesViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.expense_category = Category.objects.create(name='Test Expense Category', type='expense')
        self.income_category = Category.objects.create(name='Test Income Category', type='income')

    def test_categories_view(self):
        self.client.login(username='testuser', password='12345')
        url = reverse('categories')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'categories.html')
        expected_ids = [self.expense_category.id]
        actual_ids = [category.id for category in response.context['expense_categories']]
        self.assertListEqual(expected_ids, actual_ids)


class TestViews(TestCase):

    def setUp(self):
        self.client = Client()
        self.categories_expense_url = reverse('categories_expense')
        self.categories_income_url = reverse('categories_income')
        self.delete_category_url = reverse('delete_category', args=[1])
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        self.category1 = Category.objects.create(name='Test Expense Category', type='expense')
        self.category2 = Category.objects.create(name='Test Income Category', type='income')

    def test_categories_expense_view(self):
        response = self.client.get(self.categories_expense_url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'categories_expense.html')

    def test_categories_income_view(self):
        response = self.client.get(self.categories_income_url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'categories_income.html')
