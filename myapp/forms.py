from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile

class RegistrationForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']



from django import forms
from .models import Profile

class ProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
            
    class Meta:
        model = Profile
        fields = ['full_name', 'email', 'age','date_of_birth', 'gender', 'phone_number', 'address', 'profile_picture']


from django import forms
from .models import Category

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter category name'}),
        }

from django import forms
from .models import Income

class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = ['amount', 'source', 'date', 'note']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'source': forms.TextInput(attrs={'class': 'form-control'}),
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

from django import forms
from .models import Expense, Category

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['amount', 'category', 'date', 'note']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

from django import forms
from .models import Budget, Category

class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['category', 'amount', 'month', 'year']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'month': forms.Select(choices=[(i, str(i)) for i in range(1, 13)], attrs={'class': 'form-control'}),
            'year': forms.NumberInput(attrs={'class': 'form-control', 'min': 2020}),
        }
