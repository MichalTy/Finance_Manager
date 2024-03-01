"""
URL configuration for budget project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from budget_app import views


urlpatterns = [
    path('', views.home, name='home'),
    path('budget_summary/', views.budget_summary, name='budget_summary'),
    path('expenses_list/', views.expenses_list, name='expenses_list'),
    path('add_expenses/', views.add_expenses, name='add_expenses'),
    path('fetch_expenses/', views.fetch_expenses, name='fetch_expenses'),
    path('expenses_period/', views.expenses_period, name='expenses_period'),
    path('incomes_list/', views.incomes_list, name='incomes_list'),
    path('add_income/', views.add_income, name='add_income'),
    path('fetch_incomes/', views.fetch_incomes, name='fetch_incomes'),
    path('incomes_period/', views.incomes_period, name='incomes_period'),
    path('login/', views.user_login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.user_logout, name='logout'),
    path('charts/', views.charts_view, name='charts'),
    path('data', views.get_data, name='get_data'),
    path('categories/', views.categories_view, name='categories'),
    path('add_category/', views.add_category_view, name='add_category'),
    path('categories/expense/', views.categories_expense, name='categories_expense'),
    path('categories/income/', views.categories_income, name='categories_income'),
    path('delete_category/<int:category_id>/', views.delete_category, name='delete_category'),
    path('report/', views.report_view, name='report'),
    path('generate_csv_report/', views.generate_csv_report, name='generate_csv_report'),
    path('generate_pdf_report/', views.generate_pdf_report, name='generate_pdf_report'),
    path('atms/', views.atms_view, name='atms'),
]
