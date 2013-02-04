# -*- coding: utf-8 -*-
import os, md5
from datetime import datetime, date, timedelta
from django.http import Http404, HttpResponse, HttpResponseBadRequest, HttpResponseRedirect, HttpResponseForbidden
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.views.generic.simple import direct_to_template

from django.views.generic import ListView, DetailView, DetailView, TemplateView, View
from apps.pages.models import Page

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

        context['catalog'] = products
        sizes = []
        sizes_ids = []
        for product in products:
            for size in product.get_sizes():
                if size.id in sizes_ids:
                    pass
                else:
                    sizes.append({'id': size.id, 'value': size.value,})
                    sizes_ids.append(size.id)
                    #sizes = list(set(sizes))
        #sizes.sort()
        sizes = sorted(sizes, key=lambda k: k['value'])
        setattr(self.object, 'sizes', sizes)
        return context

show_category = ShowCategory.as_view()

class ShowProduct(DetailView):
    model = Product
    context_object_name = 'product'
    template_name = 'products/show_product.html'

    def get_context_data(self, **kwargs):
        context = super(ShowProduct, self).get_context_data()
        cat_slug = self.kwargs.get('slug', None)
        try:
            category = self.object.category.get(slug=cat_slug)
            cat_products = category.get_products()
        except:
            category = False
        context['category'] = category
        context['attached_photos'] = self.object.get_photos()
        product_price = self.object.price
        great_pp = product_price + 100
        less_pp = product_price - 100
        # похожие товары
        related_products_list = []
        related_products = self.object.get_related_products()
        if related_products:
            rp_count = related_products.count()
            if rp_count<4:
                remaining_count = 4 - rp_count
                for item in related_products:
                    related_products_list.append(item)
                related_products_next_part = Product.objects.filter(is_published=True, category=category, price__gte=less_pp, price__lte=great_pp).exclude(id__in=related_products.values("id")).order_by('?')[:remaining_count]
                for item in related_products_next_part:
                    related_products_list.append(item)
                related_products = related_products_list
            else:
                pass
        else:
            if category:
                related_products = Product.objects.filter(is_published=True, category=category, price__gte=less_pp, price__lte=great_pp).exclude(id=self.object.id).order_by('?')[:4]
        context['product_related_products'] = related_products
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
            if 'size' not in request.POST or 'id_cat' not in request.POST:
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
            if size != 'all':
                try:
                    size = int(size)
                except ValueError:
                    return HttpResponseBadRequest()
                queryset = products.filter(size__in=[size])
            else:
                queryset = products

            items_html = render_to_string(
                'products/products_list.html',
                    {'catalog': queryset, 'request': request, }
            )
            return HttpResponse(items_html)

load_catalog = csrf_exempt(LoadCatalogView.as_view())

class ShowOptListView(TemplateView):
    template_name = 'products/opt_list.html'

    def get_context_data(self, **kwargs):
        context = super(ShowOptListView, self).get_context_data(**kwargs)
        products = Product.objects.published()
        try:
            page = Page.objects.get(url='/opt/')
        except:
            page = False
        context['catalog'] = products.filter(category__target__is_opt=True)
        context['page'] = page
        return context

opt_list = ShowOptListView.as_view()
