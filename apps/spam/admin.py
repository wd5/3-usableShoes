# -*- coding: utf-8 -*-
from _socket import error
from django.contrib.sites.models import Site
from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib import admin
from django import forms
from django.forms.models import save_instance
from django.contrib.auth.models import User
from apps.utils.widgets import Redactor

from apps.spam.models import Mailer, Email

class ModelAdminForm(forms.ModelForm):
    text= forms.CharField(widget=Redactor(attrs={'cols': 140, 'rows': 25}))
    text.label = u'Текст'

    class Meta:
        model = Mailer

    def save(self, commit=True):
        """
        Saves this ``form``'s cleaned_data into model instance
        ``self.instance``.

        If commit=True, then the changes to ``instance`` will be saved to the
        database. Returns ``instance``.
        """
        if self.instance.pk is None:
            fail_message = 'created'
        else:
            fail_message = 'changed'

        data = self.data
        send = True
        try:
            ADMIN_EMAIL = data['ADMIN_EMAIL']
        except KeyError:
            send = False
        if send:
            current_site = Site.objects.get_current()

            emails = []
            if '_test' in data:
                subject = data['name']
                subject = u'%s - Тестовая рассылка "%s".' %(current_site.name, subject)
                subject = u''.join(subject.splitlines())

                message = data['text']
                emails.append(ADMIN_EMAIL)

            elif '_send' in data:
                subject = data['name']
                subject = u'%s - "%s".' %(current_site,subject)
                subject = u''.join(subject.splitlines())

                message = u'%s <hr /><p>Практичная обувь <a href="http://%s">«Практичная обувь»</a>' % (data['text'], current_site.domain)

                emails_list = Email.objects.all()
                emails =[]
                for e in emails_list:
                    emails.append(e.email)

            else:
                send = False

            from_email = u'«Практичная обувь» <no-reply@%s>' % current_site.domain
            if send:
                for email in emails:
                    message_extend = u'%s (Для того чтобы отписаться от рассылки перейдите по данной ссылке: <a href="http://%s/cancel_subscribe/%s/">Отменить рассылку</a>)' % (message, current_site.domain, email)
                    msg = EmailMessage(subject, message_extend, from_email, [email])
                    msg.content_subtype = "html"

                    try:
                        msg.send()
                    except error:
                        pass

        instance = save_instance(self, self.instance, self._meta.fields,
                             fail_message, commit, construct=False)
        return instance

    save.alters_data = True

class MailerAdmin(admin.ModelAdmin):
    list_display = ('id','name','pub_date',)
    list_display_links = ('id','name',)
    search_fields = ('name','text',)
    list_filter = ('pub_date',)
    form = ModelAdminForm

admin.site.register(Mailer, MailerAdmin)

class EmailAdmin(admin.ModelAdmin):
    list_display = ('id','email',)
    list_display_links = ('id','email',)
    search_fields = ('email',)
    readonly_fields = ('email',)

admin.site.register(Email, EmailAdmin)