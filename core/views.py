from decimal import Decimal
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

    available_toppings = pizza.available_toppings.filter(is_available=True)

    if request.method == 'POST':
        form = PizzaCustomizeForm(request.POST, pizza=pizza)
        if form.is_valid():
            selected_size = form.cleaned_data['size']
            selected_toppings = form.cleaned_data['toppings']

            size_code = selected_size.size
            base_price = selected_size.price
            topping_total = Decimal('0.00')

            topping_names = []
            topping_ids = []

            for topping in selected_toppings:
                topping_names.append(topping.name)
                topping_ids.append(topping.id)

                if size_code == 'S':
                    topping_total += topping.price_small
                elif size_code == 'M':
                    topping_total += topping.price_medium
                elif size_code == 'L':
                    topping_total += topping.price_large

            unit_price = base_price + topping_total

            cart = request.session.get('cart', [])

            cart_item = {
                'item_type': 'pizza',
                'item_id': pizza.id,
                'name': pizza.name,
                'size_id': selected_size.id,
                'size_label': selected_size.get_size_display(),
                'topping_ids': topping_ids,
                'topping_names': topping_names,
                'quantity': 1,
                'unit_price': str(unit_price),
            }

            cart.append(cart_item)
            request.session['cart'] = cart
            request.session.modified = True

            messages.success(
                request,
                f'{pizza.name} ({selected_size.get_size_display()}) added to cart.'
            )
            return redirect('pizza_detail', pizza_id=pizza.id)
    else:
        form = PizzaCustomizeForm(pizza=pizza)

    context = {
        'pizza': pizza,
        'form': form,
        'available_toppings': available_toppings,
    }
    return render(request, 'core/pizza_detail.html', context)


def add_drink_to_cart_view(request, drink_id):
    drink = get_object_or_404(Drink, id=drink_id, is_available=True)

    cart = request.session.get('cart', [])

    cart_item = {
        'item_type': 'drink',
        'item_id': drink.id,
        'name': drink.name,
        'size_label': drink.size_label,
        'quantity': 1,
        'unit_price': str(drink.price),
    }

    cart.append(cart_item)
    request.session['cart'] = cart
    request.session.modified = True

    messages.success(request, f'{drink.name} ({drink.size_label}) added to cart.')
    return redirect('menu')


def cart_view(request):
    cart = request.session.get('cart', [])
    cart_items = []
    cart_total = Decimal('0.00')

    for index, item in enumerate(cart):
        unit_price = Decimal(str(item.get('unit_price', '0.00')))
        quantity = int(item.get('quantity', 1))
        subtotal = unit_price * quantity

        item_type = item.get('item_type')

        if not item_type:
            if 'pizza_name' in item:
                item_type = 'pizza'
            elif 'name' in item and 'pizza_name' not in item:
                item_type = 'drink'

        if item_type == 'pizza':
            cart_item = {
                'index': index,
                'item_type': 'pizza',
                'name': item.get('name', item.get('pizza_name', 'Pizza')),
                'size_label': item.get('size_label', ''),
                'topping_names': item.get('topping_names', []),
                'quantity': quantity,
            }

        elif item_type == 'drink':
            cart_item = {
                'index': index,
                'item_type': 'drink',
                'name': item.get('name', 'Drink'),
                'size_label': item.get('size_label', ''),
                'quantity': quantity,
            }

        else:
            continue

        cart_items.append(cart_item)
        cart_total += subtotal

    context = {
        'cart_items': cart_items,
        'cart_total': cart_total,
    }
    return render(request, 'core/cart.html', context)

def remove_from_cart_view(request, item_index):
    cart = request.session.get('cart', [])

    if 0 <= item_index < len(cart):
        removed_item = cart.pop(item_index)
        request.session['cart'] = cart
        request.session.modified = True

        item_name = removed_item.get('name', 'Item')
        messages.success(request, f'{item_name} removed from cart.')

    return redirect('cart')

def increase_cart_item_view(request, item_index):
    cart = request.session.get('cart', [])

    if 0 <= item_index < len(cart):
        cart[item_index]['quantity'] = int(cart[item_index].get('quantity', 1)) + 1
        request.session['cart'] = cart
        request.session.modified = True

    return redirect('cart')


def decrease_cart_item_view(request, item_index):
    cart = request.session.get('cart', [])

    if 0 <= item_index < len(cart):
        current_quantity = int(cart[item_index].get('quantity', 1))

        if current_quantity > 1:
            cart[item_index]['quantity'] = current_quantity - 1
        else:
            cart.pop(item_index)

        request.session['cart'] = cart
        request.session.modified = True

    return redirect('cart')