from django.urls import path
from . import views

urlpatterns = [
    
    path('bloodstock/', views.blood_stock_list, name='blood_stock_list'),
    path('register/', views.register, name='register'),
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
    path('donors/', views.admin_donors, name='admin_donors'),
    path('patients/', views.admin_patients, name='admin_patients'),
    path('admin_donor_list/', views.admin_donor_list, name='admin_donors_list'),
    path('hospitals/', views.admin_hospitals, name='admin_hospitals'),
    path('admin_blood_request/', views.admin_blood_request, name='admin_blood_request'),
    path('bloodrequests/approve/<int:pk>/', views.approve_request, name='approve_request'),
    path('bloodrequests/reject/<int:pk>/', views.reject_request, name='reject_request'),
    path('donors/dashboard/', views.admin_donors, name='admin_donor_dashboard'),
    path('donor/<int:donor_id>/<str:status>/', views.update_donor_status, name='update_donor_status'),
    path('history/', views.donor_history, name='donor_history'),
    path('request-history/', views.patient_request_history, name='request_history'),
    path('blood-request/', views.admin_blood_request, name='admin_blood_request'),
    path('approve-request/<int:pk>/', views.approve_request, name='approve_request'),
    path('reject-request/<int:pk>/', views.reject_request, name='reject_request'),
    path('deletedonorreq/', views.delete_my_donor_requests, name='delete_my_donor_requests'),
    path('deletealldonors/', views.delete_all_donor_requests, name='delete_all_donor_requests'),
    path('hospitalrequests/', views.hospital_request_history, name='hospital_request_history'),

    path('adminprofile/profile/', views.admin_profile, name='admin_profile'),

    path('hospital/profile/', views.hospital_profile, name='hospital_profile'),
    path('hospital/profile/view/', views.hospital_profile_view, name='hospital_profile_view'),

]