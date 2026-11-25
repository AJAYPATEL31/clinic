from django.urls import path
from . import views

urlpatterns = [
    # Dashboard & Root
    path('', views.admin_dashboard_view, name='dashboard'),
    path('dashboard/', views.admin_dashboard_view, name='dashboard'),

    # Day 1 & Day 2 Auth URLs
    path('login/', views.admin_login_view, name='login'),
    path('logout/', views.admin_logout_view, name='logout'),

    # Day 3 Doctor Category CRUD URLs
    path('categories/', views.category_list_view, name='category_list'),
    path('categories/add/', views.category_add_view, name='category_add'),
    path('categories/<int:pk>/edit/', views.category_edit_view, name='category_edit'),
    path('categories/<int:pk>/delete/', views.category_delete_view, name='category_delete'),

    # Department Management URLs
    path('departments/', views.department_list_view, name='department_list'),
    path('departments/add/', views.department_add_view, name='department_add'),
    path('departments/<int:pk>/edit/', views.department_edit_view, name='department_edit'),
    path('departments/<int:pk>/delete/', views.department_delete_view, name='department_delete'),

    # Doctor Registration URLs
    path('doctors/', views.doctor_list_view, name='doctor_list'),
    path('doctors/register/', views.doctor_register_view, name='doctor_register'),
    path('doctors/<int:pk>/confirmation/', views.doctor_confirmation_view, name='doctor_confirmation'),
    path('doctors/<int:pk>/edit/', views.doctor_edit_view, name='doctor_edit'),
    path('doctors/<int:pk>/delete/', views.doctor_delete_view, name='doctor_delete'),
]
