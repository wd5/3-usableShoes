# -*- coding: utf-8 -*-
from django import forms
from apps.faq.models import Question, Review

class QuestionForm(forms.ModelForm):
    email = forms.EmailField(
        widget=forms.TextInput(
            attrs={
                'required':'required',
            }
        ),
        required=True
    )
    name = forms.CharField(
        required=False
    )
    question = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'required':'required',
            }
        ),
        required=True
    )

    class Meta:
        model = Question
        fields = ('name', 'email', 'question',)

class ReviewForm(forms.ModelForm):
    city = forms.CharField(
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
                'required':'required',
            }
        ),
        required=True
    )
    text = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'required':'required',
            }
        ),
        required=True
    )

    class Meta:
        model = Review
        fields = ('name', 'city', 'text',)


