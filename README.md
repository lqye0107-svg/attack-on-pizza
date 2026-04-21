# Attack on Pizza (AOP)

Attack on Pizza is a Django-based pizza take-out web application made for the course **ELE 3921 Web Applications Development**.

The project is inspired by anime style, especially *Attack on Titan*, and combines a themed visual design with a functional pizza ordering system.

## Project Features

This project currently includes:

- User registration, login, and logout
- Pizza menu with category sections:
  - Classic
  - Premium
  - Vegetable
- Drink menu
- Pizza detail page with:
  - size selection
  - topping selection
- Session-based shopping cart
- Cart item quantity increase and decrease
- Checkout page
- Order creation and order success page
- My Orders page
- Order Detail page
- Django admin for managing:
  - pizzas
  - drinks
  - toppings
  - pizza sizes
  - orders

## Technology

- Python
- Django
- HTML
- CSS
- SQLite

## How to Run the Project

python manage.py migrate
python manage.py loaddata menu_data.json
python manage.py createsuperuser
python manage.py runserver