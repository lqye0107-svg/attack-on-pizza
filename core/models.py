from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Topping(models.Model):
    name = models.CharField(max_length=100, unique=True)
    price_small = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    price_medium = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    price_large = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Pizza(models.Model):
    CATEGORY_CHOICES = [
        ('CLASSIC', 'Classic'),
        ('PREMIUM', 'Premium'),
        ('VEGETABLE', 'Vegetable'),
    ]

    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='CLASSIC'
    )
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='pizzas/', blank=True, null=True)
    is_available = models.BooleanField(default=True)
    available_toppings = models.ManyToManyField(Topping, blank=True, related_name='pizzas')

    def __str__(self):
        return self.name


class PizzaSize(models.Model):
    SIZE_CHOICES = [
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
    ]

    pizza = models.ForeignKey(Pizza, on_delete=models.CASCADE, related_name='sizes')
    size = models.CharField(max_length=1, choices=SIZE_CHOICES)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        unique_together = ('pizza', 'size')

    def __str__(self):
        return f"{self.pizza.name} - {self.get_size_display()}"


class Drink(models.Model):
    name = models.CharField(max_length=100)
    size_label = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='drinks/', blank=True, null=True)
    is_available = models.BooleanField(default=True)

    class Meta:
        unique_together = ('name', 'size_label')

    def __str__(self):
        return f"{self.name} {self.size_label}"


class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PREPARING', 'Preparing'),
        ('READY', 'Ready'),
        ('COMPLETED', 'Completed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    total_price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    delivery_address = models.CharField(max_length=255)

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"


class OrderItem(models.Model):
    ITEM_TYPE_CHOICES = [
        ('pizza', 'Pizza'),
        ('drink', 'Drink'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    item_type = models.CharField(max_length=10, choices=ITEM_TYPE_CHOICES)
    name_snapshot = models.CharField(max_length=100)
    size_snapshot = models.CharField(max_length=50, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    toppings_snapshot = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name_snapshot} x {self.quantity}"
    
