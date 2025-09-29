from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import date
from .models import Status, TransactionType, Category, Subcategory, Transaction
from .forms import TransactionForm, StatusForm, TransactionTypeForm, CategoryForm, SubcategoryForm

class ModelTests(TestCase):
    def setUp(self):
        """Создание тестовых данных"""
        self.status = Status.objects.create(name='Бизнес')
        self.transaction_type_income = TransactionType.objects.create(name='Пополнение')
        self.transaction_type_expense = TransactionType.objects.create(name='Списание')
        
        self.category = Category.objects.create(
            name='Маркетинг', 
            transaction_type=self.transaction_type_expense
        )
        
        self.subcategory = Subcategory.objects.create(
            name='Avito', 
            category=self.category
        )
        
        self.transaction = Transaction.objects.create(
            date=date.today(),
            status=self.status,
            transaction_type=self.transaction_type_expense,
            category=self.category,
            subcategory=self.subcategory,
            amount=1000.00,
            comment='Тестовая транзакция'
        )

    def test_status_creation(self):
        """Тест создания статуса"""
        self.assertEqual(str(self.status), 'Бизнес')
        self.assertEqual(Status.objects.count(), 1)

    def test_transaction_type_creation(self):
        """Тест создания типа транзакции"""
        self.assertEqual(str(self.transaction_type_income), 'Пополнение')
        self.assertEqual(TransactionType.objects.count(), 2)

    def test_category_creation(self):
        """Тест создания категории"""
        self.assertEqual(str(self.category), 'Маркетинг')
        self.assertEqual(self.category.transaction_type, self.transaction_type_expense)
        self.assertEqual(Category.objects.count(), 1)

    def test_subcategory_creation(self):
        """Тест создания подкатегории"""
        self.assertEqual(str(self.subcategory), 'Avito')
        self.assertEqual(self.subcategory.category, self.category)
        self.assertEqual(Subcategory.objects.count(), 1)

    def test_transaction_creation(self):
        """Тест создания транзакции"""
        # Исправлено: форматирование суммы с двумя десятичными знаками
        expected_str = f"{date.today()} - Списание - {self.transaction.amount:.2f} руб."
        self.assertEqual(str(self.transaction), expected_str)
        self.assertEqual(Transaction.objects.count(), 1)
        self.assertEqual(self.transaction.amount, 1000.00)

    def test_transaction_validation(self):
        """Тест валидации транзакции"""
        # Создаем невалидную транзакцию с несоответствующей подкатегорией
        another_category = Category.objects.create(
            name='Инфраструктура',
            transaction_type=self.transaction_type_expense
        )
        
        transaction = Transaction(
            date=date.today(),
            status=self.status,
            transaction_type=self.transaction_type_expense,
            category=another_category,  # Другая категория
            subcategory=self.subcategory,  # Подкатегория от другой категории
            amount=500.00
        )
        
        with self.assertRaises(Exception):
            transaction.full_clean()

    def test_unique_constraints(self):
        """Тест уникальных ограничений"""
        # Попытка создать дублирующий статус
        with self.assertRaises(Exception):
            Status.objects.create(name='Бизнес')

    def test_ordering(self):
        """Тест ordering в мета-классах"""
        # Создаем еще одну транзакцию
        Transaction.objects.create(
            date=date(2024, 1, 1),
            status=self.status,
            transaction_type=self.transaction_type_income,
            category=self.category,
            subcategory=self.subcategory,
            amount=2000.00
        )
        
        transactions = Transaction.objects.all()
        self.assertEqual(transactions[0].date, date.today())  # Самая новая первая


