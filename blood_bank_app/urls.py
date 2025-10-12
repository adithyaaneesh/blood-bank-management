from django.urls import path
from . import views

urlpatterns = [
    path('bloodstock/', views.blood_stock_list, name='blood_stock_list'),
    path('register/', views.user_register, name='register'),
    path('login/', views.user_login, name='login'),
    path('', views.index, name='home'),
    path('contact/', views.contact, name='contact'),
    path('bloodstock/add/', views.add_blood_stock, name='add_blood_stock'),
    path('bloodstock/update/<int:stock_id>/', views.update_blood_stock, name='update_blood_stock'),
    path('bloodstock/delete/<int:stock_id>/', views.delete_blood_stock, name='delete_blood_stock'),
]