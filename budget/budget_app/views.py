import csv  # Importing CSV module for CSV file operations
import json  # Importing JSON module for JSON data operations

from datetime import datetime, timedelta

from django.core.serializers.json import DjangoJSONEncoder  # Importing Django JSON Encoder
from django.contrib.auth import login, logout  # Importing login and logout functions from Django authentication
from django.contrib.auth.decorators import login_required  # Importing login_required decorator for view authorization
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm  # Importing authentication forms
from django.db.models import Sum  # Importing Sum function for aggregation in Django queries
from django.http import HttpResponse, JsonResponse  # Importing HttpResponse and JsonResponse for HTTP responses
from django.shortcuts import render, redirect  # Importing render and redirect for rendering templates and redirection

from reportlab.lib import colors  # Importing colors module from ReportLab library
from reportlab.lib.pagesizes import letter  # Importing letter page size from ReportLab library
from reportlab.lib.styles import getSampleStyleSheet  # Importing style sheet from ReportLab library
from reportlab.platypus import SimpleDocTemplate, Table, \
    TableStyle  # Importing PDF generation components from ReportLab library

from .forms import CategoryForm, ExpenseForm, IncomeForm
from .models import Budget, Category, Expense, Income


# Function to render home page
def home(request):
    # Check if the user is authenticated
    if request.user.is_authenticated:
        # Retrieve the budget for the current user
        budget = Budget.objects.filter(user=request.user).first()
        # Retrieve expenses for the current user
        expenses = Expense.objects.filter(user=request.user)
        # Retrieve incomes for the current user
        incomes = Income.objects.filter(user=request.user)
        # Prepare context data with budget, expenses, and incomes
        context = {
            'budget': budget,
            'expenses': expenses,
            'incomes': incomes
        }
        # Render the home page with the context data
        return render(request, 'home.html', context)
    else:
        # If the user is not authenticated, render the home page without context data
        return render(request, 'home.html')


# Function to handle user registration
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Redirecting to login page after successful registration
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})  # Rendering register.html template with registration form


# Function for user login
def user_login(request):
    # Check if the request method is POST
    if request.method == 'POST':
        # Create an AuthenticationForm instance with POST data
        form = AuthenticationForm(request, request.POST)
        # Check if the form data is valid
        if form.is_valid():
            # Log in the user using the form's user object
            login(request, form.get_user())
            # Redirect the user to the home page after successful login
            return redirect('home')
    else:
        # If the request method is not POST, create an empty AuthenticationForm instance
        form = AuthenticationForm()
    # Render the login page with the form
    return render(request, 'login.html', {'form': form})


# Function for user logout
def user_logout(request):
    logout(request)
    return redirect('home')


# Function to display budget summary
@login_required
def budget_summary(request):
    total_income = Income.objects.filter(user=request.user).aggregate(total_income=Sum('amount'))['total_income'] or 0
    total_expense = Expense.objects.filter(user=request.user).aggregate(total_expense=Sum('amount'))[
                        'total_expense'] or 0
    balance = total_income - total_expense
    return render(request, 'budget_summary.html',
                  {'total_income': total_income, 'total_expense': total_expense, 'balance': balance})


# Function to display list of expenses
@login_required
def expenses_list(request):
    expenses = Expense.objects.filter(user=request.user).order_by('-date')
    return render(request, 'expenses_list.html', {'expenses': expenses})


# Function to add expenses
@login_required
def add_expenses(request):
    # Retrieve expense categories for the current user
    expense_categories = Category.objects.filter(type='expense')

    # Check if the request method is POST
    if request.method == 'POST':
        # Create an ExpenseForm instance with POST data
        form = ExpenseForm(request.POST)
        # Check if the form data is valid
        if form.is_valid():
            # Extract expense details from the form
            amount = form.cleaned_data['amount']
            category = form.cleaned_data['category']
            date = form.cleaned_data['date']
            comment = form.cleaned_data['comment']
            # Create a new Expense object with the extracted data
            expense = Expense.objects.create(user=request.user, category=category, amount=amount, date=date,
                                             comment=comment)
            # Redirect the user to the expenses list page
            return redirect('expenses_list')
    else:
        # If the request method is not POST, create an empty ExpenseForm instance
        form = ExpenseForm()

    # Render the template with the form and expense categories
    return render(request, 'add_expenses.html', {'form': form, 'expense_categories': expense_categories})


