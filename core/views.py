from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from .forms import RegisterForm, PizzaCustomizeForm
from .models import Pizza, Drink


def home_view(request):
    return render(request, 'core/home.html')


def menu_view(request):
    pizzas = Pizza.objects.filter(is_available=True).prefetch_related('sizes')
    drinks = Drink.objects.filter(is_available=True)

    context = {
        'pizzas': pizzas,
        'drinks': drinks,
    }
    return render(request, 'core/menu.html', context)


def register_view(request):
    if request.user.is_authenticated:
        return redirect('menu')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful. Welcome to Attack on Pizza!')
            return redirect('menu')
    else:
        form = RegisterForm()

    return render(request, 'core/register.html', {'form': form})


class CustomLoginView(LoginView):
    template_name = 'core/login.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('menu')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, 'You have logged in successfully.')
        return super().form_valid(form)


class CustomLogoutView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        messages.success(request, 'You have logged out successfully.')
        return super().dispatch(request, *args, **kwargs)
    

def pizza_detail_view(request, pizza_id):
    pizza = get_object_or_404(
        Pizza.objects.prefetch_related('sizes', 'available_toppings'),
        id=pizza_id,
        is_available=True
    )

    if request.method == 'POST':
        form = PizzaCustomizeForm(request.POST, pizza=pizza)
        if form.is_valid():
            selected_size = form.cleaned_data['size']
            selected_toppings = form.cleaned_data['toppings']
            quantity = form.cleaned_data['quantity']

            toppings_names = [t.name for t in selected_toppings]

            messages.success(
                request,
                f'Pizza selected: {pizza.name}, size: {selected_size.get_size_display()}, '
                f'toppings: {", ".join(toppings_names) if toppings_names else "None"}, '
                f'quantity: {quantity}'
            )
            return redirect('pizza_detail', pizza_id=pizza.id)
    else:
        form = PizzaCustomizeForm(pizza=pizza)

    context = {
        'pizza': pizza,
        'form': form,
    }
    return render(request, 'core/pizza_detail.html', context)