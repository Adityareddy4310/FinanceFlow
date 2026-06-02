from django.urls import path
from django.contrib.auth import views as auth_views
from core import views

urlpatterns = [
    # Home - redirect to dashboard or login
    path('', views.home, name='home'),

    # Login and Logout (Django built-in, we just give it our template)
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Signup
    path('signup/', views.signup, name='signup'),

    # Dashboard (after login)
    path('dashboard/', views.dashboard, name='dashboard'),
]