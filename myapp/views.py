from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordChangeForm
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from .models import Profile
from .forms import ProfileForm , CategoryForm

def user_register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')   
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import Income, Expense, Budget, Category

@login_required
def dashboard(request):
    # Get total income for the logged-in user
    total_income = Income.objects.filter(user=request.user).aggregate(total_income=Sum('amount'))['total_income'] or 0

    # Get total expenses for the logged-in user
    total_expenses = Expense.objects.filter(user=request.user).aggregate(total_expense=Sum('amount'))['total_expense'] or 0

    # Calculate savings as income - expenses
    total_savings = total_income - total_expenses

    # Prepare data for category-wise distribution (Pie chart)
    categories = Category.objects.all()
    for category in categories:
        category.total_expenses = Expense.objects.filter(
            user=request.user,
            category=category
        ).aggregate(total_expense=Sum('amount'))['total_expense'] or 0

    # Prepare data for month-on-month spending (Bar chart)
    months = Expense.objects.filter(user=request.user).values('date__month').annotate(
        spending=Sum('amount')
    ).order_by('date__month')

    # Get all budgets to check budget status
    budgets = Budget.objects.filter(user=request.user)

    # Prepare alerts for exceeded or nearing budget limits
    alerts = []
    for budget in budgets:
        total_spent = sum(expense.amount for expense in budget.get_expenses())
        remaining_budget = budget.amount - total_spent
        if remaining_budget < 0:
            alerts.append(f"Budget for {budget.category.name} exceeded!")
        elif remaining_budget < budget.amount * 0.1:
            alerts.append(f"Warning: You're nearing the budget for {budget.category.name}.")

    return render(request, 'dashboard.html', {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'total_savings': total_savings,
        'alerts': alerts,
        'categories': categories,
        'months': months
    })


@login_required
def update_profile(request):
    user = request.user
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        profile = Profile(user=user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'update_profile.html', {'form': form})

@login_required
def view_profile(request):
    user_profile = Profile.objects.get(user=request.user)
    return render(request, 'view_profile.html', {'user_profile': user_profile})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change_password.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('user_login')


from .models import Category

@login_required
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added successfully.')
            return redirect('view_categories')
    else:
        form = CategoryForm()

    return render(request, 'add_category.html', {'form': form})


@login_required
def view_categories(request):
    categories = Category.objects.all()
    return render(request, 'view_categories.html', {'categories': categories})


@login_required
def edit_category(request, category_id):
    category = get_object_or_404(Category, category_id=category_id)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully.')
            return redirect('view_categories')
    else:
        form = CategoryForm(instance=category)

    return render(request, 'edit_category.html', {'form': form, 'category': category})


@login_required
def delete_category(request, category_id):
    category = get_object_or_404(Category, category_id=category_id)
    category.delete()
    messages.success(request, 'Category deleted successfully.')
    return redirect('view_categories')

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import IncomeForm
from .models import Income

@login_required
def add_income(request):
    if request.method == 'POST':
        form = IncomeForm(request.POST)
        if form.is_valid():
            income = form.save(commit=False)
            income.user = request.user  # Set the user to the logged-in user
            income.save()
            messages.success(request, 'Income added successfully.')
            return redirect('view_income')
    else:
        form = IncomeForm()

    return render(request, 'add_income.html', {'form': form})
 
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import Income
import csv
from datetime import datetime

@login_required
def view_income(request):
    # Filtering logic based on the request parameters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    min_amount = request.GET.get('min_amount')
    max_amount = request.GET.get('max_amount')
    source = request.GET.get('source')  # New filter for source

    incomes = Income.objects.filter(user=request.user)

    if start_date:
        incomes = incomes.filter(date__gte=start_date)
    if end_date:
        incomes = incomes.filter(date__lte=end_date)
    if min_amount:
        incomes = incomes.filter(amount__gte=min_amount)
    if max_amount:
        incomes = incomes.filter(amount__lte=max_amount)
    if source:
        incomes = incomes.filter(source__icontains=source)  # Case-insensitive search for source

    # Sort the incomes by date (newest first)
    incomes = incomes.order_by('-date')

    return render(request, 'view_income.html', {'incomes': incomes})