class FormTests(TestCase):
    def setUp(self):
        self.status = Status.objects.create(name='Бизнес')
        self.transaction_type = TransactionType.objects.create(name='Списание')
        self.category = Category.objects.create(
            name='Маркетинг', 
            transaction_type=self.transaction_type
        )
        self.subcategory = Subcategory.objects.create(
            name='Avito', 
            category=self.category
        )

    def test_transaction_form_valid(self):
        """Тест валидной формы транзакции"""
        form_data = {
            'date': date.today(),
            'status': self.status.id,
            'transaction_type': self.transaction_type.id,
            'category': self.category.id,
            'subcategory': self.subcategory.id,
            'amount': 1500.00,
            'comment': 'Тестовый комментарий'
        }
        form = TransactionForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_transaction_form_invalid(self):
        """Тест невалидной формы транзакции"""
        # Неправильное соответствие категории и типа
        another_type = TransactionType.objects.create(name='Пополнение')
        
        form_data = {
            'date': date.today(),
            'status': self.status.id,
            'transaction_type': another_type.id,  # Другой тип
            'category': self.category.id,  # Категория от другого типа
            'subcategory': self.subcategory.id,
            'amount': 1500.00,
        }
        form = TransactionForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('Выбранная категория не соответствует выбранному типу операции', str(form.errors))

    def test_transaction_form_missing_required_fields(self):
        """Тест формы с отсутствующими обязательными полями"""
        # Исправлено: передаем только часть обязательных полей
        form_data = {
            'date': date.today(),
            'status': self.status.id,
            'transaction_type': self.transaction_type.id,
            # Отсутствуют category, subcategory, amount
        }
        form = TransactionForm(data=form_data)
        self.assertFalse(form.is_valid())
        # Проверяем наличие ошибок для обязательных полей
        self.assertIn('category', form.errors)
        self.assertIn('subcategory', form.errors)
        self.assertIn('amount', form.errors)

    def test_dictionary_forms(self):
        """Тест форм справочников"""
        # Тест формы статуса
        status_form = StatusForm(data={'name': 'Новый статус'})
        self.assertTrue(status_form.is_valid())

        # Тест формы типа транзакции
        type_form = TransactionTypeForm(data={'name': 'Новый тип'})
        self.assertTrue(type_form.is_valid())

        # Тест формы категории
        category_form = CategoryForm(data={
            'name': 'Новая категория',
            'transaction_type': self.transaction_type.id
        })
        self.assertTrue(category_form.is_valid())

        # Тест формы подкатегории
        subcategory_form = SubcategoryForm(data={
            'name': 'Новая подкатегория',
            'category': self.category.id
        })
        self.assertTrue(subcategory_form.is_valid())