# Function to fetch data based on filter
@login_required
def fetch_data(request, model_class, template_name):
    # Get the filter value from the request
    filter = request.GET.get('filter')
    # Get the logged-in user
    user = request.user

    # Check the filter value
    if filter == 'day':
        # If the filter is set to 'day', get today's date
        today = datetime.now().date()
        # Fetch data from the model for the current user on today's date, ordered from the newest
        data = model_class.objects.filter(user=user, date=today).order_by('-date')
    elif filter == 'week':
        # If the filter is set to 'week', calculate the range of the current week
        today = datetime.now().date()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        # Fetch data from the model for the current user within the range of the current week, ordered from the newest
        data = model_class.objects.filter(user=user, date__range=[start_of_week, end_of_week]).order_by('-date')
    elif filter == 'month':
        # If the filter is set to 'month', calculate the range of the current month
        today = datetime.now().date()
        start_of_month = today.replace(day=1)
        end_of_month = start_of_month + timedelta(days=32)
        end_of_month = end_of_month.replace(day=1) - timedelta(days=1)
        # Fetch data from the model for the current user within the range of the current month, ordered from the newest
        data = model_class.objects.filter(user=user, date__range=[start_of_month, end_of_month]).order_by('-date')
    elif filter == 'year':
        # If the filter is set to 'year', calculate the range of the current year
        today = datetime.now().date()
        start_of_year = today.replace(month=1, day=1)
        end_of_year = today.replace(month=12, day=31)
        # Fetch data from the model for the current user within the range of the current year, ordered from the newest
        data = model_class.objects.filter(user=user, date__range=[start_of_year, end_of_year]).order_by('-date')
    else:
        # If no filter is set, fetch all data for the current user
        data = model_class.objects.filter(user=user)

    # Create a context containing the data in the appropriate format
    context = {model_class.__name__.lower() + 's': data}
    # Return a response with the data rendered in the template
    return render(request, template_name, context)


# Function to fetch expenses data
@login_required
def fetch_expenses(request):
    return fetch_data(request, Expense, 'expenses_partial.html')


# Function to display expenses within a period
@login_required
def expenses_period(request):
    # Check if the request method is GET
    if request.method == 'GET':
        # Get the start and end dates from the GET parameters
        start_date_str = request.GET.get('start-date')
        end_date_str = request.GET.get('end-date')

        # If both start and end dates are provided
        if start_date_str and end_date_str:
            # Convert start and end date strings to date objects
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

            # Retrieve expenses within the specified date range for the current user
            expenses = Expense.objects.filter(user=request.user, date__range=[start_date, end_date])

            # Calculate total expenses for each category within the date range
            expense_categories = {}
            for expense in expenses:
                category_name = expense.category.name
                amount = expense.amount
                if category_name in expense_categories:
                    expense_categories[category_name] += amount
                else:
                    expense_categories[category_name] = amount

            # Convert expense amounts to float for rendering
            expense_categories_float = {category: float(amount) for category, amount in expense_categories.items()}

            # Render the template with expense categories and date range
            return render(request, 'expenses_period.html', {'expense_categories': expense_categories_float,
                                                            'start_date': start_date,
                                                            'end_date': end_date})
        else:
            # If start or end dates are missing, render an error message
            return render(request, 'expenses_period.html',
                          {'error_message': 'Please provide both start and end dates.'})
    else:
        # If the request method is not GET, render an error message
        return render(request, 'expenses_period.html', {'error_message': 'HTTP method not supported.'})


# Function to display list of incomes
@login_required
def incomes_list(request):
    incomes = Income.objects.filter(user=request.user).order_by('-date')
    return render(request, 'incomes_list.html', {'incomes': incomes})


