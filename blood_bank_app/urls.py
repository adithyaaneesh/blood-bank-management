from django.urls import path
from . import views

urlpatterns = [
    
    path('bloodstock/', views.blood_stock_list, name='blood_stock_list'),
    path('register/', views.register, name='register'),
    path('hospital_register/', views.hospital_register, name='hospitalregister'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('', views.index, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('stock_details/', views.stock_details, name='stock_details'),
    path('bloodstock/add/', views.add_blood_stock, name='add_blood_stock'),
    path('bloodstock/update/<int:stock_id>/', views.update_blood_stock, name='update_blood_stock'),
    path('bloodstock/delete/<int:stock_id>/', views.delete_blood_stock, name='delete_blood_stock'),
    path('patienthome/', views.patient_home, name='patienthome'),
    path('donorhome/', views.donor_home, name='donorhome'),
    path('donateform/', views.donate_form, name='donateform'),
    path('requestform/', views.request_form, name='requestform'),
    path('hospitalhome/', views.hospital_home, name='hospitalhome'),
    path('hospitalhome/', views.hospital_home, name='hospitalhome'),
    path('hospitalrequest/', views.hospital_request_form, name='hospitalrequest'),
    path('hospitalstock/', views.hospital_stock, name='hospitalstock'),
]