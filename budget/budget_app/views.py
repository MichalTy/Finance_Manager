import csv
import json

from django.core.serializers.json import DjangoJSONEncoder

from datetime import datetime, timedelta

from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from django.db.models import Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

from .forms import CategoryForm, ExpenseForm, IncomeForm
from .models import Budget, Category, Expense, Income


def home(request):
    if request.user.is_authenticated:
        budget = Budget.objects.filter(user=request.user).first()
        expenses = Expense.objects.filter(user=request.user)
        incomes = Income.objects.filter(user=request.user)
        context = {
            'budget': budget,
            'expenses': expenses,
            'incomes': incomes
        }
        return render(request, 'home.html', context)
    else:
        return render(request, 'home.html')


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('home')


@login_required
def budget_summary(request):
    total_income = Income.objects.filter(user=request.user).aggregate(total_income=Sum('amount'))['total_income'] or 0
    total_expense = Expense.objects.filter(user=request.user).aggregate(total_expense=Sum('amount'))[
                        'total_expense'] or 0
    balance = total_income - total_expense
    return render(request, 'budget_summary.html',
                  {'total_income': total_income, 'total_expense': total_expense, 'balance': balance})


@login_required
def expenses_list(request):
    expenses = Expense.objects.filter(user=request.user).order_by('-date')
    return render(request, 'expenses_list.html', {'expenses': expenses})


