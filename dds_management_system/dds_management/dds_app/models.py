from django.db import models
from django.core.exceptions import ValidationError
from datetime import date

# Статусы
class Status(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Название статуса")
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Статус"
        verbose_name_plural = "Статусы"

# Тип транзакции
class TransactionType(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Название типа")
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Тип операции"
        verbose_name_plural = "Типы операций"

# Категория транзакции
class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название категории")
    transaction_type = models.ForeignKey(TransactionType, on_delete=models.CASCADE, verbose_name="Тип операции")
    
    def __str__(self):
        return self.name  
    
    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        unique_together = ['name', 'transaction_type']

# Подкатегория транзакции
class Subcategory(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название подкатегории")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Категория")
    
    def __str__(self):
        return self.name  
    
    class Meta:
        verbose_name = "Подкатегория"
        verbose_name_plural = "Подкатегории"
        unique_together = ['name', 'category']

# Транзакция
class Transaction(models.Model):
    date = models.DateField(default=date.today, verbose_name="Дата операции")
    status = models.ForeignKey(Status, on_delete=models.PROTECT, verbose_name="Статус")
    transaction_type = models.ForeignKey(TransactionType, on_delete=models.PROTECT, verbose_name="Тип операции")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, verbose_name="Категория")
    subcategory = models.ForeignKey(Subcategory, on_delete=models.PROTECT, verbose_name="Подкатегория")
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Сумма")
    comment = models.TextField(blank=True, verbose_name="Комментарий")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания записи")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления записи")
    
    def clean(self):
        # Проверяем только если все связанные объекты существуют
        if hasattr(self, 'subcategory') and self.subcategory and hasattr(self, 'category') and self.category:
            if self.subcategory.category != self.category:
                raise ValidationError("Выбранная подкатегория не принадлежит выбранной категории")
        
        if hasattr(self, 'category') and self.category and hasattr(self, 'transaction_type') and self.transaction_type:
            if self.category.transaction_type != self.transaction_type:
                raise ValidationError("Выбранная категория не принадлежит выбранному типу операции")
    
    def __str__(self):
        return f"{self.date} - {self.transaction_type} - {self.amount:.2f} руб."  # Исправлено форматирование
    
    class Meta:
        verbose_name = "Транзакция"
        verbose_name_plural = "Транзакции"
        ordering = ['-date', '-created_at']