"""
URL configuration for accounts app.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('register/', views.UserRegistrationView.as_view(), name='user-register'),
    path('login/', views.UserLoginView.as_view(), name='user-login'),
    path('logout/', views.logout_view, name='user-logout'),
    
    # Profile Management
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    path('profile/extended/', views.UserProfileExtendedView.as_view(), name='user-profile-extended'),
    path('password/change/', views.PasswordChangeView.as_view(), name='password-change'),
    
    # User Management
    path('list/', views.UserListView.as_view(), name='user-list'),
    path('stats/', views.user_stats_view, name='user-stats'),
    path('activity/', views.UserActivityView.as_view(), name='user-activity'),
]