@login_required
def add_expenses(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            category = form.cleaned_data['category']
            date = form.cleaned_data['date']
            comment = form.cleaned_data['comment']
            expense = Expense.objects.create(user=request.user, category=category, amount=amount, date=date,
                                             comment=comment)
            return redirect('expenses_list')
    else:
        form = ExpenseForm()
        expense_categories = Category.objects.filter(type='expense')
    return render(request, 'add_expenses.html', {'form': form, 'expense_categories': expense_categories})


def fetch_expenses(request):
    filter = request.GET.get('filter')
    user = request.user

    if filter == 'day':
        today = datetime.now().date()
        expenses = Expense.objects.filter(user=user, date=today).order_by('-date')
    elif filter == 'week':
        today = datetime.now().date()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        expenses = Expense.objects.filter(user=user, date__range=[start_of_week, end_of_week]).order_by('-date')
    elif filter == 'month':
        today = datetime.now().date()
        start_of_month = today.replace(day=1)
        end_of_month = start_of_month + timedelta(days=32)
        end_of_month = end_of_month.replace(day=1) - timedelta(days=1)
        expenses = Expense.objects.filter(user=user, date__range=[start_of_month, end_of_month]).order_by('-date')
    elif filter == 'year':
        today = datetime.now().date()
        start_of_year = today.replace(month=1, day=1)
        end_of_year = today.replace(month=12, day=31)
        expenses = Expense.objects.filter(user=user, date__range=[start_of_year, end_of_year]).order_by('-date')
    else:
        expenses = Expense.objects.filter(user=user)

    return render(request, 'expenses_partial.html', {'expenses': expenses})


def expenses_period(request):
    if request.method == 'GET':
        start_date_str = request.GET.get('start-date')
        end_date_str = request.GET.get('end-date')

        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            expenses = Expense.objects.filter(user=request.user, date__range=[start_date, end_date])

            expense_categories = {}
            for expense in expenses:
                category_name = expense.category.name
                amount = expense.amount
                if category_name in expense_categories:
                    expense_categories[category_name] += amount
                else:
                    expense_categories[category_name] = amount

            expense_categories_float = {category: float(amount) for category, amount in expense_categories.items()}

            return render(request, 'expenses_period.html', {'expense_categories': expense_categories_float,
                                                            'start_date': start_date,
                                                            'end_date': end_date})
        else:
            return render(request, 'expenses_period.html', {'error_message': 'Proszę podać daty początkową i końcową.'})
    else:
        return render(request, 'expenses_period.html', {'error_message': 'Metoda HTTP nie jest obsługiwana.'})


@login_required
def incomes_list(request):
    incomes = Income.objects.filter(user=request.user).order_by('-date')
    return render(request, 'incomes_list.html', {'incomes': incomes})


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


def fetch_incomes(request):
    filter = request.GET.get('filter')
    user = request.user

    if filter == 'day':
        today = datetime.now().date()
        incomes = Income.objects.filter(user=user, date=today).order_by('-date')
    elif filter == 'week':
        today = datetime.now().date()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        incomes = Income.objects.filter(user=user, date__range=[start_of_week, end_of_week]).order_by('-date')
    elif filter == 'month':
        today = datetime.now().date()
        start_of_month = today.replace(day=1)
        end_of_month = start_of_month + timedelta(days=32)
        end_of_month = end_of_month.replace(day=1) - timedelta(days=1)
        incomes = Income.objects.filter(user=user, date__range=[start_of_month, end_of_month]).order_by('-date')
    elif filter == 'year':
        today = datetime.now().date()
        start_of_year = today.replace(month=1, day=1)
        end_of_year = today.replace(month=12, day=31)
        incomes = Income.objects.filter(user=user, date__range=[start_of_year, end_of_year]).order_by('-date')
    else:
        incomes = Income.objects.filter(user=user)

    return render(request, 'incomes_partial.html', {'incomes': incomes})


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


def charts_view(request):
    available_years = Expense.objects.filter(user=request.user).dates('date', 'year')
    years = [year.year for year in available_years]

    monthly_data = []
    for month in range(1, 13):
        monthly_income = \
            Income.objects.filter(user=request.user, date__month=month).aggregate(total_income=Sum('amount'))[
                'total_income'] or 0
        monthly_expense = \
            Expense.objects.filter(user=request.user, date__month=month).aggregate(total_expense=Sum('amount'))[
                'total_expense'] or 0
        monthly_balance = monthly_income - monthly_expense
        monthly_data.append({'income': monthly_income, 'expense': monthly_expense, 'balance': monthly_balance})

    data_json = json.dumps(monthly_data, cls=DjangoJSONEncoder)

    return render(request, 'charts.html', {'monthly_data': data_json, 'years': years})


def get_data(request):
    year = request.GET.get('year')
    monthly_data = []

    for month in range(1, 13):
        monthly_income = Income.objects.filter(user=request.user, date__year=year, date__month=month).aggregate(
            total_income=Sum('amount'))['total_income'] or 0
        monthly_expense = Expense.objects.filter(user=request.user, date__year=year, date__month=month).aggregate(
            total_expense=Sum('amount'))['total_expense'] or 0
        monthly_balance = monthly_income - monthly_expense
        monthly_data.append({'income': monthly_income, 'expense': monthly_expense, 'balance': monthly_balance})

    return JsonResponse(monthly_data, safe=False)


def categories_view(request):
    expense_categories = Category.objects.filter(type='expense')
    income_categories = Category.objects.filter(type='income')
    return render(request, 'categories.html',
                  {'expense_categories': expense_categories, 'income_categories': income_categories})


def add_category_view(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            new_category = form.cleaned_data['new_category']
            category_type = form.cleaned_data['category_type']
            category = Category.objects.create(name=new_category, type=category_type)
            if category.type == 'expense':
                return redirect('categories_expense')
            elif category.type == 'income':
                return redirect('categories_income')
    else:
        form = CategoryForm()
    return render(request, 'add_category.html', {'form': form})


@login_required
def categories_expense(request):
    expense_categories = Category.objects.filter(type='expense')
    return render(request, 'categories_expense.html', {'expense_categories': expense_categories})


@login_required
def categories_income(request):
    income_categories = Category.objects.filter(type='income')
    return render(request, 'categories_income.html', {'income_categories': income_categories})


@login_required
def delete_category(request, category_id):
    if request.method == 'POST':
        category = Category.objects.get(id=category_id)
        category.delete()
    return redirect('categories')


def report_view(request):
    return render(request, 'report.html')


def generate_csv_report(request):
    incomes = Income.objects.filter(user=request.user)
    expenses = Expense.objects.filter(user=request.user)

    filename = f"Raport_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)

    writer.writerow(["Sekcja", "Data", "Kategoria", "Kwota", "Komentarz"])

    for income in incomes:
        writer.writerow(
            ["Przychody", income.date.strftime("%Y-%m-%d"), income.category.name, income.amount, income.comment])

    for expense in expenses:
        writer.writerow(
            ["Wydatki", expense.date.strftime("%Y-%m-%d"), expense.category.name, expense.amount, expense.comment])

    return response


def generate_pdf_report(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Raport.pdf"'
    doc = SimpleDocTemplate(response, pagesize=letter)

    styles = getSampleStyleSheet()
    style_normal = styles['Normal']

    incomes = Income.objects.filter(user=request.user)
    expenses = Expense.objects.filter(user=request.user)

    data = [['Typ', 'Data', 'Kategoria', 'Kwota', 'Komentarz']]

    for income in incomes:
        data.append(['Dochód', income.date.strftime("%Y-%m-%d"), income.category.name, income.amount, income.comment])

    for expense in expenses:
        data.append(
            ['Wydatek', expense.date.strftime("%Y-%m-%d"), expense.category.name, expense.amount, expense.comment])

    table = Table(data)
    style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)])

    table.setStyle(style)

    elements = [table]
    doc.build(elements)

    return response


def atms_view(request):
    return render(request, 'atms.html')
