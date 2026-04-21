from django.contrib import admin
from .models import Topping, Pizza, PizzaSize, Drink, Order, OrderItem

# Register your models here.
@admin.register(Topping)
class ToppingAdmin(admin.ModelAdmin):
    list_display = ('name', 'price_small', 'price_medium', 'price_large', 'is_available')
    list_filter = ('is_available',)
    search_fields = ('name',)

class PizzaSizeInline(admin.TabularInline):
    model = PizzaSize
    extra = 1

@admin.register(Pizza)
class PizzaAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'is_available')
    list_filter = ('category', 'is_available')
    search_fields = ('name',)
    filter_horizontal = ('available_toppings',)
    inlines = [PizzaSizeInline]

@admin.register(Drink)
class DrinkAdmin(admin.ModelAdmin):
    list_display = ('name', 'size_label', 'price', 'is_available')
    list_filter = ('is_available',)
    search_fields = ('name',)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('item_type', 'name_snapshot', 'size_snapshot', 'quantity', 'unit_price', 'toppings_snapshot')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'status', 'total_price')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'user__email')
    inlines = [OrderItemInline]