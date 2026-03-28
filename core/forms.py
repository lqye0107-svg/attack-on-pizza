from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import PizzaSize, Topping

class RegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']


class PizzaCustomizeForm(forms.Form):
    size = forms.ModelChoiceField(
        queryset=PizzaSize.objects.none(),
        empty_label=None
    )
    toppings = forms.ModelMultipleChoiceField(
        queryset=Topping.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )
    quantity = forms.IntegerField(min_value=1, initial=1)

    def __init__(self, *args, pizza=None, **kwargs):
        super().__init__(*args, **kwargs)

        if pizza is not None:
            self.fields['size'].queryset = pizza.sizes.all()
            self.fields['toppings'].queryset = pizza.available_toppings.filter(is_available=True)