from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms

from .models import Expense, Income


class RegistrationForm(UserCreationForm):
    email = forms.EmailField()  # Adds an email field to the registration form

    class Meta:
        model = User  # Specifies the User model
        fields = ['username', 'email', 'password1', 'password2']  # Fields to be displayed in the form


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense  # Specifies the Expense model
        fields = ['category', 'amount', 'date', 'comment']  # Fields to be displayed in the form
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),  # Configures the date field to use a date picker
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Retrieves the 'user' parameter from kwargs
        super(ExpenseForm, self).__init__(*args, **kwargs)  # Calls the parent class constructor
        if user:
            # Filters the category choices based on the user's expenses and removes duplicates
            self.fields['category'].queryset = self.fields['category'].queryset.filter(expense__isnull=False,
                                                                                       user=user).distinct()


class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income  # Specifies the Income model
        fields = ['category', 'amount', 'date', 'comment']  # Fields to be displayed in the form
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),  # Configures the date field to use a date picker
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Retrieves the 'user' parameter from kwargs
        super(IncomeForm, self).__init__(*args, **kwargs)  # Calls the parent class constructor
        if user:
            # Filters the category choices based on the user's incomes and removes duplicates
            self.fields['category'].queryset = self.fields['category'].queryset.filter(income__isnull=False,
                                                                                       user=user).distinct()


class CategoryForm(forms.Form):
    new_category = forms.CharField(label='Nowa kategoria', max_length=100)  # Adds a text field for a new category
    category_type = forms.ChoiceField(label='Typ', choices=(('expense', 'Wydatek'), ('income', 'Dochód')))
    # Adds a dropdown for selecting the type of category: expense or income