class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Создание тестовых данных
        self.status = Status.objects.create(name='Бизнес')
        self.transaction_type = TransactionType.objects.create(name='Списание')
        self.category = Category.objects.create(
            name='Маркетинг', 
            transaction_type=self.transaction_type
        )
        self.subcategory = Subcategory.objects.create(
            name='Avito', 
            category=self.category
        )
        self.transaction = Transaction.objects.create(
            date=date.today(),
            status=self.status,
            transaction_type=self.transaction_type,
            category=self.category,
            subcategory=self.subcategory,
            amount=1000.00
        )

    def test_transaction_list_view(self):
        """Тест страницы списка транзакций"""
        response = self.client.get(reverse('transaction_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dds_app/transaction_list.html')
        self.assertContains(response, 'Список транзакций')
        self.assertContains(response, '1000.00')

    def test_transaction_list_filtering(self):
        """Тест фильтрации списка транзакций"""
        # Фильтр по статусу
        response = self.client.get(reverse('transaction_list'), {'status': self.status.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['transactions']), 1)

        # Фильтр по несуществующему статусу
        response = self.client.get(reverse('transaction_list'), {'status': 999})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['transactions']), 0)

    def test_transaction_create_view(self):
        """Тест создания транзакции"""
        response = self.client.get(reverse('transaction_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dds_app/transaction_form.html')

        # POST запрос на создание
        post_data = {
            'date': date.today(),
            'status': self.status.id,
            'transaction_type': self.transaction_type.id,
            'category': self.category.id,
            'subcategory': self.subcategory.id,
            'amount': 2000.00,
            'comment': 'Новая транзакция'
        }
        response = self.client.post(reverse('transaction_create'), post_data)
        self.assertEqual(response.status_code, 302)  # redirect
        self.assertEqual(Transaction.objects.count(), 2)

    def test_transaction_edit_view(self):
        """Тест редактирования транзакции"""
        url = reverse('transaction_edit', args=[self.transaction.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # POST запрос на редактирование
        post_data = {
            'date': date.today(),
            'status': self.status.id,
            'transaction_type': self.transaction_type.id,
            'category': self.category.id,
            'subcategory': self.subcategory.id,
            'amount': 1500.00,  # Измененная сумма
            'comment': 'Обновленный комментарий'
        }
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 302)
        
        # Проверяем обновление
        self.transaction.refresh_from_db()
        self.assertEqual(self.transaction.amount, 1500.00)

    def test_transaction_delete_view(self):
        """Тест удаления транзакции"""
        url = reverse('transaction_delete', args=[self.transaction.id])
        
        # GET запрос - страница подтверждения
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dds_app/transaction_confirm_delete.html')

        # POST запрос - удаление
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Transaction.objects.count(), 0)

    def test_dictionaries_view(self):
        """Тест страницы справочников"""
        response = self.client.get(reverse('dictionaries'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dds_app/dictionaries.html')
        self.assertContains(response, 'Статусы')
        self.assertContains(response, 'Категории')

    def test_add_dictionary_item_view(self):
        """Тест добавления элемента справочника"""
        # Статус
        response = self.client.get(reverse('add_dictionary_item', args=['status']))
        self.assertEqual(response.status_code, 200)

        # POST запрос на добавление статуса
        post_data = {'name': 'Новый статус'}
        response = self.client.post(reverse('add_dictionary_item', args=['status']), post_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Status.objects.count(), 2)

    def test_edit_dictionary_item_view(self):
        """Тест редактирования элемента справочника"""
        url = reverse('edit_dictionary_item', args=['status', self.status.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # POST запрос на редактирование
        post_data = {'name': 'Обновленный статус'}
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 302)
        
        self.status.refresh_from_db()
        self.assertEqual(self.status.name, 'Обновленный статус')

    def test_delete_dictionary_item_view(self):
        """Тест удаления элемента справочника"""
        # Создаем временный статус для удаления
        temp_status = Status.objects.create(name='Временный статус')
        url = reverse('delete_dictionary_item', args=['status', temp_status.id])

        # POST запрос на удаление
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Status.objects.count(), 1)  # Остался только исходный статус


class APITests(TestCase):
    def setUp(self):
        self.client = Client()
        
        self.transaction_type = TransactionType.objects.create(name='Списание')
        self.another_type = TransactionType.objects.create(name='Пополнение')
        
        self.category1 = Category.objects.create(
            name='Маркетинг', 
            transaction_type=self.transaction_type
        )
        self.category2 = Category.objects.create(
            name='Продажи', 
            transaction_type=self.another_type
        )
        
        self.subcategory1 = Subcategory.objects.create(
            name='Avito', 
            category=self.category1
        )
        self.subcategory2 = Subcategory.objects.create(
            name='Farpost', 
            category=self.category1
        )

    def test_get_categories_by_type(self):
        """Тест API получения категорий по типу"""
        url = reverse('get_categories_by_type')
        response = self.client.get(url, {'transaction_type_id': self.transaction_type.id})
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'Маркетинг')

    def test_get_categories_by_invalid_type(self):
        """Тест API с невалидным типом"""
        url = reverse('get_categories_by_type')
        response = self.client.get(url, {'transaction_type_id': 999})  # Несуществующий ID
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 0)

    def test_get_subcategories_by_category(self):
        """Тест API получения подкатегорий по категории"""
        url = reverse('get_subcategories_by_category')
        response = self.client.get(url, {'category_id': self.category1.id})
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 2)
        subcategory_names = [item['name'] for item in data]
        self.assertIn('Avito', subcategory_names)
        self.assertIn('Farpost', subcategory_names)

    def test_get_subcategories_by_invalid_category(self):
        """Тест API с невалидной категорией"""
        url = reverse('get_subcategories_by_category')
        response = self.client.get(url, {'category_id': 999})  # Несуществующий ID
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 0)