@login_required
def export_income_csv(request):
    # Get the filtered data based on the same filters as in the view
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    min_amount = request.GET.get('min_amount')
    max_amount = request.GET.get('max_amount')
    source = request.GET.get('source')  # New filter for source

    incomes = Income.objects.filter(user=request.user)

    if start_date:
        incomes = incomes.filter(date__gte=start_date)
    if end_date:
        incomes = incomes.filter(date__lte=end_date)
    if min_amount:
        incomes = incomes.filter(amount__gte=min_amount)
    if max_amount:
        incomes = incomes.filter(amount__lte=max_amount)
    if source:
        incomes = incomes.filter(source__icontains=source)  # Case-insensitive search for source

    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="income_data.csv"'

    writer = csv.writer(response)
    writer.writerow(['Date', 'Source', 'Amount', 'Note'])

    for income in incomes:
        writer.writerow([income.date, income.source, income.amount, income.note])

    return response


@login_required
def edit_income(request, income_id):
    income = get_object_or_404(Income, income_id=income_id, user=request.user)
    if request.method == 'POST':
        form = IncomeForm(request.POST, instance=income)
        if form.is_valid():
            form.save()
            messages.success(request, 'Income updated successfully.')
            return redirect('view_income')
    else:
        form = IncomeForm(instance=income)

    return render(request, 'edit_income.html', {'form': form, 'income': income})

@login_required
def delete_income(request, income_id):
    income = get_object_or_404(Income, income_id=income_id, user=request.user)
    income.delete()
    messages.success(request, 'Income deleted successfully.')
    return redirect('view_income')


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ExpenseForm
from .models import Expense, Category

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ExpenseForm
from .models import Expense, Budget

from decimal import Decimal
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ExpenseForm
from .models import Budget

@login_required
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user  # Set user to the logged-in user

            # Check if the expense exceeds the budget
            budget = Budget.objects.filter(user=request.user, category=expense.category, month=expense.date.month, year=expense.date.year).first()
            
            if budget:
                total_expenses = sum(exp.amount for exp in budget.get_expenses()) + expense.amount
                
                # Convert 0.9 to a Decimal to ensure compatibility with budget.amount (which is Decimal)
                if total_expenses > budget.amount:
                    # Notify the user about the exceeded budget
                    messages.warning(request, f"You are exceeding your budget for {budget.category.name}!")
                    expense.save()
                    return redirect('view_expense')  # After warning, return to the expense view page
                
                # Compare total expenses against 90% of the budget
                elif total_expenses > budget.amount * Decimal('0.9'):  # Convert 0.9 to Decimal
                    # Alert user if the expenses are nearing the budget limit (90%)
                    messages.warning(request, f"You are nearing your budget for {budget.category.name}.")
            
            expense.save()  # Save the expense after checking
            messages.success(request, 'Expense added successfully.')
            return redirect('view_expense')

    else:
        form = ExpenseForm()

    return render(request, 'add_expense.html', {'form': form})



from decimal import Decimal

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import Expense, Budget
from django.db.models import Sum
from django.contrib import messages
import csv
from datetime import datetime
from decimal import Decimal

@login_required
def view_expense(request):
    # Filtering logic based on the request parameters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    min_amount = request.GET.get('min_amount')
    max_amount = request.GET.get('max_amount')
    category = request.GET.get('category')  # New filter for category

    expenses = Expense.objects.filter(user=request.user)

    if start_date:
        expenses = expenses.filter(date__gte=start_date)
    if end_date:
        expenses = expenses.filter(date__lte=end_date)
    if min_amount:
        expenses = expenses.filter(amount__gte=min_amount)
    if max_amount:
        expenses = expenses.filter(amount__lte=max_amount)
    if category:
        expenses = expenses.filter(category__name__icontains=category)  # Filter by category name

    # Sorting by date (oldest first)
    expenses = expenses.order_by('date')

    # Check if the expenses exceed the budget
    for expense in expenses:
        budget = Budget.objects.filter(user=request.user, category=expense.category, month=expense.date.month, year=expense.date.year).first()
        if budget:
            total_expenses = sum(exp.amount for exp in budget.get_expenses()) + expense.amount
            if total_expenses > budget.amount:
                messages.warning(request, f"You are exceeding your budget for {budget.category.name}.")
            elif total_expenses > budget.amount * Decimal('0.9'):  # Warning if 90% of budget is spent
                messages.warning(request, f"You are nearing your budget for {budget.category.name}.")

    return render(request, 'view_expense.html', {'expenses': expenses})

