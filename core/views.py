from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from .forms import RegisterForm, PizzaCustomizeForm, CheckoutForm
from .models import Pizza, Drink, Order, OrderItem


def home_view(request):
    return render(request, 'core/home.html')


def menu_view(request):
    classic_pizzas = Pizza.objects.filter(
        is_available=True,
        category='CLASSIC'
    ).prefetch_related('sizes')

    premium_pizzas = Pizza.objects.filter(
        is_available=True,
        category='PREMIUM'
    ).prefetch_related('sizes')

    vegetable_pizzas = Pizza.objects.filter(
        is_available=True,
        category='VEGETABLE'
    ).prefetch_related('sizes')

    drinks = Drink.objects.filter(is_available=True)

    context = {
        'classic_pizzas': classic_pizzas,
        'premium_pizzas': premium_pizzas,
        'vegetable_pizzas': vegetable_pizzas,
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


def calculate_cart_total(cart):
    total = Decimal('0.00')

    for item in cart:
        unit_price = Decimal(str(item.get('unit_price', '0.00')))
        quantity = int(item.get('quantity', 1))
        total += unit_price * quantity

    return total


@login_required
def checkout_view(request):
    cart = request.session.get('cart', [])

    if not cart:
        messages.warning(request, 'Your cart is empty. Please add items before checkout.')
        return redirect('cart')

    cart_total = calculate_cart_total(cart)

    if request.method == 'POST':
        form = CheckoutForm(request.POST)

        if form.is_valid():
            delivery_address = form.cleaned_data['delivery_address']

            order = Order.objects.create(
                user=request.user,
                delivery_address=delivery_address,
                total_price=cart_total,
                status='PENDING'
            )

            for item in cart:
                item_type = item.get('item_type')
                name_snapshot = item.get('name', '')
                size_snapshot = item.get('size_label', '')
                quantity = int(item.get('quantity', 1))
                unit_price = Decimal(str(item.get('unit_price', '0.00')))

                toppings_snapshot = ''
                if item_type == 'pizza':
                    topping_names = item.get('topping_names', [])
                    toppings_snapshot = ', '.join(topping_names)

                OrderItem.objects.create(
                    order=order,
                    item_type=item_type,
                    name_snapshot=name_snapshot,
                    size_snapshot=size_snapshot,
                    quantity=quantity,
                    unit_price=unit_price,
                    toppings_snapshot=toppings_snapshot
                )

            request.session['cart'] = []
            request.session.modified = True

            messages.success(request, 'Your order has been placed successfully.')
            return redirect('order_success', order_id=order.id)

    else:
        form = CheckoutForm()

    cart_items = []

    for index, item in enumerate(cart):
        item_type = item.get('item_type')

        if item_type == 'pizza':
            cart_item = {
                'index': index,
                'item_type': 'pizza',
                'name': item.get('name', 'Pizza'),
                'size_label': item.get('size_label', ''),
                'topping_names': item.get('topping_names', []),
                'quantity': int(item.get('quantity', 1)),
            }
        elif item_type == 'drink':
            cart_item = {
                'index': index,
                'item_type': 'drink',
                'name': item.get('name', 'Drink'),
                'size_label': item.get('size_label', ''),
                'quantity': int(item.get('quantity', 1)),
            }
        else:
            continue

        cart_items.append(cart_item)

    context = {
        'form': form,
        'cart_items': cart_items,
        'cart_total': cart_total,
    }
    return render(request, 'core/checkout.html', context)


@login_required
def order_success_view(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    user_order_ids = list(
        Order.objects.filter(user=request.user)
        .order_by('created_at', 'id')
        .values_list('id', flat=True)
    )

    order_display_number = user_order_ids.index(order.id) + 1

    context = {
        'order': order,
        'order_display_number': order_display_number,
    }
    return render(request, 'core/order_success.html', context)


@login_required
@login_required
def my_orders_view(request):
    orders = list(
        Order.objects.filter(user=request.user)
        .prefetch_related('items')
        .order_by('-created_at')
    )

    user_order_ids = list(
        Order.objects.filter(user=request.user)
        .order_by('created_at', 'id')
        .values_list('id', flat=True)
    )

    order_number_map = {
        order_id: index + 1
        for index, order_id in enumerate(user_order_ids)
    }

    for order in orders:
        order.display_number = order_number_map.get(order.id)

    context = {
        'orders': orders,
    }
    return render(request, 'core/my_orders.html', context)


@login_required
def order_detail_view(request, order_id):
    order = get_object_or_404(
        Order.objects.prefetch_related('items'),
        id=order_id,
        user=request.user
    )

    user_order_ids = list(
        Order.objects.filter(user=request.user)
        .order_by('created_at', 'id')
        .values_list('id', flat=True)
    )

    order_display_number = user_order_ids.index(order.id) + 1

    context = {
        'order': order,
        'items': order.items.all(),
        'order_display_number': order_display_number,
    }
    return render(request, 'core/order_detail.html', context)


def cart_view(request):
    cart = request.session.get('cart', [])
    cart_items = []
    cart_total = calculate_cart_total(cart)

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