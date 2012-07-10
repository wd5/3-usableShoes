# -*- coding: utf-8 -*-
from django.contrib.auth.forms import AuthenticationForm
from django.core.urlresolvers import reverse

def authorization_form(request):

    authform = AuthenticationForm()
    next_url = reverse('show_cabinet')
#    if '/cabinet/' in next_url:
#        next_url = '/'

    return {
        'auth_form':authform,
        'next_url':next_url,
    }