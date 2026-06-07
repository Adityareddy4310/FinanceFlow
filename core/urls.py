from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Home & Auth
    path('', views.home, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', views.signup, name='signup'),
    
    # Password Reset
    path('password-reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', views.password_reset_done, name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset/complete/', views.password_reset_complete, name='password_reset_complete'),
    
    # Dashboard & Groups
    path('dashboard/', views.dashboard, name='dashboard'),
    path('group/<int:group_id>/', views.group_detail, name='group_detail'),
    
    # API Endpoints
    path('api/group/<int:group_id>/edit/', views.edit_finance_group, name='edit_finance_group'),
    path('api/group/<int:group_id>/search/', views.search_borrowers, name='search_borrowers'),
    path('api/group/<int:group_id>/add-borrower/', views.add_borrower, name='add_borrower'),
    path('api/borrower/<int:borrower_id>/delete/', views.delete_borrower, name='delete_borrower'),
    path('api/borrower/<int:borrower_id>/update-payment/', views.update_payment, name='update_payment'),
    path('api/borrower/<int:borrower_id>/update-amount-paid/', views.update_amount_paid, name='update_amount_paid'),
    path('api/borrower/<int:borrower_id>/update/', views.update_borrower, name='update_borrower'),
]