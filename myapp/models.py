
from django.db import models
from django.contrib.auth.models import User
from django.core import validators

class Profile(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100, default="")
    email = models.EmailField(default="")
    date_of_birth = models.DateField(default=None, blank=True, null=True)
    age = models.IntegerField(default=None, blank=True, null=True, validators=[validators.MinValueValidator(0)])
    phone_number = models.CharField(
        max_length=20,
        default="",
        blank=True,
        null=True,
        validators=[validators.RegexValidator(regex='^[0-9]*$', message='Enter a valid phone number.', code='invalid_number')]
    )  # Only allow numeric values
    address = models.TextField(default="", blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', default='default.jpg')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    
    def __str__(self):
        return self.user.username

class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name
    

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Income(models.Model):
    income_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    source = models.CharField(max_length=255)
    date = models.DateTimeField(default=timezone.now)
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.source} - {self.amount} ({self.date.strftime('%Y-%m-%d')})"


from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Expense(models.Model):
    expense_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.category.name} - {self.amount} ({self.date.strftime('%Y-%m-%d')})"

from django.db import models
from django.contrib.auth.models import User

class Budget(models.Model):
    budget_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    month = models.IntegerField(choices=[(i, str(i)) for i in range(1, 13)], default=1)
    year = models.IntegerField()

    def __str__(self):
        return f"Budget for {self.category.name} - {self.amount} ({self.month}/{self.year})"

    def get_expenses(self):
        """
        Get all expenses for the given budget for the current month/year.
        """
        from .models import Expense
        return Expense.objects.filter(user=self.user, category=self.category, date__year=self.year, date__month=self.month)

    def remaining_budget(self):
        """
        Returns the remaining budget after subtracting expenses for the current month and year.
        """
        total_expenses = sum(expense.amount for expense in self.get_expenses())
        remaining = self.amount - total_expenses

        if remaining < 0:
            return 'Exceeded'
        elif remaining < 0.1 * self.amount:
            return 'Warning'  # 90% of the budget
        else:
            return 'Safe'
