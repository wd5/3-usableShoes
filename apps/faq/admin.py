﻿# -*- coding: utf-8 -*-
from django.contrib import admin
from models import Question, Review#,QuestionCategory


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id','pub_date','name','email', 'is_published',)
    list_display_links = ('id','pub_date',)
    list_editable = ('is_published',)
    search_fields = ('name','email', 'question', 'answer',)
    list_filter = ('pub_date','is_published',)

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id','pub_date','name','city', 'is_published',)
    list_display_links = ('id','pub_date','name','city',)
    list_editable = ('is_published',)
    search_fields = ('name','city', 'text',)
    list_filter = ('pub_date','is_published',)

#class QuestionCategoryAdmin(admin.ModelAdmin):
#    list_display = ('title', 'order','is_published',)
#    list_display_links = ('title',)
#    list_editable = ('order','is_published',)

admin.site.register(Question, QuestionAdmin)
admin.site.register(Review, ReviewAdmin)
#admin.site.register(QuestionCategory, QuestionCategoryAdmin)