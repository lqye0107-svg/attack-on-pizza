from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('menu/', views.menu_view, name='menu'),
    path('register/', views.register_view, name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('pizza/<int:pizza_id>/', views.pizza_detail_view, name='pizza_detail'),
    path('cart/', views.cart_view, name='cart'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('order-success/<int:order_id>/', views.order_success_view, name='order_success'),
    path('drinks/<int:drink_id>/add/', views.add_drink_to_cart_view, name='add_drink_to_cart'),
    path('cart/remove/<int:item_index>/', views.remove_from_cart_view, name='remove_from_cart'),
    path('cart/increase/<int:item_index>/', views.increase_cart_item_view, name='increase_cart_item'),
    path('cart/decrease/<int:item_index>/', views.decrease_cart_item_view, name='decrease_cart_item'),
]