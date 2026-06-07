from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Prefetch
from datetime import datetime, timedelta, date
from django.urls import reverse_lazy
import json

from .models import FinanceGroup, Borrower, WeeklyPayment
from .forms import CustomUserCreationForm


def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')


def signup(request):
    """Signup with email and phone"""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/signup.html', {'form': form})


class CustomPasswordResetView(PasswordResetView):
    """Password reset view with email"""
    template_name = 'registration/password_reset.html'
    email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')
    
    def form_valid(self, form):
        """Send password reset email"""
        opts = {
            'use_https': self.request.is_secure(),
            'email_template_name': self.email_template_name,
            'subject_template_name': self.subject_template_name,
            'request': self.request,
            'html_email_template_name': None,
        }
        form.save(**opts)
        return super().form_valid(form)


def password_reset_done(request):
    """Password reset email sent confirmation"""
    return render(request, 'registration/password_reset_done.html')


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """Password reset confirm view"""
    template_name = 'registration/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')


def password_reset_complete(request):
    """Password reset complete"""
    return render(request, 'registration/password_reset_complete.html')


@login_required
def dashboard(request):
    """Dashboard with finance groups"""
    groups = FinanceGroup.objects.filter(user=request.user).prefetch_related('borrowers')
    
    if not groups.exists():
        FinanceGroup.objects.create(user=request.user, name='Vizag Finance', day='Sunday Collection - Vizag', location='Vizag')
        FinanceGroup.objects.create(user=request.user, name='Eluru Finance', day='Monday Collection - Eluru', location='Eluru')
        groups = FinanceGroup.objects.filter(user=request.user).prefetch_related('borrowers')

    finance_groups = []
    for group in groups:
        active_borrowers = [b for b in group.borrowers.all() if b.name]
        total_balance = sum(float(b.balance) for b in active_borrowers)
        
        finance_groups.append({
            'id': group.id,
            'name': group.name,
            'day': group.day,
            'location': group.location,
            'active_borrowers': len(active_borrowers),
            'total_balance': int(total_balance),
        })

    return render(request, 'core/dashboard.html', {
        'finance_groups': finance_groups,
        'user': request.user,
    })