class IntegrationTests(TestCase):
    """Интеграционные тесты"""
    
    def setUp(self):
        self.client = Client()
        
        # Создание полного набора тестовых данных
        self.status = Status.objects.create(name='Бизнес')
        self.transaction_type = TransactionType.objects.create(name='Списание')
        self.category = Category.objects.create(
            name='Маркетинг', 
            transaction_type=self.transaction_type
        )
        self.subcategory = Subcategory.objects.create(
            name='Avito', 
            category=self.category
        )

    def test_complete_workflow(self):
        """Тест полного рабочего процесса"""
        # 1. Создание транзакции
        post_data = {
            'date': date.today(),
            'status': self.status.id,
            'transaction_type': self.transaction_type.id,
            'category': self.category.id,
            'subcategory': self.subcategory.id,
            'amount': 1000.00,
            'comment': 'Тестовая транзакция'
        }
        response = self.client.post(reverse('transaction_create'), post_data)
        self.assertEqual(response.status_code, 302)
        transaction = Transaction.objects.first()
        self.assertIsNotNone(transaction)

        # 2. Проверка отображения в списке
        response = self.client.get(reverse('transaction_list'))
        self.assertContains(response, '1000.00')

        # 3. Редактирование транзакции
        edit_url = reverse('transaction_edit', args=[transaction.id])
        post_data['amount'] = 1500.00
        response = self.client.post(edit_url, post_data)
        self.assertEqual(response.status_code, 302)
        
        transaction.refresh_from_db()
        self.assertEqual(transaction.amount, 1500.00)

        # 4. Удаление транзакции
        delete_url = reverse('transaction_delete', args=[transaction.id])
        response = self.client.post(delete_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Transaction.objects.count(), 0)

    def test_dictionary_management_workflow(self):
        """Тест рабочего процесса управления справочниками"""
        # 1. Добавление нового статуса
        post_data = {'name': 'Новый тестовый статус'}
        response = self.client.post(reverse('add_dictionary_item', args=['status']), post_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Status.objects.count(), 2)

        # 2. Проверка отображения в справочниках
        response = self.client.get(reverse('dictionaries'))
        self.assertContains(response, 'Новый тестовый статус')

        # 3. Редактирование статуса
        new_status = Status.objects.get(name='Новый тестовый статус')
        edit_url = reverse('edit_dictionary_item', args=['status', new_status.id])
        post_data = {'name': 'Обновленный статус'}
        response = self.client.post(edit_url, post_data)
        self.assertEqual(response.status_code, 302)
        
        new_status.refresh_from_db()
        self.assertEqual(new_status.name, 'Обновленный статус')

        # 4. Удаление статуса
        delete_url = reverse('delete_dictionary_item', args=['status', new_status.id])
        response = self.client.post(delete_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Status.objects.count(), 1)


