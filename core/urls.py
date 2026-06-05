from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', views.signup, name='signup'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('group/<int:group_id>/', views.group_detail, name='group_detail'),
    
    # API Endpoints
    path('api/group/<int:group_id>/edit/', views.edit_finance_group, name='edit_finance_group'),
    path('api/group/<int:group_id>/add-borrower/', views.add_borrower, name='add_borrower'),
    path('api/borrower/<int:borrower_id>/delete/', views.delete_borrower, name='delete_borrower'),
    path('api/borrower/<int:borrower_id>/update-payment/', views.update_payment, name='update_payment'),
    path('api/borrower/<int:borrower_id>/update-amount-paid/', views.update_amount_paid, name='update_amount_paid'),
    path('api/borrower/<int:borrower_id>/update/', views.update_borrower, name='update_borrower'),
]