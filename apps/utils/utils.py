# -*- coding: utf-8 -*-
import os
from django.core.mail import EmailMultiAlternatives
from django.contrib.sites.models import Site
from django.http import HttpResponse
from apps.siteblocks.models import Settings
from django.template.loader import get_template
from django.template import Context
import xhtml2pdf.pisa as pisa
import settings

def url_spliter(url,cut_count):
    url = url.split('/')
    current = ''
    counter = 0
    if len(url)>1:
        for part in url[1:]:
            counter = counter + 1
            if cut_count==False:
                current = '%s/%s' % (current,part)
            else:
                if counter <= cut_count:
                    current = '%s/%s' % (current,part)
                else:
                    pass
    else:
        current = u'/'

    if not current.startswith('/'):
        current = '/%s' % current
    if not current.endswith('/'):
        current = '%s/' % current
    current = current.replace('//,', '/')

    return current

def random_key(length=6, allowed_chars='abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789'):
    from random import choice
    return ''.join([choice(allowed_chars) for i in range(length)])

def send_order_email(subject, html_content, email_list, file):
    current_site = Site.objects.get_current()

    email_from = u'«3DX Moscow Open» <reply@%s>' % current_site.domain
    text_content = u''

    if email_list:
        msg = EmailMultiAlternatives(subject, text_content, email_from, email_list)
        msg.attach_alternative(html_content, "text/html")
        msg.attach_file(file, mimetype="application/pdf")
        msg.send()

def render_to_pdf(template_src, id_guest, context_dict):
    from cStringIO import StringIO
    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=somefilename.pdf'
    template = get_template(template_src)
    context = Context(context_dict)
    html = template.render(context)
    result = StringIO()

    file_name = 'guest_%s.pdf' % id_guest
    path_name = settings.MEDIA_ROOT + 'uploads/files/guests/' + file_name
    destination = open(path_name, 'wb+')

    pdf = pisa.pisaDocument(StringIO(html.encode("utf-8")), result, show_error_as_pdf=True, encoding='utf-8', )

    destination.write(result.getvalue())
    destination.close()
    return u'%s' % path_name


def send_emails(m, file):
    admin_email = Settings.objects.get(name = 'email_notification').value
    email_list = [u'%s' % admin_email,]
    subject = u'Новый зарегистрированный гость'
    html_content = u'''
        <p style="font-size: 12px;">Здравствуйте.<br /><br />Новый зарегистрированный гость.</p>
        <p style="padding-left: 10px; font-style: italic; font-size: 12px;
        border-left: 2px solid #666;">
        <b>Номер п/п:</b> %s<br />
        <b>ФИО:</b> %s<br />
        <b>E-mail:</b> %s<br />
        <b>Телефон:</b> %s<br />
        <b>Уникальный ключ:</b> %s</p>
        <p><a href="http://3dxopen.ru/admin/members/guests/%s/">перейти к просмотру</a></p>''' % \
           (m.id, m.name, m.email, m.phone, m.key, m.id)

    send_order_email(subject, html_content, email_list, file)

    email_list = [u'%s' % m.email,]
    subject = u'Приглашение на 3DX Moscow Open'
    html_content = u'''
        <p style="font-size: 12px;">Здравствуйте.<br /><br />Пропуск успешно выписан(см. прикрепления).</p>
        <p style="padding-left: 10px; font-style: italic; font-size: 12px;
        border-left: 2px solid #666;">
        <b>Номер п/п:</b> %s<br />
        <b>ФИО:</b> %s<br />
        <b>E-mail:</b> %s<br />
        <b>Телефон:</b> %s<br /></p>''' % \
           (m.id, m.name, m.email, m.phone)

    send_order_email(subject, html_content, email_list, file)
