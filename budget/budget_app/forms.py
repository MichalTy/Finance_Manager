from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import Expense, Income


class RegistrationForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['category', 'amount', 'date', 'comment']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ExpenseForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['category'].queryset = self.fields['category'].queryset.filter(expense__isnull=False,
                                                                                       user=user).distinct()


class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = ['category', 'amount', 'date', 'comment']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(IncomeForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['category'].queryset = self.fields['category'].queryset.filter(income__isnull=False,
                                                                                       user=user).distinct()


class CategoryForm(forms.Form):
    new_category = forms.CharField(label='Nowa kategoria', max_length=100)
    category_type = forms.ChoiceField(label='Typ', choices=(('expense', 'Wydatek'), ('income', 'Dochód')))
