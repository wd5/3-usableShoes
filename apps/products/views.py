# -*- coding: utf-8 -*-
import os, md5
from datetime import datetime, date, timedelta
from django.http import Http404, HttpResponse, HttpResponseBadRequest, HttpResponseRedirect, HttpResponseForbidden
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.views.generic.simple import direct_to_template

from django.views.generic import ListView, DetailView, DetailView, TemplateView, View

from models import Category, Product, Client

class ShowCatalogByTypeView(TemplateView):
    template_name = 'catalog.html'

    def get_context_data(self, **kwargs):
        context = super(ShowCatalogByTypeView, self).get_context_data(**kwargs)
        products = Product.objects.published()
        type = self.kwargs.get('type', None)
        if type == "all":
            context['catalog'] = products
        else:
            try:
                context['catalog'] = products.filter(trade_type=type)
            except:
                context['catalog'] = False

        return context

show_catalog_by_type = ShowCatalogByTypeView.as_view()


class ShowCategory(DetailView):
    model = Category
    context_object_name = 'category'
    template_name = 'products/show_category.html'

    def get_context_data(self, **kwargs):
        context = super(ShowCategory, self).get_context_data()
        products = self.object.get_products()
        s_type = self.kwargs.get('s_type', None)
        if s_type == 'all':
            pass
        else:
            products = products.filter(s_type=s_type)
        context['catalog'] = products
        sizes = []
        sizes_ids = []
        for product in products:
            for size in product.get_sizes():
                if size.id in sizes_ids:
                    pass
                else:
                    sizes.append({'id': size.id, 'value': size.value, })
                    sizes_ids.append(size.id)
                    #sizes = list(set(sizes))
        sizes.sort()
        setattr(self.object, 'sizes', sizes)
        return context

show_category = ShowCategory.as_view()

class ShowProduct(DetailView):
    model = Product
    context_object_name = 'product'
    template_name = 'products/show_product.html'

    def get_context_data(self, **kwargs):
        context = super(ShowProduct, self).get_context_data()
        context['attached_photos'] = self.object.get_photos()
        return context

show_product = ShowProduct.as_view()

class ProductsSearch(TemplateView):
    template_name = 'products/search_results.html'

    def get_context_data(self, **kwargs):
        context = super(ProductsSearch, self).get_context_data()
        products = Product.objects.published()
        try:
            q = self.request.GET['q']
        except:
            q = ''
        qs = products.filter(
            Q(title__icontains=q) |
            Q(description__icontains=q) |
            Q(material__icontains=q) |
            Q(art__icontains=q) |
            Q(price__icontains=q)
        )
        context['catalog'] = qs
        context['query'] = q
        return context

search_products = ProductsSearch.as_view()

class ClientsListView(ListView):
    model = Client
    context_object_name = 'clients'
    template_name = 'products/clients_list.html'
    queryset = Client.objects.published()

clients_list = ClientsListView.as_view()

class LoadCatalogView(View):
    def post(self, request, *args, **kwargs):
        if not request.is_ajax():
            return HttpResponseRedirect('/')
        else:
            if 'size' not in request.POST or 's_type' not in request.POST or 'id_cat' not in request.POST:
                return HttpResponseBadRequest()
            try:
                id_cat = int(request.POST['id_cat'])
            except:
                return HttpResponseBadRequest()

            try:
                curr_categ = Category.objects.get(id=id_cat)
            except Category.DoesNotExist:
                return HttpResponseBadRequest()

            products = curr_categ.get_products()
            size = request.POST['size']
            s_type = request.POST['s_type']
            if size != 'all':
                try:
                    size = int(size)
                except ValueError:
                    return HttpResponseBadRequest()
                if s_type == 'all':
                    queryset = products.filter(size__in=[size])
                else:
                    queryset = products.filter(s_type=s_type, size__in=[size])
            else:
                if s_type == 'all':
                    queryset = products
                else:
                    queryset = products.filter(s_type=s_type)

            items_html = render_to_string(
                'products/products_list.html',
                    {'catalog': queryset, 'request': request, }
            )
            return HttpResponse(items_html)

load_catalog = csrf_exempt(LoadCatalogView.as_view())