# -*- coding: utf-8 -*-
from django.contrib import admin

from apps.slider.models import Slider
from sorl.thumbnail.admin import AdminImageMixin
from apps.utils.widgets import AdminImageCrop
from django import forms

class SliderAdminForm(forms.ModelForm):
    image = forms.ImageField(
    	widget=AdminImageCrop(attrs={'path': 'slider/photo'}), 
    	label=u'Изображение'
    )
    model = Slider

class SliderAdmin(AdminImageMixin, admin.ModelAdmin):
    list_display = ('title','admin_photo_preview','order','is_published',)
    list_display_links = ('title', 'admin_photo_preview',)
    list_editable = ('order','is_published',)
    list_filter = ('is_published',)
    form = SliderAdminForm
    
admin.site.register(Slider, SliderAdmin)