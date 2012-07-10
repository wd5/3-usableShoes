# -*- coding: utf-8 -*-
from django import forms
from apps.spam.models import Email

class EmailForm(forms.ModelForm):
    email = forms.EmailField(
        widget=forms.TextInput(
            attrs={
                'required':'required',
            }
        ),
        required=True
    )

    class Meta:
        model = Email


