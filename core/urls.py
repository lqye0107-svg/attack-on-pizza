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
    path('drinks/<int:drink_id>/add/', views.add_drink_to_cart_view, name='add_drink_to_cart'),
    path('cart/remove/<int:item_index>/', views.remove_from_cart_view, name='remove_from_cart'),
]