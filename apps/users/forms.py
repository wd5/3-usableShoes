# -*- coding: utf-8 -*-
from django import forms
from apps.users.models import Profile
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

attrs_dict = { 'class': 'required', 'required': True }


class ProfileForm(forms.ModelForm):
    id = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'required':'required',
            }
        ),
        required=True
    )
    name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                #'required':'required',
            }
        ),
        required=True
    )
    last_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
               # 'required':'required',
            }
        ),
        required=True
    )
    user__email = forms.EmailField(
        widget=forms.TextInput(
            attrs={
                #'required':'required',
            }
        ),
        required=True
    )
    phone = forms.CharField(
        widget=forms.TextInput(
            attrs={
                #'required':'required',
            }
        ),
        required=False
    )

    class Meta:
        model = Profile
        fields = ('id', 'name', 'last_name', 'user__email', 'phone',)

class RegistrationForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs=attrs_dict), label=_(u'username'))
    email = forms.EmailField(widget=forms.TextInput(attrs=dict(attrs_dict,
                maxlength=75)), label=_(u'email address'))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict, render_value=False),
                label=_(u'password'))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict, render_value=False),
                label=_(u'password (again)'))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', )

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 != password2:
            raise forms.ValidationError("Повторите пароль верно.")

        return cleaned_data