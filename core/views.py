from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required


def home(request):
    # If already logged in, go to dashboard. Else go to login.
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
            login(request, user)           # auto login after signup
            return redirect('dashboard')
    else:
        form = UserCreationForm()

    return render(request, 'registration/signup.html', {'form': form})


@login_required                            # if not logged in, sends to /login/
def dashboard(request):
    # Sample finance groups - later we will load these from database
    finance_groups = [
        {
            'name': 'Vizag Finance',
            'day': 'Sunday',
            'location': 'Vizag',
            'total_borrowers': 12,
            'total_given': 108000,
            'pending_emis': 3,
            'color': 'blue',
        },
        {
            'name': 'Eluru Finance',
            'day': 'Monday',
            'location': 'Eluru',
            'total_borrowers': 8,
            'total_given': 72000,
            'pending_emis': 1,
            'color': 'green',
        },
    ]
    return render(request, 'core/dashboard.html', {
        'finance_groups': finance_groups,
        'user': request.user,
    })