# -*- coding: utf-8 -*-
from django import forms
from apps.orders.models import Order

class RegistrationOrderForm(forms.ModelForm):
    note = forms.CharField(
        widget=forms.Textarea(),
        required=False
    )

    class Meta:
        model = Order
        exclude = ('create_date',)

    def clean(self):
        cleaned_data = super(RegistrationOrderForm, self).clean()
        order_carting = cleaned_data.get("order_carting")
        city = cleaned_data.get("city")
        address = cleaned_data.get("address")
        index = cleaned_data.get("index")

        if order_carting == 'country' and (city=='' and address=='' and index==''):
            raise forms.ValidationError("Обязательное поле.")

        return cleaned_data