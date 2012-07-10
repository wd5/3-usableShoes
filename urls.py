from django.conf.urls.defaults import patterns, include, url

from django.contrib import admin
from django.contrib.auth.views import login,logout
from django.conf import settings

from apps.urls import urlpatterns as apps_urlpatterns


admin.autodiscover()

urlpatterns = patterns('',
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),

    # Admin
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin_tools/', include('admin_tools.urls')),

    url(r'^login/', login, {'redirect_field_name':'next','template_name':'auth_error.html'}, name='auth_login'),
    url(r'^logout/', logout, {'next_page':'/'}, name='auth_logout'),

     #Redactor
    (r'^upload_img/$', 'views.upload_img'),
    (r'^upload_file/$', 'views.upload_file'),

)

urlpatterns += apps_urlpatterns
