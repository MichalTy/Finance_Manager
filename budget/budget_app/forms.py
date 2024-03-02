from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms

from .models import Expense, Income


class RegistrationForm(UserCreationForm):
    '''
    Registration form with additional email field.
    '''
    email = forms.EmailField()

    class Meta:
        '''
        Meta class specifying the User model and fields.
        '''
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class ExpenseForm(forms.ModelForm):
    '''
    Form for adding expenses.
    '''
    class Meta:
        '''
        Meta class specifying the Expense model and fields.
        '''
        model = Expense  # Specifies the Expense model
        fields = ['category', 'amount', 'date', 'comment']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        '''
        Constructor method for ExpenseForm.
        '''
        user = kwargs.pop('user', None)
        super(ExpenseForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['category'].queryset = self.fields['category'].queryset.filter(expense__isnull=False,
                                                                                       user=user).distinct()


class IncomeForm(forms.ModelForm):
    '''
    Form for adding incomes.
    '''
    class Meta:
        '''
        Meta class specifying the Income model and fields.
        '''
        model = Income
        fields = ['category', 'amount', 'date', 'comment']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        '''
        Constructor method for IncomeForm.
        '''
        user = kwargs.pop('user', None)
        super(IncomeForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['category'].queryset = self.fields['category'].queryset.filter(income__isnull=False,
                                                                                       user=user).distinct()


class CategoryForm(forms.Form):
    '''
    Form for adding categories.
    '''
    new_category = forms.CharField(label='Nowa kategoria', max_length=100)
    category_type = forms.ChoiceField(label='Typ', choices=(('expense', 'Wydatek'), ('income', 'Dochód')))