# Function to add income
@login_required
def add_income(request):
    if request.method == 'POST':
        form = IncomeForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            category = form.cleaned_data['category']
            date = form.cleaned_data['date']
            comment = form.cleaned_data['comment']
            income = Income.objects.create(user=request.user, category=category, amount=amount, date=date,
                                           comment=comment)
            return redirect('incomes_list')
    else:
        categories = Category.objects.filter(type='income').distinct()
        form = IncomeForm()
    return render(request, 'add_incomes.html', {'form': form, 'income_categories': categories})


# Function to fetch incomes data
@login_required
def fetch_incomes(request):
    return fetch_data(request, Income, 'incomes_partial.html')


# Function to display incomes within a period
@login_required
def incomes_period(request):
    if request.method == 'GET':
        start_date_str = request.GET.get('start-date')
        end_date_str = request.GET.get('end-date')

        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            incomes = Income.objects.filter(user=request.user, date__range=[start_date, end_date])

            income_categories = {}
            for income in incomes:
                category_name = income.category.name
                amount = income.amount
                if category_name in income_categories:
                    income_categories[category_name] += amount
                else:
                    income_categories[category_name] = amount

            income_categories_float = {category: float(amount) for category, amount in income_categories.items()}

            return render(request, 'incomes_period.html', {'income_categories': income_categories_float,
                                                           'start_date': start_date,
                                                           'end_date': end_date})
        else:
            return render(request, 'incomes_period.html', {'error_message': 'Proszę podać daty początkową i końcową.'})
    else:
        return render(request, 'incomes_period.html', {'error_message': 'Metoda HTTP nie jest obsługiwana.'})


# Function to display charts
@login_required
def charts_view(request):
    # Retrieve available years from expense data for the current user
    available_years = Expense.objects.filter(user=request.user).dates('date', 'year')
    # Extract years from available years
    years = [year.year for year in available_years]

    # Initialize an empty list to store monthly data
    monthly_data = []

    # Iterate over each month of the year (1 to 12)
    for month in range(1, 13):
        # Calculate total income for the month
        monthly_income = \
            Income.objects.filter(user=request.user, date__month=month).aggregate(total_income=Sum('amount'))[
                'total_income'] or 0
        # Calculate total expense for the month
        monthly_expense = \
            Expense.objects.filter(user=request.user, date__month=month).aggregate(total_expense=Sum('amount'))[
                'total_expense'] or 0
        # Calculate monthly balance (income - expense)
        monthly_balance = monthly_income - monthly_expense
        # Append monthly income, expense, and balance to the monthly data list
        monthly_data.append({'income': monthly_income, 'expense': monthly_expense, 'balance': monthly_balance})

    # Convert monthly data to JSON format
    data_json = json.dumps(monthly_data, cls=DjangoJSONEncoder)

    # Render the template with monthly data and available years
    return render(request, 'charts.html', {'monthly_data': data_json, 'years': years})


# Function to get data for charts
@login_required
def get_data(request):
    # Get the year from the GET parameters
    year = request.GET.get('year')
    # Initialize an empty list to store monthly data
    monthly_data = []

    # Iterate over each month of the year (1 to 12)
    for month in range(1, 13):
        # Calculate total income for the month
        monthly_income = Income.objects.filter(user=request.user, date__year=year, date__month=month).aggregate(
            total_income=Sum('amount'))['total_income'] or 0
        # Calculate total expense for the month
        monthly_expense = Expense.objects.filter(user=request.user, date__year=year, date__month=month).aggregate(
            total_expense=Sum('amount'))['total_expense'] or 0
        # Calculate monthly balance (income - expense)
        monthly_balance = monthly_income - monthly_expense
        # Append monthly income, expense, and balance to the monthly data list
        monthly_data.append({'income': monthly_income, 'expense': monthly_expense, 'balance': monthly_balance})

    # Return monthly data as a JSON response
    return JsonResponse(monthly_data, safe=False)


# Function to display categories
@login_required
def categories_view(request):
    expense_categories = Category.objects.filter(type='expense')
    income_categories = Category.objects.filter(type='income')
    return render(request, 'categories.html',
                  {'expense_categories': expense_categories, 'income_categories': income_categories})


