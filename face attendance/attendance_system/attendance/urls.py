from django.urls import path, include
from . import views
from .views import *


urlpatterns = [
    path('', views.home, name='home'),
   path('login/', views.user_login, name='login'),
    # path('attendance-report/', views.attendance_report), # Correct this
    path('admin-login/', views.admin_login, name='admin_login'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('add-user/', views.add_user, name='add_user'),
    path('list-users/', views.list_users, name='list_users'),
    path('edit-user/<int:user_id>/', views.edit_user, name='edit_user'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('mark-attendance/<str:data>/', views.mark_attendance_view, name='mark_attendance'),
    path('admin_attendance_report/', views.admin_attendance_report, name='admin_attendance_report'), 
]


