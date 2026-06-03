from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from datetime import datetime, timedelta
import json

from .models import FinanceGroup, Borrower, WeeklyPayment


def home(request):
    """Redirect to dashboard if logged in, else to login"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')


def signup(request):
    """Handle user signup"""
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
    """Show user's finance groups"""
    # Get or create sample finance groups for this user
    groups = FinanceGroup.objects.filter(user=request.user)
    
    # If no groups exist, create sample ones (only once)
    if not groups.exists():
        FinanceGroup.objects.create(
            user=request.user,
            name='Vizag Finance',
            day='Sunday',
            location='Vizag'
        )
        FinanceGroup.objects.create(
            user=request.user,
            name='Eluru Finance',
            day='Monday',
            location='Eluru'
        )
        groups = FinanceGroup.objects.filter(user=request.user)

    # Add stats to each group
    finance_groups = []
    for group in groups:
        borrower_count = group.borrowers.count()
        total_given = sum(float(b.amount_given) for b in group.borrowers.all())
        
        # Count pending EMIs (payment_date <= today AND amount_paid = 0)
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
            'pending_emis': pending,
            'color': color,
        })

    return render(request, 'core/dashboard.html', {
        'finance_groups': finance_groups,
        'user': request.user,
    })


@login_required
def group_detail(request, group_id):
    """Show the EMI sheet for a specific finance group"""
    group = get_object_or_404(FinanceGroup, id=group_id, user=request.user)
    borrowers = group.borrowers.all()

    # Generate 20 weeks of dates starting from today
    today = datetime.now().date()
    weeks = []
    for i in range(20):
        date = today + timedelta(weeks=i)
        weeks.append({
            'date': date.isoformat(),  # Convert to ISO string format
            'display': date.strftime('%d/%m/%Y')
        })

    # Prepare borrower data with payments
    borrower_data = []
    for borrower in borrowers:
        payments = {}
        for week in weeks:
            payment = WeeklyPayment.objects.filter(
                borrower=borrower,
                payment_date=week['date']  # Now using ISO string
            ).first()
            payments[week['date']] = float(payment.amount_paid) if payment else 0

        borrower_data.append({
            'id': borrower.id,
            'name': borrower.name,
            'amount_given': float(borrower.amount_given),
            'total_paid': borrower.total_paid,
            'balance': borrower.balance,
            'payments': payments
        })

    # Calculate daily totals
    daily_totals = {}
    for week in weeks:
        total = 0
        for borrower in borrowers:
            payment = WeeklyPayment.objects.filter(
                borrower=borrower,
                payment_date=week['date']  # Now using ISO string
            ).first()
            if payment:
                total += float(payment.amount_paid)
        daily_totals[week['date']] = total

    return render(request, 'core/group_detail.html', {
        'group': group,
        'borrowers': borrower_data,
        'weeks': weeks,
        'daily_totals': daily_totals,
    })


@login_required
@require_http_methods(["POST"])
def add_borrower(request, group_id):
    """Add a new borrower to a finance group"""
    group = get_object_or_404(FinanceGroup, id=group_id, user=request.user)
    
    try:
        data = json.loads(request.body)
        name = data.get('name', '').strip()
        amount_given = float(data.get('amount_given', 0))

        if not name or amount_given <= 0:
            return JsonResponse({'error': 'Invalid name or amount'}, status=400)

        borrower = Borrower.objects.create(
            finance_group=group,
            name=name,
            amount_given=amount_given
        )

        # Create empty payment records for 20 weeks
        today = datetime.now().date()
        for i in range(20):
            date = today + timedelta(weeks=i)
            WeeklyPayment.objects.get_or_create(
                borrower=borrower,
                payment_date=date,
                defaults={'amount_paid': 0}
            )

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
    """Delete a borrower"""
    borrower = get_object_or_404(Borrower, id=borrower_id, finance_group__user=request.user)
    borrower.delete()
    return JsonResponse({'success': True})


@login_required
@require_http_methods(["POST"])
def update_payment(request, borrower_id):
    """Update payment for a specific date"""
    from datetime import datetime as dt
    borrower = get_object_or_404(Borrower, id=borrower_id, finance_group__user=request.user)
    
    try:
        data = json.loads(request.body)
        payment_date_str = data.get('date')  # ISO format string like '2026-06-02'
        amount = float(data.get('amount', 0))

        # Convert ISO string to date object
        payment_date = dt.fromisoformat(payment_date_str).date()

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
def update_borrower(request, borrower_id):
    """Update borrower name or amount given"""
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