from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from datetime import datetime, timedelta, date
import json

from .models import FinanceGroup, Borrower, WeeklyPayment


def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')


def signup(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()

    return render(request, 'registration/signup.html', {'form': form})


@login_required
def dashboard(request):
    groups = FinanceGroup.objects.filter(user=request.user)
    
    if not groups.exists():
        FinanceGroup.objects.create(user=request.user, name='Vizag Finance', day='Sunday', location='Vizag')
        FinanceGroup.objects.create(user=request.user, name='Eluru Finance', day='Monday', location='Eluru')
        groups = FinanceGroup.objects.filter(user=request.user)

    finance_groups = []
    for group in groups:
        borrower_count = group.borrowers.count()
        total_given = sum(float(b.amount_given) for b in group.borrowers.all())
        total_balance = sum(float(b.amount_given) - b.total_paid for b in group.borrowers.all())
        
        pending = WeeklyPayment.objects.filter(
            borrower__finance_group=group,
            payment_date__lte=datetime.now().date(),
            amount_paid=0
        ).count()
        
        color = 'blue' if 'Vizag' in group.name else 'green'
        
        finance_groups.append({
            'id': group.id,
            'name': group.name,
            'day': group.day,
            'location': group.location,
            'total_borrowers': borrower_count,
            'total_given': int(total_given),
            'total_balance': int(total_balance),
            'pending_emis': pending,
            'color': color,
        })

    return render(request, 'core/dashboard.html', {
        'finance_groups': finance_groups,
        'user': request.user,
    })


@login_required
def group_detail(request, group_id):
    group = get_object_or_404(FinanceGroup, id=group_id, user=request.user)
    borrowers = group.borrowers.all()

    # Get current month's first and last date
    today = datetime.now().date()
    first_day = today.replace(day=1)
    
    # Get last day of current month
    if today.month == 12:
        last_day = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        last_day = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
    
    # Generate all days of current month
    days = []
    current = first_day
    while current <= last_day:
        days.append({
            'date': current.isoformat(),
            'display': current.strftime('%d/%m')
        })
        current += timedelta(days=1)

    # Prepare borrower data with payments
    borrower_data = []
    for borrower in borrowers:
        payments = {}
        for day in days:
            payment = WeeklyPayment.objects.filter(
                borrower=borrower,
                payment_date=day['date']
            ).first()
            payments[day['date']] = float(payment.amount_paid) if payment else 0

        borrower_data.append({
            'id': borrower.id,
            'name': borrower.name,
            'amount_given': float(borrower.amount_given),
            'amount_paid': float(borrower.amount_paid),
            'total_paid': borrower.total_paid,
            'balance': borrower.balance,
            'loan_date': borrower.date_of_loan.isoformat(),
            'payments': payments
        })

    # Calculate daily totals
    daily_totals = {}
    for day in days:
        total = 0
        for borrower in borrowers:
            payment = WeeklyPayment.objects.filter(
                borrower=borrower,
                payment_date=day['date']
            ).first()
            if payment:
                total += float(payment.amount_paid)
        daily_totals[day['date']] = total

    total_to_collect = sum(b['balance'] for b in borrower_data)
    month_name = today.strftime('%B %Y')

    return render(request, 'core/group_detail.html', {
        'group': group,
        'borrowers': borrower_data,
        'days': days,
        'daily_totals': daily_totals,
        'total_to_collect': total_to_collect,
        'month_name': month_name,
    })


@login_required
@require_http_methods(["POST"])
def add_borrower(request, group_id):
    group = get_object_or_404(FinanceGroup, id=group_id, user=request.user)
    
    try:
        data = json.loads(request.body)
        name = data.get('name', '').strip()
        amount_given = float(data.get('amount_given', 0))
        date_of_loan_str = data.get('date_of_loan')

        if not name or amount_given <= 0:
            return JsonResponse({'error': 'Invalid name or amount'}, status=400)

        if date_of_loan_str:
            date_of_loan = datetime.fromisoformat(date_of_loan_str).date()
        else:
            date_of_loan = date.today()

        borrower = Borrower.objects.create(
            finance_group=group,
            name=name,
            amount_given=amount_given,
            date_of_loan=date_of_loan
        )

        # Create daily payment records for current month only
        today = datetime.now().date()
        first_day = today.replace(day=1)
        
        if today.month == 12:
            last_day = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            last_day = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
        
        current = first_day
        while current <= last_day:
            WeeklyPayment.objects.get_or_create(
                borrower=borrower,
                payment_date=current,
                defaults={'amount_paid': 0}
            )
            current += timedelta(days=1)

        return JsonResponse({
            'success': True,
            'borrower': {
                'id': borrower.id,
                'name': borrower.name,
                'amount_given': float(borrower.amount_given),
            }
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def delete_borrower(request, borrower_id):
    borrower = get_object_or_404(Borrower, id=borrower_id, finance_group__user=request.user)
    borrower.delete()
    return JsonResponse({'success': True})


@login_required
@require_http_methods(["POST"])
def update_payment(request, borrower_id):
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
    borrower = get_object_or_404(Borrower, id=borrower_id, finance_group__user=request.user)
    
    try:
        data = json.loads(request.body)
        
        if 'name' in data:
            borrower.name = data['name'].strip()
        
        if 'amount_given' in data:
            borrower.amount_given = float(data['amount_given'])
        
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