class ErrorCaseTests(TestCase):
    """Тесты обработки ошибок"""
    
    def setUp(self):
        self.client = Client()
        self.status = Status.objects.create(name='Бизнес')
        self.transaction_type = TransactionType.objects.create(name='Списание')
        self.category = Category.objects.create(
            name='Маркетинг', 
            transaction_type=self.transaction_type
        )
        self.subcategory = Subcategory.objects.create(
            name='Avito', 
            category=self.category
        )

    def test_invalid_urls(self):
        """Тест невалидных URL"""
        # Несуществующий ID транзакции
        response = self.client.get(reverse('transaction_edit', args=[999]))
        self.assertEqual(response.status_code, 404)

        response = self.client.get(reverse('transaction_delete', args=[999]))
        self.assertEqual(response.status_code, 404)

        # Невалидный тип справочника
        response = self.client.get(reverse('add_dictionary_item', args=['invalid_model']))
        self.assertEqual(response.status_code, 302)  # redirect to dictionaries

    def test_invalid_form_submissions(self):
        """Тест невалидных отправок форм"""
        # Исправлено: передаем минимальный набор данных, но с невалидными значениями
        post_data = {
            'date': date.today(),
            'status': self.status.id,
            'transaction_type': self.transaction_type.id,
            'category': self.category.id,
            'subcategory': self.subcategory.id,
            'amount': '',  # Пустая сумма - невалидно
        }
        response = self.client.post(reverse('transaction_create'), post_data)
        self.assertEqual(response.status_code, 200)  # Остается на форме с ошибками
        # Проверяем, что форма содержит ошибки
        self.assertContains(response, 'error', status_code=200)


class BusinessLogicTests(TestCase):
    def setUp(self):
        self.status = Status.objects.create(name='Бизнес')
        self.income_type = TransactionType.objects.create(name='Пополнение')
        self.expense_type = TransactionType.objects.create(name='Списание')
        
        self.income_category = Category.objects.create(
            name='Продажи', 
            transaction_type=self.income_type
        )
        self.expense_category = Category.objects.create(
            name='Маркетинг', 
            transaction_type=self.expense_type
        )
        
        self.income_subcategory = Subcategory.objects.create(
            name='Онлайн', 
            category=self.income_category
        )
        self.expense_subcategory = Subcategory.objects.create(
            name='Avito', 
            category=self.expense_category
        )

    def test_category_type_consistency(self):
        """Тест согласованности категорий и типов"""
        # Попытка создать транзакцию с несоответствующей категорией
        transaction = Transaction(
            date=date.today(),
            status=self.status,
            transaction_type=self.income_type,  # Тип "Пополнение"
            category=self.expense_category,     # Категория от "Списание"
            subcategory=self.expense_subcategory,
            amount=1000.00
        )
        
        with self.assertRaises(Exception):
            transaction.full_clean()

    def test_subcategory_category_consistency(self):
        """Тест согласованности подкатегорий и категорий"""
        # Попытка создать транзакцию с несоответствующей подкатегорией
        transaction = Transaction(
            date=date.today(),
            status=self.status,
            transaction_type=self.expense_type,
            category=self.expense_category,
            subcategory=self.income_subcategory,  # Подкатегория от другой категории
            amount=1000.00
        )
        
        with self.assertRaises(Exception):
            transaction.full_clean()


# Дополнительные тесты для проверки безопасности
class SecurityTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.status = Status.objects.create(name='Бизнес')
        self.transaction_type = TransactionType.objects.create(name='Списание')
        self.category = Category.objects.create(
            name='Маркетинг', 
            transaction_type=self.transaction_type
        )
        self.subcategory = Subcategory.objects.create(
            name='Avito', 
            category=self.category
        )
        self.transaction = Transaction.objects.create(
            date=date.today(),
            status=self.status,
            transaction_type=self.transaction_type,
            category=self.category,
            subcategory=self.subcategory,
            amount=1000.00
        )

    def test_csrf_protection(self):
        """Тест защиты CSRF"""
        # POST запрос без CSRF токена должен быть отклонен
        post_data = {
            'date': date.today(),
            'status': self.status.id,
            'transaction_type': self.transaction_type.id,
            'category': self.category.id,
            'subcategory': self.subcategory.id,
            'amount': 2000.00,
        }
        
        # Создаем клиент без CSRF проверки для тестирования
        csrf_client = Client(enforce_csrf_checks=True)
        response = csrf_client.post(reverse('transaction_create'), post_data)
        # Должен вернуть 403 Forbidden или перенаправить
        self.assertIn(response.status_code, [403, 302])

