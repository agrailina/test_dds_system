from django.core.management.base import BaseCommand
from dds_app.models import Status, TransactionType, Category, Subcategory

class Command(BaseCommand):
    help = 'Load initial data for DDS application'
    
    def handle(self, *args, **options):
        # Статусы
        status_business = Status.objects.get_or_create(name='Бизнес')[0]
        status_personal = Status.objects.get_or_create(name='Личное')[0]
        status_tax = Status.objects.get_or_create(name='Налог')[0]
        
        # Типы операций
        type_income = TransactionType.objects.get_or_create(name='Пополнение')[0]
        type_expense = TransactionType.objects.get_or_create(name='Списание')[0]
        
        # Категории и подкатегории для расходов
        category_infra = Category.objects.get_or_create(
            name='Инфраструктура', 
            transaction_type=type_expense
        )[0]
        Subcategory.objects.get_or_create(name='VPS', category=category_infra)
        Subcategory.objects.get_or_create(name='Proxy', category=category_infra)
        
        category_marketing = Category.objects.get_or_create(
            name='Маркетинг', 
            transaction_type=type_expense
        )[0]
        Subcategory.objects.get_or_create(name='Farpost', category=category_marketing)
        Subcategory.objects.get_or_create(name='Avito', category=category_marketing)
        
        # Категории для доходов
        category_sales = Category.objects.get_or_create(
            name='Продажи', 
            transaction_type=type_income
        )[0]
        Subcategory.objects.get_or_create(name='Онлайн', category=category_sales)
        Subcategory.objects.get_or_create(name='Оффлайн', category=category_sales)
        
        self.stdout.write(
            self.style.SUCCESS('Initial data loaded successfully!')
        )