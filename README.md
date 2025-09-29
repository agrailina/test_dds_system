# 📦 DDS Management System  
**Система управления для дистрибьюторских компаний (DDS - Distribution & Delivery System)**  

Этот проект представляет собой систему управления процессами дистрибуции и доставки, разработанную на **Django**.  
Он помогает автоматизировать работу дистрибьюторских компаний, включая учет, управление заказами и обработку данных.  

---

## 🚀 Установка и запуск  

### ✅ Предварительные требования  
Перед началом убедитесь, что у вас установлено:  
- **Python**: версия `3.8+`  
- **pip**: менеджер пакетов Python  
- **Git**: для клонирования репозитория 
---

## Технический стек
- Backend: Django 4.2+
- Database: SQLite (по умолчанию, для разработки)
- Frontend: HTML, CSS, JavaScript
---

### 🔽 Шаги для запуска  

- #### 1. Клонирование репозитория  
    ```bash
    git clone <url-репозитория>
    ```
- #### 2. Создание и активация виртуального окружения
    ####  Создание виртуального окружения
    ```bash
    python -m venv venv
    ```
    #### Активация виртуального окружения
    ```bash
    # Для Windows:
    venv\Scripts\activate
    ```
    ```bash
    # Для Linux/MacOS:
    source venv/bin/activate
    ```
- #### 3. Установка зависимостей
    ```bash
    cd test_dds_system
    cd dds_management
    cd dds_management_system
    pip install -r requirements.txt
    ```
- #### 4. Настройка базы данных
    ```bash
    # Применение миграций
    python manage.py migrate

    # Загрузка начальных данных
    python manage.py load_initial_data
    ```
- #### 5. Запуск сервера разработки
    ```bash
    python manage.py runserver
    ```
После успешного запуска приложение будет доступно по адресу:

👉 http://localhost:8000.