@login_required
def export_expense_csv(request):
    # Get the filtered data based on the same filters as in the view
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    min_amount = request.GET.get('min_amount')
    max_amount = request.GET.get('max_amount')
    category = request.GET.get('category')  # New filter for category

    expenses = Expense.objects.filter(user=request.user)

    if start_date:
        expenses = expenses.filter(date__gte=start_date)
    if end_date:
        expenses = expenses.filter(date__lte=end_date)
    if min_amount:
        expenses = expenses.filter(amount__gte=min_amount)
    if max_amount:
        expenses = expenses.filter(amount__lte=max_amount)
    if category:
        expenses = expenses.filter(category__name__icontains=category)  # Filter by category name

    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="expense_data.csv"'

    writer = csv.writer(response)
    writer.writerow(['Date', 'Category', 'Amount', 'Note'])

    for expense in expenses:
        writer.writerow([expense.date, expense.category.name, expense.amount, expense.note])

    return response

@login_required
def edit_expense(request, expense_id):
    expense = get_object_or_404(Expense, expense_id=expense_id, user=request.user)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            messages.success(request, 'Expense updated successfully.')
            return redirect('view_expense')
    else:
        form = ExpenseForm(instance=expense)

    return render(request, 'edit_expense.html', {'form': form, 'expense': expense})

@login_required
def delete_expense(request, expense_id):
    expense = get_object_or_404(Expense, expense_id=expense_id, user=request.user)
    expense.delete()
    messages.success(request, 'Expense deleted successfully.')
    return redirect('view_expense')


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import BudgetForm
from .models import Budget, Category

@login_required
def add_budget(request):
    if request.method == 'POST':
        form = BudgetForm(request.POST)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user  # Assign the logged-in user
            budget.save()
            messages.success(request, 'Budget added successfully.')
            return redirect('view_budget')
    else:
        form = BudgetForm()

    return render(request, 'add_budget.html', {'form': form})

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Budget, Expense
from django.db.models import Sum

@login_required
def view_budget(request):
    # Get all budgets for the logged-in user
    budgets = Budget.objects.filter(user=request.user).order_by('year', 'month', 'category__name')
    
    # Loop through each budget and calculate remaining budget and status
    for budget in budgets:
        # Get total expenses for this category, month, and year
        total_expenses = Expense.objects.filter(
            user=request.user, 
            category=budget.category, 
            date__month=budget.month, 
            date__year=budget.year
        ).aggregate(total_expense=Sum('amount'))['total_expense']
        
        # If total_expenses is None (i.e., no expenses found), set it to 0
        if total_expenses is None:
            total_expenses = 0

        # Calculate the remaining budget
        remaining_budget = budget.amount - total_expenses
        
        # Set the budget status
        if remaining_budget < 0:
            budget.remaining_budget = 'Exceeded'
        elif remaining_budget <= budget.amount * 0.1:
            budget.remaining_budget = 'Warning'  # Nearing budget limit (10%)
        else:
            budget.remaining_budget = 'Safe'  # Within the budget
        
        # Store the remaining budget for display
        budget.remaining_budget_value = remaining_budget

    # Pass the budgets with the calculated status to the template
    return render(request, 'view_budget.html', {'budgets': budgets})


@login_required
def edit_budget(request, budget_id):
    budget = get_object_or_404(Budget, budget_id=budget_id, user=request.user)
    if request.method == 'POST':
        form = BudgetForm(request.POST, instance=budget)
        if form.is_valid():
            form.save()
            messages.success(request, 'Budget updated successfully.')
            return redirect('view_budget')
    else:
        form = BudgetForm(instance=budget)

    return render(request, 'edit_budget.html', {'form': form, 'budget': budget})

@login_required
def delete_budget(request, budget_id):
    budget = get_object_or_404(Budget, budget_id=budget_id, user=request.user)
    budget.delete()
    messages.success(request, 'Budget deleted successfully.')
    return redirect('view_budget')
