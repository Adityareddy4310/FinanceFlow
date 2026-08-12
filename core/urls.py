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
    path('contact/', views.contact, name='contact'),
    
    # API Endpoints
    path('api/group/<int:group_id>/edit/', views.edit_finance_group, name='edit_finance_group'),
    path('api/group/<int:group_id>/search/', views.search_borrowers, name='search_borrowers'),
    path('api/group/<int:group_id>/add-borrower/', views.add_borrower, name='add_borrower'),
    path('api/borrower/<int:borrower_id>/delete/', views.delete_borrower, name='delete_borrower'),
    path('api/borrower/<int:borrower_id>/update-payment/', views.update_payment, name='update_payment'),
    path('api/borrower/<int:borrower_id>/update-amount-paid/', views.update_amount_paid, name='update_amount_paid'),
    path('api/borrower/<int:borrower_id>/update/', views.update_borrower, name='update_borrower'),


    path('api/group/<int:group_id>/import-excel/preview/', views.import_borrowers_preview, name='import_borrowers_preview'),
    path('api/group/<int:group_id>/import-excel/confirm/', views.import_borrowers_confirm, name='import_borrowers_confirm'),
    path('api/group/<int:group_id>/export-excel/', views.export_borrowers_excel, name='export_borrowers_excel'),
    path('api/group/<int:group_id>/cash-flow/', views.cash_flow_data, name='cash_flow_data'),
    path('api/borrower/<int:borrower_id>/give-new-loan/', views.give_new_loan, name='give_new_loan'),
    path('api/borrower/<int:borrower_id>/loan-history/', views.loan_history, name='loan_history'),
    path('api/group/<int:group_id>/cash-flow/', views.cash_flow_summary, name='cash_flow_summary'),

    path('api/group/<int:group_id>/cash-flow-extras/', views.cash_flow_extras, name='cash_flow_extras'),
    path('api/group/<int:group_id>/add-expense/', views.add_expense, name='add_expense'),
    path('api/expense/<int:expense_id>/delete/', views.delete_expense, name='delete_expense'),
    path('api/group/<int:group_id>/update-interest/', views.update_interest, name='update_interest'),
    path('api/group/<int:group_id>/save-collection-staff/', views.save_collection_staff, name='save_collection_staff'),
]