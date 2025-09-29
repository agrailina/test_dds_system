from django.urls import path
from . import views

urlpatterns = [
    path('', views.transaction_list, name='transaction_list'),
    path('transaction/create/', views.transaction_create, name='transaction_create'),
    path('transaction/<int:pk>/edit/', views.transaction_edit, name='transaction_edit'),
    path('transaction/<int:pk>/delete/', views.transaction_delete, name='transaction_delete'),
    
    path('dictionaries/', views.dictionaries, name='dictionaries'),
    path('dictionaries/<str:model_name>/add/', views.add_dictionary_item, name='add_dictionary_item'),
    path('dictionaries/<str:model_name>/<int:pk>/edit/', views.edit_dictionary_item, name='edit_dictionary_item'),
    path('dictionaries/<str:model_name>/<int:pk>/delete/', views.delete_dictionary_item, name='delete_dictionary_item'),
    
    path('api/categories/by-type/', views.get_categories_by_type, name='get_categories_by_type'),
    path('api/subcategories/by-category/', views.get_subcategories_by_category, name='get_subcategories_by_category'),
]