from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q
from .models import Transaction, Status, TransactionType, Category, Subcategory
from .forms import TransactionForm, StatusForm, TransactionTypeForm, CategoryForm, SubcategoryForm
from django.contrib import messages

def transaction_list(request):
    transactions = Transaction.objects.all()
    
    # Фильтрация
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    status_id = request.GET.get('status')
    transaction_type_id = request.GET.get('transaction_type')
    category_id = request.GET.get('category')
    subcategory_id = request.GET.get('subcategory')
    
    if date_from:
        transactions = transactions.filter(date__gte=date_from)
    if date_to:
        transactions = transactions.filter(date__lte=date_to)
    if status_id:
        transactions = transactions.filter(status_id=status_id)
    if transaction_type_id:
        transactions = transactions.filter(transaction_type_id=transaction_type_id)
    if category_id:
        transactions = transactions.filter(category_id=category_id)
    if subcategory_id:
        transactions = transactions.filter(subcategory_id=subcategory_id)
    
    context = {
        'transactions': transactions,
        'statuses': Status.objects.all(),
        'transaction_types': TransactionType.objects.all(),
        'categories': Category.objects.all(),
        'subcategories': Subcategory.objects.all(),
        'filters': {
            'date_from': date_from,
            'date_to': date_to,
            'status': status_id,
            'transaction_type': transaction_type_id,
            'category': category_id,
            'subcategory': subcategory_id,
        }
    }
    return render(request, 'dds_app/transaction_list.html', context)

def transaction_create(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Транзакция успешно создана!')
            return redirect('transaction_list')
    else:
        form = TransactionForm()
    
    context = {
        'form': form,
        'title': 'Создание транзакции'
    }
    return render(request, 'dds_app/transaction_form.html', context)

# Редактирование транзакций
def transaction_edit(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    
    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            form.save()
            messages.success(request, 'Транзакция успешно обновлена!')
            return redirect('transaction_list')
    else:
        form = TransactionForm(instance=transaction)
        form.fields['transaction_type'].initial = transaction.transaction_type
        form.fields['category'].initial = transaction.category
        form.fields['subcategory'].initial = transaction.subcategory
    
    context = {
        'form': form,
        'title': 'Редактирование транзакции',
        'transaction': transaction
    }
    return render(request, 'dds_app/transaction_form.html', context)

# Удаление транзакций
def transaction_delete(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    
    if request.method == 'POST':
        transaction.delete()
        messages.success(request, 'Транзакция успешно удалена!')
        return redirect('transaction_list')
    
    context = {
        'transaction': transaction
    }
    return render(request, 'dds_app/transaction_confirm_delete.html', context)

# Справочники
def dictionaries(request):
    statuses = Status.objects.all().order_by('name')
    transaction_types = TransactionType.objects.all().order_by('name')
    categories = Category.objects.all().order_by('transaction_type__name', 'name')
    subcategories = Subcategory.objects.all().order_by('category__name', 'name')
    
    context = {
        'statuses': statuses,
        'transaction_types': transaction_types,
        'categories': categories,
        'subcategories': subcategories,
    }
    return render(request, 'dds_app/dictionaries.html', context)

# Создание элемента в справочнике
def add_dictionary_item(request, model_name):
    models = {
        'status': (Status, StatusForm),
        'transaction_type': (TransactionType, TransactionTypeForm),
        'category': (Category, CategoryForm),
        'subcategory': (Subcategory, SubcategoryForm),
    }
    
    if model_name not in models:
        return redirect('dictionaries')
    
    model, form_class = models[model_name]
    
    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'{model._meta.verbose_name} успешно добавлен!')
            return redirect('dictionaries')
    else:
        form = form_class()
    
    context = {
        'form': form,
        'model_name': model_name,
        'verbose_name': model._meta.verbose_name
    }
    return render(request, 'dds_app/dictionary_form.html', context)

# Редактирование элемента в справочнике
def edit_dictionary_item(request, model_name, pk):
    models = {
        'status': (Status, StatusForm),
        'transaction_type': (TransactionType, TransactionTypeForm),
        'category': (Category, CategoryForm),
        'subcategory': (Subcategory, SubcategoryForm),
    }
    
    if model_name not in models:
        return redirect('dictionaries')
    
    model, form_class = models[model_name]
    item = get_object_or_404(model, pk=pk)
    
    if request.method == 'POST':
        form = form_class(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, f'{model._meta.verbose_name} успешно обновлен!')
            return redirect('dictionaries')
    else:
        form = form_class(instance=item)
    
    context = {
        'form': form,
        'model_name': model_name,
        'verbose_name': model._meta.verbose_name,
        'item': item
    }
    return render(request, 'dds_app/dictionary_form.html', context)

# Удаление элемента в справочнике
def delete_dictionary_item(request, model_name, pk):
    models = {
        'status': Status,
        'transaction_type': TransactionType,
        'category': Category,
        'subcategory': Subcategory,
    }
    
    if model_name not in models:
        return redirect('dictionaries')
    
    model = models[model_name]
    item = get_object_or_404(model, pk=pk)
    
    if request.method == 'POST':
        item.delete()
        messages.success(request, f'{model._meta.verbose_name} успешно удален!')
        return redirect('dictionaries')
    
    context = {
        'item': item,
        'model_name': model_name,
        'verbose_name': model._meta.verbose_name
    }
    return render(request, 'dds_app/dictionary_confirm_delete.html', context)

# API views
def get_categories_by_type(request):
    transaction_type_id = request.GET.get('transaction_type_id')
    categories = Category.objects.filter(transaction_type_id=transaction_type_id)
    data = [{'id': cat.id, 'name': cat.name} for cat in categories]  
    return JsonResponse(data, safe=False)

def get_subcategories_by_category(request):
    category_id = request.GET.get('category_id')
    subcategories = Subcategory.objects.filter(category_id=category_id)
    data = [{'id': sub.id, 'name': sub.name} for sub in subcategories]  
    return JsonResponse(data, safe=False)