# Function to add category
@login_required
def add_category_view(request):
    # Check if the request method is POST
    if request.method == 'POST':
        # Create a CategoryForm instance with POST data
        form = CategoryForm(request.POST)
        # Check if the form data is valid
        if form.is_valid():
            # Extract the new category name and type from the form
            new_category = form.cleaned_data['new_category']
            category_type = form.cleaned_data['category_type']
            # Create a new Category object with the extracted data
            category = Category.objects.create(name=new_category, type=category_type)
            # Redirect the user based on the type of category added
            if category.type == 'expense':
                return redirect('categories_expense')
            elif category.type == 'income':
                return redirect('categories_income')
    else:
        # If the request method is not POST, create an empty CategoryForm instance
        form = CategoryForm()
    # Render the template with the form
    return render(request, {'form': form})


# Function to display expense categories
@login_required
def categories_expense(request):
    expense_categories = Category.objects.filter(type='expense')
    return render(request, 'categories_expense.html', {'expense_categories': expense_categories})


# Function to display income categories
@login_required
def categories_income(request):
    income_categories = Category.objects.filter(type='income')
    return render(request, 'categories_income.html', {'income_categories': income_categories})


# Function to delete category
@login_required
def delete_category(request, category_id):
    if request.method == 'POST':
        category = Category.objects.get(id=category_id)
        category.delete()
    return redirect('categories')


# Function to display report page
def report_view(request):
    return render(request, 'report.html')


# Function to generate CSV report
@login_required
def generate_csv_report(request):
    # Retrieve income and expense data for the current user
    incomes = Income.objects.filter(user=request.user)
    expenses = Expense.objects.filter(user=request.user)

    # Generate a filename with current timestamp for the CSV report
    filename = f"Report_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"

    # Create an HTTP response object with content type of text/csv
    response = HttpResponse(content_type='text/csv')
    # Set the content disposition to make the CSV an attachment with the generated filename
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    # Create a CSV writer object
    writer = csv.writer(response)

    # Write the header row for the CSV
    writer.writerow(["Section", "Date", "Category", "Amount", "Comment"])

    # Write income data rows to the CSV
    for income in incomes:
        writer.writerow(
            ["Income", income.date.strftime("%Y-%m-%d"), income.category.name, income.amount, income.comment])

    # Write expense data rows to the CSV
    for expense in expenses:
        writer.writerow(
            ["Expense", expense.date.strftime("%Y-%m-%d"), expense.category.name, expense.amount, expense.comment])

    # Return the HTTP response with the CSV content
    return response


# Function to generate PDF report
@login_required
def generate_pdf_report(request):
    # Create a response object with PDF content type
    response = HttpResponse(content_type='application/pdf')
    # Set the content disposition to attachment with a filename
    response['Content-Disposition'] = 'attachment; filename="Report.pdf"'
    # Create a SimpleDocTemplate object for PDF generation with letter-sized pages
    doc = SimpleDocTemplate(response, pagesize=letter)

    # Get the default styles for PDF elements
    styles = getSampleStyleSheet()
    style_normal = styles['Normal']

    # Retrieve income and expense data for the current user
    incomes = Income.objects.filter(user=request.user)
    expenses = Expense.objects.filter(user=request.user)

    # Initialize data with headers
    data = [['Type', 'Date', 'Category', 'Amount', 'Comment']]

    # Add income data to the table
    for income in incomes:
        data.append(['Income', income.date.strftime("%Y-%m-%d"), income.category.name, income.amount, income.comment])

    # Add expense data to the table
    for expense in expenses:
        data.append(
            ['Expense', expense.date.strftime("%Y-%m-%d"), expense.category.name, expense.amount, expense.comment])

    # Create a Table object with data
    table = Table(data)

    # Define styles for the table
    style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)])

    # Apply styles to the table
    table.setStyle(style)

    # Add the table to the elements to be included in the PDF
    elements = [table]

    # Generate the PDF document with provided elements
    doc.build(elements)

    # Return the response with the PDF content
    return response


# Function to display ATMs view
def atms_view(request):
    return render(request, 'atms.html')
