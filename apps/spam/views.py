# -*- coding: utf-8 -*-
import datetime, settings
from django.http import HttpResponseRedirect, HttpResponse, Http404, HttpResponseBadRequest
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, FormView, DetailView, ListView, View

from apps.spam.forms import EmailForm
from apps.spam.models import Email
from apps.products.models import Product

class AddSubscribeView(View):
    def post(self, request, *args, **kwargs):
        if request.is_ajax():
            data = request.POST.copy()
            email_form = EmailForm(data)
            if email_form.is_valid():
                email_form.save()
                return HttpResponse('success')
            else:
                return HttpResponse('Для подписки на рассылку введите верный электронный адрес.')
        else:
            return HttpResponseBadRequest()

add_subscribe = csrf_exempt(AddSubscribeView.as_view())

class CancelSubscribeView(TemplateView):
    template_name = 'pages/subscr_cancel.html'

    def get_context_data(self, **kwargs):
        context = super(CancelSubscribeView, self).get_context_data(**kwargs)
        context['catalog'] = Product.objects.published()

        email = self.kwargs.get('email', None)
        if email:
            try:
                item = Email.objects.get(email=email)
            except:
                item = False
            if item:
                item.delete()
                context['system_text'] = 'Подписка на рассылку успешно отменена.'
            else:
                self.template_name = 'catalog.html'
        else:
            self.template_name = 'catalog.html'

        return context

cancel_subscribe = CancelSubscribeView.as_view()