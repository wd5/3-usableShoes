# -*- coding: utf-8 -*-
import os
from django import http
from django.conf import settings
from django.views.generic.simple import direct_to_template
from pytils.translit import translify
from django.views.decorators.csrf import csrf_exempt
try:
    from PIL import Image
except ImportError:
    import Image
import md5
import datetime
from django.http import HttpResponseRedirect, HttpResponse

def handle_uploaded_file(f, filename, folder):
    name, ext = os.path.splitext(translify(filename).replace(' ', '_'))
    hashed_name=md5.md5(name+datetime.datetime.now().strftime("%Y%m%d%H%M%S")).hexdigest()
    path_name = settings.MEDIA_ROOT + '/uploads/' + folder + hashed_name + ext
    destination = open(path_name, 'wb+')

    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()
    return '/media/uploads/'+ folder + hashed_name + ext

@csrf_exempt
def upload_img(request):
    if request.user.is_staff:
        if request.method == 'POST':
            url = handle_uploaded_file(request.FILES['file'], request.FILES['file'].name, 'images/')

            #Resizing
            size = 650, 650
            im = Image.open(settings.ROOT_PATH + url)
            imageSize=im.size
            if (imageSize[0] > size[0]) or  (imageSize[1] > size[1]):
                im.thumbnail(size, Image.ANTIALIAS)
                im.save(settings.ROOT_PATH + url, "JPEG", quality = 100)
            return http.HttpResponse('<img src="%s"/>'%url)

        else:
            return http.HttpResponse('error')
    else:
        return http.HttpResponse('403 Forbidden. Authentication Required!')

@csrf_exempt
def upload_file(request):
    if request.user.is_staff:
        if request.method == 'POST':
            url = handle_uploaded_file(request.FILES['file'], request.FILES['file'].name, 'files/')
            url = '<a href="%s" target=_blank>%s</a>' % (url, request.FILES['file'].name)
            return http.HttpResponse(url)
    else:
        return http.HttpResponse('403 Forbidden. Authentication Required!')

'''
@csrf_exempt
def crop_image_view(request, id_image):
    next = request.REQUEST.get('next', None)
    if request.method != "POST":
        try:
            image = Members.objects.get(id=id_image).image
            return direct_to_template(request, 'crop_image.html', locals())
        except Members.DoesNotExist:
            return http.HttpResponseRedirect(next)
    else:
        x1 = int(request.POST['x1'])
        y1 = int(request.POST['y1'])
        x2 = int(request.POST['x2'])
        y2 = int(request.POST['y2'])
        box = (x1, y1, x2, y2)
        original_img = Members.objects.get(id=id_image)
        infile = settings.ROOT_PATH + original_img.image.url
        file, ext = os.path.splitext(infile)
        im = Image.open(infile)
        ms = im.crop(box)
        name = file + "_crop.jpg"
        ms.save(name, "JPEG")
        output_size = [76, 77]

        image = Image.open(name)
        m_width = float(output_size[0])
        m_height = float(output_size[1])
        w_k = image.size[0]/m_width
        h_k = image.size[1]/m_height
        if output_size < image.size:
            if w_k > h_k:
                new_size = (int(m_width), int(image.size[1]/w_k))
            else:
                new_size = (int(image.size[0]/h_k), int(m_height))
        else:
            new_size = image.size
        image = image.resize(new_size, Image.ANTIALIAS)
        image.save(name, "JPEG", quality=100)
        return http.HttpResponseRedirect(next)
'''
