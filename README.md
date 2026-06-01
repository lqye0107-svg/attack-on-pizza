# Attack on Pizza (AOP)

Attack on Pizza is a simple Django-based pizza ordering website made for the course **ELE 3921 Web Applications Development**.

The website allows users to order pizza online and choose delivery. It does not include a pickup option. The idea of the project is to combine a basic online ordering system with an anime-inspired visual style, especially inspired by *Attack on Titan*.

## Project Features

The project includes:

- User registration, login, and logout
- Pizza menu
- Drink menu
- Pizza detail page
- Pizza size selection
- Topping selection
- Shopping cart using session
- Increase and decrease item quantity in the cart
- Checkout page with delivery address
- Order success page
- My Orders page
- Order detail page
- Django admin page for managing menu items and orders

## Technology Used

- Python
- Django
- HTML
- CSS
- SQLite

## Models and Pages

This project uses Django’s built-in User model and six custom models.

The custom models are:

**Topping**: stores topping names, different prices for each pizza size, and availability.
**Pizza**: stores pizza name, category, description, image, availability, and available toppings.
**PizzaSize**: stores the size and price for each pizza.
**Drink**: stores drink name, size, price, image, and availability.
**Order**: stores customer order information, including user, order status, total price, and delivery address.
**OrderItem**: stores each item inside an order, such as pizzas and drinks.

These models are connected to support the full ordering process, from browsing the menu to placing an order.

The project also includes 10 main HTML templates:

**base.html**: the main layout template. It includes the navbar, CSS link, message display area, and the main content block.
**home.html**: the homepage of the website.
**menu.html**: shows pizza categories and drinks.
**pizza_detail.html**: allows users to choose pizza size and toppings.
**cart.html**: shows the shopping cart and item quantities.
**checkout.html**: allows users to enter a delivery address and place an order.
**order_success.html**: shows confirmation after an order is placed.
**my_orders.html**: shows the user’s previous orders.
**order_detail.html**: shows details of a selected order.
**register.html**: allows new users to create an account.
**login.html**: allows users to log in.

The pages are connected through Django views and URL patterns to create a simple online pizza ordering system with delivery.