@login_required
@require_http_methods(["POST"])
def edit_finance_group(request, group_id):
    """Edit finance group name and day"""
    group = get_object_or_404(FinanceGroup, id=group_id, user=request.user)
    
    try:
        data = json.loads(request.body)
        name = data.get('name', '').strip()
        day = data.get('day', '').strip()
        
        if name:
            group.name = name
        if day:
            group.day = day
        
        group.save()
        
        return JsonResponse({
            'success': True,
            'group': {
                'id': group.id,
                'name': group.name,
                'day': group.day,
            }
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def group_detail(request, group_id):
    """Group detail with search support"""
    group = get_object_or_404(FinanceGroup, id=group_id, user=request.user)
    
    # Get search query
    search_query = request.GET.get('search', '').strip()
    
    # Get borrowers with optional search filter
    borrowers_query = Borrower.objects.filter(
        finance_group=group, 
        name__gt=''
    ).prefetch_related('weekly_payments')
    
    # Apply search filter
    if search_query:
        borrowers_query = borrowers_query.filter(
            Q(name__icontains=search_query) |
            Q(serial_number__icontains=search_query)
        )
    
    all_borrowers = list(borrowers_query.order_by('serial_number'))

    today = datetime.now().date()
    first_day = today.replace(day=1)
    
    if today.month == 12:
        last_day = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        last_day = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
    
    days = []
    current = first_day
    while current <= last_day:
        days.append({
            'date': current.isoformat(),
            'display': current.strftime('%d/%m')
        })
        current += timedelta(days=1)

    borrower_data = []
    daily_totals = {day['date']: 0 for day in days}
    
    for borrower in all_borrowers:
        payments = {day['date']: 0 for day in days}
        
        for payment in borrower.weekly_payments.all():
            payment_date_str = payment.payment_date.isoformat()
            if payment_date_str in payments:
                payments[payment_date_str] = float(payment.amount_paid)
                daily_totals[payment_date_str] += float(payment.amount_paid)

        borrower_data.append({
            'id': borrower.id,
            'serial': borrower.serial_number,
            'name': borrower.name,
            'amount_given': float(borrower.amount_given),
            'amount_paid': float(borrower.amount_paid),
            'total_paid': borrower.total_paid,
            'balance': borrower.balance,
            'loan_date': borrower.date_of_loan.isoformat() if borrower.date_of_loan else '',
            'payments': payments
        })

    total_to_collect = sum(b['balance'] for b in borrower_data)
    month_name = today.strftime('%B %Y')

    return render(request, 'core/group_detail.html', {
        'group': group,
        'borrowers': borrower_data,
        'days': days,
        'daily_totals': daily_totals,
        'total_to_collect': total_to_collect,
        'month_name': month_name,
        'search_query': search_query,
    })


@login_required
def search_borrowers(request, group_id):
    """AJAX search endpoint for borrowers"""
    group = get_object_or_404(FinanceGroup, id=group_id, user=request.user)
    search_query = request.GET.get('q', '').strip()
    
    if len(search_query) < 1:
        return JsonResponse({'results': []})
    
    borrowers = Borrower.objects.filter(
        finance_group=group,
        name__gt=''
    ).filter(
        Q(name__icontains=search_query) |
        Q(serial_number__icontains=search_query)
    )[:10]  # Limit to 10 results
    
    results = []
    for borrower in borrowers:
        results.append({
            'id': borrower.id,
            'serial': borrower.serial_number,
            'name': borrower.name,
            'amount_given': float(borrower.amount_given),
            'balance': borrower.balance,
        })
    
    return JsonResponse({'results': results})


@login_required
@require_http_methods(["POST"])
def add_borrower(request, group_id):
    """Create new borrower"""
    group = get_object_or_404(FinanceGroup, id=group_id, user=request.user)
    
    try:
        data = json.loads(request.body)
        serial_number = int(data.get('serial_number', 0))
        name = data.get('name', '').strip()
        amount_given = float(data.get('amount_given', 0))
        date_of_loan_str = data.get('date_of_loan')

        if serial_number <= 0:
            return JsonResponse({'error': 'Serial number must be greater than 0'}, status=400)
        if not name:
            return JsonResponse({'error': 'Name is required'}, status=400)
        if amount_given <= 0:
            return JsonResponse({'error': 'Amount must be greater than 0'}, status=400)

        existing = Borrower.objects.filter(
            finance_group=group, 
            serial_number=serial_number
        ).first()
        
        if existing and existing.name:
            return JsonResponse({
                'error': f'Serial #{serial_number} already exists'
            }, status=400)

        if existing:
            borrower = existing
        else:
            borrower = Borrower(
                finance_group=group,
                serial_number=serial_number
            )
        
        borrower.name = name
        borrower.amount_given = amount_given
        borrower.amount_paid = 0
        borrower.date_of_loan = datetime.fromisoformat(date_of_loan_str).date() if date_of_loan_str else date.today()
        borrower.save()

        today = datetime.now().date()
        first_day = today.replace(day=1)
        
        if today.month == 12:
            last_day = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            last_day = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
        
        payments_to_create = []
        current = first_day
        while current <= last_day:
            payments_to_create.append(
                WeeklyPayment(
                    borrower=borrower,
                    payment_date=current,
                    amount_paid=0
                )
            )
            current += timedelta(days=1)
        
        WeeklyPayment.objects.bulk_create(payments_to_create, ignore_conflicts=True)

        return JsonResponse({
            'success': True,
            'borrower': {
                'id': borrower.id,
                'serial': borrower.serial_number,
                'name': borrower.name,
            }
        })
    except Exception as e:
        return JsonResponse({'error': f'Error: {str(e)}'}, status=400)


@login_required
@require_http_methods(["POST"])
def delete_borrower(request, borrower_id):
    """Delete borrower"""
    borrower = get_object_or_404(Borrower, id=borrower_id, finance_group__user=request.user)
    borrower.delete()
    return JsonResponse({'success': True})


@login_required
@require_http_methods(["POST"])
def update_payment(request, borrower_id):
    """Update payment"""
    borrower = get_object_or_404(Borrower, id=borrower_id, finance_group__user=request.user)
    
    try:
        data = json.loads(request.body)
        payment_date_str = data.get('date')
        amount = float(data.get('amount', 0))

        payment_date = datetime.fromisoformat(payment_date_str).date()

        payment, created = WeeklyPayment.objects.get_or_create(
            borrower=borrower,
            payment_date=payment_date,
            defaults={'amount_paid': amount}
        )
        
        if not created:
            payment.amount_paid = amount
            payment.save()

        return JsonResponse({
            'success': True,
            'total_paid': borrower.total_paid,
            'balance': borrower.balance
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def update_amount_paid(request, borrower_id):
    """Update amount paid"""
    borrower = get_object_or_404(Borrower, id=borrower_id, finance_group__user=request.user)
    
    try:
        data = json.loads(request.body)
        amount = float(data.get('amount', 0))
        
        borrower.amount_paid = amount
        borrower.save()
        
        return JsonResponse({
            'success': True,
            'total_paid': borrower.total_paid,
            'balance': borrower.balance
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def update_borrower(request, borrower_id):
    """Update borrower details"""
    borrower = get_object_or_404(Borrower, id=borrower_id, finance_group__user=request.user)
    
    try:
        data = json.loads(request.body)
        
        if 'name' in data:
            borrower.name = data['name'].strip()
        
        if 'amount_given' in data:
            borrower.amount_given = float(data['amount_given'])
        
        if 'date_of_loan' in data and data['date_of_loan']:
            borrower.date_of_loan = datetime.fromisoformat(data['date_of_loan']).date()
        
        borrower.save()
        
        return JsonResponse({
            'success': True,
            'borrower': {
                'id': borrower.id,
                'name': borrower.name,
                'amount_given': float(borrower.amount_given),
                'total_paid': borrower.total_paid,
                'balance': borrower.balance
            }
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)