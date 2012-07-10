# -*- coding: utf-8 -*-
import datetime, settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import FormView, DetailView, TemplateView, View
from apps.users.forms import ProfileForm, RegistrationForm
from apps.users.models import Profile
from apps.orders.models import Order
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.contrib.auth import logout as auth_logout, authenticate as auth_check, login as auth_login

def send_email_registration(username, password, to_email):
    from django.core.mail import send_mail

    subject = u'Регистрация на сайте – %s' % settings.SITE_NAME
    # Email subject *must not* contain newlines
    subject = ''.join(subject.splitlines())

    message = render_to_string('users/registration_email.txt',
            {
            'username': username,
            'password': password,
            'SITE_NAME': settings.SITE_NAME
        })

    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [to_email])


class RegistrationFormView(FormView):
    form_class = RegistrationForm
    template_name = 'users/registration.html'

    def post(self, request, *args, **kwargs):
        data = request.POST.copy()
        data['username'] = data['email']
        reg_form = RegistrationForm(data)
        if reg_form.is_valid():
            new_user = User.objects.create(username=data['username'], email=data['email'])
            new_user.set_password(data['password1'])
            new_user.save()

            profile = Profile.objects.create(user=new_user, name=u'', last_name=u'')

            send_email_registration(username=new_user.username, password=data['password1'], to_email=new_user.email)

            user = auth_check(username=request.POST['email'], password=request.POST['password1'])
            if data['order_id']:
                try:
                    order = Order.objects.get(id=int(data['order_id']))
                except:
                    order = False

                if order:
                    order.profile = profile
                    order.save()

            if user is not None:
                auth_login(request, user)
                return HttpResponseRedirect('/cabinet/')
            return HttpResponseRedirect('/catalog/')
        else:
            return render_to_response('users/registration.html',
                    {'reg_form': reg_form, 'request': request, 'user': request.user})

    def get(self, request, **kwargs):
        if self.request.user.is_authenticated and self.request.user.id:
            return HttpResponseRedirect(reverse('index'))
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(RegistrationFormView, self).get_context_data()
        context['reg_form'] = self.form_class()
        return context

registration_form = RegistrationFormView.as_view()

class ShowProfileForm(FormView):
    form_class = ProfileForm
    template_name = 'users/profile_form.html'

    def get(self, request, **kwargs):
        if self.request.user.is_authenticated and self.request.user.id:
            pass
        else:
            return HttpResponseRedirect(reverse('index'))
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(ShowProfileForm, self).get_context_data()
        if self.request.user.is_authenticated and self.request.user.id:
            context['profile_form'] = self.form_class(initial={'id': self.request.user.profile.id,
                                                               'name': self.request.user.profile.name,
                                                               'last_name': self.request.user.profile.last_name,
                                                               'user__email': self.request.user.email,
                                                               'phone': self.request.user.profile.phone})
        return context

show_profile_form = ShowProfileForm.as_view()

class ShowCabinetView(TemplateView):
    template_name = 'users/show_cabinet.html'

    def get(self, request, **kwargs):
        if self.request.user.is_authenticated and self.request.user.id:
            pass
        else:
            return HttpResponseRedirect(reverse('index'))
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(ShowCabinetView, self).get_context_data()
        if self.request.user.is_authenticated and self.request.user.id:
            try:
                profile = Profile.objects.get(id=self.request.user.profile.id)
            except:
                profile = False
            if profile:
                context['orders']=profile.get_orders()
        return context

show_cabinet = ShowCabinetView.as_view()

class EditUsrInfoView(View):
    def post(self, request, *args, **kwargs):
        data = request.POST.copy()
        profiles = Profile.objects.all()
        try:
            profile = Profile.objects.get(pk=int(data['id']))
        except:
            profile = False

        if profile:
            profile_form = ProfileForm(data, instance=profile)
            if profile_form.is_valid():
                profile_form.save()
                try:
                    user = User.objects.get(id=int(profile.user.id))
                    user.email = data['user__email']
                    if not request.user.is_superuser:
                        user.username = data['user__email']
                    user.save()
                except:
                    return HttpResponseRedirect('/cabinet/')
                return HttpResponseRedirect('/cabinet/')
            else:
                return render_to_response('users/profile_form.html',
                        {'profile_form': profile_form, 'request': request, 'user': request.user})
        else:
            errors = u'Произошла внутренняя ошибка. Не верный идентификатор пользователя.'
            return render_to_response('users/profile_form.html', {'errors': errors, 'request': request, })

edt_profile_info = csrf_exempt(EditUsrInfoView.as_view())