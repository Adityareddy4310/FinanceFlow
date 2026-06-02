from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

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

    # Finance Group Detail (EMI Sheet)
    path('group/<int:group_id>/', views.group_detail, name='group_detail'),

    # API Endpoints for saving data
    path('api/group/<int:group_id>/add-borrower/', views.add_borrower, name='add_borrower'),
    path('api/borrower/<int:borrower_id>/delete/', views.delete_borrower, name='delete_borrower'),
    path('api/borrower/<int:borrower_id>/update-payment/', views.update_payment, name='update_payment'),
    path('api/borrower/<int:borrower_id>/update/', views.update_borrower, name='update_borrower'),
]