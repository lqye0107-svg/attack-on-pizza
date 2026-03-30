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
        empty_label=None,
        widget=forms.RadioSelect
    )
    toppings = forms.ModelMultipleChoiceField(
        queryset=Topping.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    def __init__(self, *args, pizza=None, **kwargs):
        super().__init__(*args, **kwargs)

        if pizza is not None:
            size_qs = pizza.sizes.all()
            topping_qs = pizza.available_toppings.filter(is_available=True)

            self.fields['size'].queryset = size_qs
            self.fields['toppings'].queryset = topping_qs

            self.fields['size'].label_from_instance = (
                lambda obj: f"{obj.get_size_display()} ({obj.price})"
            )

            def topping_label(obj):
                return obj.name

            self.fields['toppings'].label_from_instance = topping_label