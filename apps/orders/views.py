# -*- coding: utf-8 -*-
import datetime, urllib, json, settings
from django.core.mail.message import EmailMessage
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views.generic import FormView, DetailView, TemplateView, View
from apps.orders.models import Cart, CartProduct, Order, OrderProduct, EmsCity
from apps.orders.forms import RegistrationOrderForm
from apps.products.models import Product, Size
from apps.users.models import Profile
from apps.users.forms import RegistrationForm
from apps.pages.models import Page
from apps.siteblocks.models import Settings
from django.core.urlresolvers import reverse
from apps.orders.forms import RegistrationOrderForm
from pytils.numeral import choose_plural

class ViewCart(TemplateView):
    template_name = 'orders/cart_detail.html'

    def get_context_data(self, **kwargs):
        context = super(ViewCart, self).get_context_data()

        cookies = self.request.COOKIES

        cookies_cart_id = False
        if 'shoes_cart_id' in cookies:
            cookies_cart_id = cookies['shoes_cart_id']

        if self.request.user.is_authenticated and self.request.user.id:
            profile_id = self.request.user.profile.id
        else:
            profile_id = False

        sessionid = self.request.session.session_key

        try:
            if profile_id:
                cart = Cart.objects.get(profile=profile_id)
            elif cookies_cart_id:
                cart = Cart.objects.get(id=cookies_cart_id)
            else:
                cart = Cart.objects.get(sessionid=sessionid)
            cart_id = cart.id
        except Cart.DoesNotExist:
            cart = False
            cart_id = False

        is_empty = True
        if cart:
            cart_products = cart.get_products_all()
        else:
            cart_products = False

        cart_str_total = u''
        if cart_products:
            is_empty = False
            cart_str_total = cart.get_str_total()

        context['is_empty'] = is_empty
        context['cart_products'] = cart_products
        context['cart_str_total'] = cart_str_total
        context['cart_id'] = cart_id
        return context

view_cart = ViewCart.as_view()

class OrderFromView(FormView):
    form_class = RegistrationOrderForm
    template_name = 'orders/order_form.html'

    def post(self, request, *args, **kwargs):
        try:
            carting_price_moscow = Settings.objects.get(name='moscow_carting_price')
        except:
            carting_price_moscow = False
        try:
            page_selfcarting = Page.objects.get(id=13)
        except:
            page_selfcarting = False

        response = HttpResponse()
        badresponse = HttpResponseBadRequest()
        cookies = self.request.COOKIES
        cookies_cart_id = False
        if 'shoes_cart_id' in cookies:
            cookies_cart_id = cookies['shoes_cart_id']

        if self.request.user.is_authenticated and self.request.user.id:
            profile_id = self.request.user.profile.id
        else:
            profile_id = False

        if profile_id:
            try:
                profile = Profile.objects.get(pk=int(profile_id))
            except:
                profile = False
        else:
            profile = False

        sessionid = self.request.session.session_key

        try:
            if profile_id:
                cart = Cart.objects.get(profile=profile_id)
            elif cookies_cart_id:
                cart = Cart.objects.get(id=cookies_cart_id)
            else:
                cart = Cart.objects.get(sessionid=sessionid)
        except Cart.DoesNotExist:
            cart = False

        if not cart:
            return HttpResponseRedirect('/cart/')

        cart_products = cart.get_products()
        cart_products_count = cart_products.count()

        if not cart_products_count:
            return HttpResponseRedirect('/cart/')

        data = request.POST.copy()
        order_form = RegistrationOrderForm(data)
        if order_form.is_valid():
            new_order = order_form.save()

            for cart_product in cart_products:
                OrderProduct.objects.create(
                    order=new_order,
                    count=cart_product.count,
                    product=cart_product.product,
                )

            if profile:
                profile.name = new_order.first_name
                profile.last_name = new_order.last_name
                profile.phone = new_order.phone
                profile.city = new_order.city
                profile.address = new_order.address
                profile.index = new_order.index
                profile.note = new_order.note
                profile.save()

            cart.delete() #Очистка и удаление корзины
            response.delete_cookie('shoes_cart_id') # todo: ???

            subject = u'Практичная обувь - Информация по заказу.'
            subject = u''.join(subject.splitlines())
            message = render_to_string(
                'orders/message_template.html',
                    {
                    'order': new_order,
                    'products': new_order.get_products()
                }
            )

            try:
                emailto = Settings.objects.get(name='workemail').value
            except Settings.DoesNotExist:
                emailto = False

            if emailto and new_order.email:
                msg = EmailMessage(subject, message, settings.DEFAULT_FROM_EMAIL, [emailto, new_order.email])
                msg.content_subtype = "html"
                msg.send()

            if not profile_id:
                reg_form = RegistrationForm(initial={'email': new_order.email, })
            else:
                reg_form = False
            return render_to_response('orders/order_form_final.html',
                    {'order': new_order, 'request': request, 'user': request.user,
                     'reg_form': reg_form, })
        else:
            return render_to_response(self.template_name,
                    {'order_form': order_form, 'request': request, 'user': request.user,
                     'page_selfcarting': page_selfcarting, 'carting_price_moscow': carting_price_moscow, })

    def get(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        context = self.get_context_data(**kwargs)
        context['order_form'] = form

        if self.request.user.is_authenticated and self.request.user.id:
            profile_id = self.request.user.profile.id
            try:
                profile_set = Profile.objects.filter(id=self.request.user.profile.id)
                profile = Profile.objects.get(pk=int(profile_id))
                context['order_form'].fields['profile'].queryset = profile_set
                context['order_form'].fields['profile'].initial = profile
                context['order_form'].fields['first_name'].initial = profile.name
                context['order_form'].fields['last_name'].initial = profile.last_name
                context['order_form'].fields['email'].initial = profile.user.email
                context['order_form'].fields['phone'].initial = profile.phone
                context['order_form'].fields['order_carting'].initial = u'country'
                context['order_form'].fields['order_status'].initial = u'processed'
                context['order_form'].fields['city'].initial = profile.city
                context['order_form'].fields['address'].initial = profile.address
                context['order_form'].fields['index'].initial = profile.index
                context['order_form'].fields['note'].initial = profile.note
            except Profile.DoesNotExist:
                return HttpResponseBadRequest()
        else:
            context['order_form'].fields['profile'].queryset = Profile.objects.extra(where=['1=0'])
            context['order_form'].fields['order_carting'].initial = u'country'
            context['order_form'].fields['order_status'].initial = u'processed'

        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(OrderFromView, self).get_context_data()
        try:
            context['carting_price_moscow'] = Settings.objects.get(name='moscow_carting_price')
        except:
            context['carting_price_moscow'] = False
        try:
            context['page_selfcarting'] = Page.objects.get(id=13)
        except:
            context['page_selfcarting'] = False

        return context

show_order_form = csrf_protect(OrderFromView.as_view())

show_finish_form = csrf_protect(OrderFromView.as_view())

class AddProdictToCartView(View):
    def post(self, request, *args, **kwargs):
        if not request.is_ajax():
            return HttpResponseRedirect('/')
        else:
            if 'product_id' not in request.POST and 'count' not in request.POST:
                return HttpResponseBadRequest()
            else:
                product_id = request.POST['product_id']
                try:
                    product_id = int(product_id)
                except ValueError:
                    return HttpResponseBadRequest()
                count = request.POST['count']
                try:
                    count = int(count)
                except ValueError:
                    return HttpResponseBadRequest()

            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return HttpResponseBadRequest()

            cookies = request.COOKIES
            response = HttpResponse()

            cookies_cart_id = False
            if 'shoes_cart_id' in cookies:
                cookies_cart_id = cookies['shoes_cart_id']

            if request.user.is_authenticated and request.user.id:
                profile_id = request.user.profile.id
                try:
                    profile = Profile.objects.get(pk=int(profile_id))
                except:
                    profile = False
            else:
                profile_id = False
                profile = False

            sessionid = request.session.session_key

            if profile_id:
                try:
                    cart = Cart.objects.get(profile=profile_id)
                except Cart.DoesNotExist:
                    if cookies_cart_id:
                        try:
                            cart = Cart.objects.get(id=cookies_cart_id)
                            if cart.profile:
                                if profile:
                                    cart = Cart.objects.create(profile=profile)
                                else:
                                    return HttpResponseBadRequest()
                            else:
                                if profile:
                                    cart.profile = profile
                                    cart.save()
                                else:
                                    return HttpResponseBadRequest()
                        except:
                            if profile:
                                cart = Cart.objects.create(profile=profile)
                            else:
                                return HttpResponseBadRequest()
                    else:
                        cart = Cart.objects.create(profile=profile)
                response.set_cookie('shoes_cart_id', cart.id, 1209600)
                #if cookies_cart_id: response.delete_cookie('shoes_cart_id')
            elif cookies_cart_id:
                try:
                    cart = Cart.objects.get(id=cookies_cart_id)
                except Cart.DoesNotExist:
                    cart = Cart.objects.create(sessionid=sessionid)
                response.set_cookie('shoes_cart_id', cart.id, 1209600)
            else:
                try:
                    cart = Cart.objects.get(sessionid=sessionid)
                except Cart.DoesNotExist:
                    cart = Cart.objects.create(sessionid=sessionid)
                response.set_cookie('shoes_cart_id', cart.id, 1209600)

            try:
                cart_product = CartProduct.objects.get(
                    cart=cart,
                    product=product,
                    count=count,
                )
                if cart_product.is_deleted:
                    cart_product.is_deleted = False
                else:
                    cart_product.count += 1
                cart_product.save()
            except CartProduct.DoesNotExist:
                CartProduct.objects.create(
                    cart=cart,
                    product=product,
                    count=count,
                )
            is_empty = True
            cart_products_count = cart.get_products_count()
            cart_total = cart.get_str_total()
            cart_products_text = u''
            if cart_products_count:
                is_empty = False
                cart_products_text = u'короб%s' % (choose_plural(cart_products_count, (u'ка', u'ки', u'ок')))

            cart_html = render_to_string(
                'orders/block_cart.html',
                    {
                    'is_empty': is_empty,
                    'cart_products_count': cart_products_count,
                    'cart_total': cart_total,
                    'cart_products_text': cart_products_text
                }
            )
            response.content = cart_html
            return response

add_product_to_cart = csrf_exempt(AddProdictToCartView.as_view())

class ShowModalToCartView(View):
    def get(self, request, *args, **kwargs):
        if not request.is_ajax():
            return HttpResponseRedirect('/')
        else:
            if 'product_id' not in request.GET:
                return HttpResponseBadRequest()
            else:
                product_id = request.GET['product_id']
                try:
                    product_id = int(product_id)
                except ValueError:
                    return HttpResponseBadRequest()

            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return HttpResponseBadRequest()

            html = render_to_string(
                'orders/block_modal_to_cart.html',
                    {
                    'product': product,
                }
            )
            response = HttpResponse()
            response.content = html
            return response

show_modal_to_cart = csrf_exempt(ShowModalToCartView.as_view())

class DeleteProductFromCart(View):
    def post(self, request, *args, **kwargs):
        if not request.is_ajax():
            return HttpResponseRedirect('/')
        else:
            if 'cart_product_id' not in request.POST:
                return HttpResponseBadRequest()
            else:
                cart_product_id = request.POST['cart_product_id']
                try:
                    cart_product_id = int(cart_product_id)
                except ValueError:
                    return HttpResponseBadRequest()

            try:
                cart_product = CartProduct.objects.get(id=cart_product_id)
            except CartProduct.DoesNotExist:
                return HttpResponseBadRequest()

            cart_product.is_deleted = True
            cart_product.save()

            response = HttpResponse()

            cart_products_count = cart_product.cart.get_products_count()
            cart_total = u''
            if cart_products_count:
                cart_total = cart_product.cart.get_str_total()
            data = u'''{"cart_total":'%s'}''' % cart_total
            response.content = data
            return response

delete_product_from_cart = csrf_exempt(DeleteProductFromCart.as_view())

class RestoreProductToCart(View):
    def post(self, request, *args, **kwargs):
        if not request.is_ajax():
            return HttpResponseRedirect('/')
        else:
            if 'cart_product_id' not in request.POST:
                return HttpResponseBadRequest()
            else:
                cart_product_id = request.POST['cart_product_id']
                try:
                    cart_product_id = int(cart_product_id)
                except ValueError:
                    return HttpResponseBadRequest()

            try:
                cart_product = CartProduct.objects.get(id=cart_product_id)
            except CartProduct.DoesNotExist:
                return HttpResponseBadRequest()

            cart_product.is_deleted = False
            cart_product.save()

            response = HttpResponse()

            cart_products_count = cart_product.cart.get_products_count()
            cart_total = u''
            if cart_products_count:
                cart_total = cart_product.cart.get_str_total()
            data = u'''{"cart_total":'%s'}''' % cart_total
            response.content = data
            return response

restore_product_to_cart = csrf_exempt(RestoreProductToCart.as_view())

class ChangeCartCountView(View):
    def post(self, request, *args, **kwargs):
        if not request.is_ajax():
            return HttpResponseRedirect('/')
        else:
            if 'cart_product_id' not in request.POST or 'new_count' not in request.POST:
                return HttpResponseBadRequest()

            cart_product_id = request.POST['cart_product_id']
            try:
                cart_product_id = int(cart_product_id)
            except ValueError:
                return HttpResponseBadRequest()

            new_count = request.POST['new_count']
            try:
                new_count = int(new_count)
            except ValueError:
                return HttpResponseBadRequest()

            try:
                cart_product = CartProduct.objects.get(id=cart_product_id)
            except CartProduct.DoesNotExist:
                return HttpResponseBadRequest()

            cart_product.count = new_count
            cart_product.save()
            cart_str_total = cart_product.cart.get_str_total()

            data = u'''{"tr_str_total":'%s', "cart_str_total":'%s'}''' % (cart_product.get_str_total(), cart_str_total)

            return HttpResponse(data)

change_cart_product_count = csrf_exempt(ChangeCartCountView.as_view())

class AddSameProductView(View):
    def post(self, request, *args, **kwargs):
        if not request.is_ajax():
            return HttpResponseRedirect('/')
        else:
            if 'cart_product_id' not in request.POST:
                return HttpResponseBadRequest()

            cart_product_id = request.POST['cart_product_id']
            try:
                cart_product_id = int(cart_product_id)
            except ValueError:
                return HttpResponseBadRequest()

            try:
                cart_product = CartProduct.objects.get(id=cart_product_id)
            except CartProduct.DoesNotExist:
                return HttpResponseBadRequest()

            size = cart_product.product.get_sizes()[0]

            new_product = CartProduct.objects.create(
                cart=cart_product.cart,
                product=cart_product.product,
            )

            cart_str_total = new_product.cart.get_str_total()
            cart_product_html = render_to_string(
                'orders/cart_item.html',
                    {
                    'cart_item': new_product,
                    'loaded': True,
                    'cart_str_total': cart_str_total,
                    }
            )
            return HttpResponse(cart_product_html)

add_same_product_to_cart = csrf_exempt(AddSameProductView.as_view())

class EmsCalculateView(View):
    def post(self, request, *args, **kwargs):
        if not request.is_ajax():
            return HttpResponseRedirect('/')
        else:
#            data = urllib.urlopen('http://emspost.ru/api/rest/?method=ems.get.locations&type=cities&plain=true')
#            json_cities = json.load(data)
#            for item in json_cities["rsp"]["locations"]:
#                record = EmsCity(value=item["value"], name=item["name"])
#                record.save()
#            return HttpResponseBadRequest()

            if 'city' not in request.POST:
                return HttpResponseBadRequest()

            city = request.POST['city']

            if city == '':
                return HttpResponseBadRequest()

            cookies = request.COOKIES
            cookies_cart_id = False
            if 'shoes_cart_id' in cookies:
                cookies_cart_id = cookies['shoes_cart_id']

            if self.request.user.is_authenticated and self.request.user.id:
                profile_id = self.request.user.profile.id
            else:
                profile_id = False

            sessionid = self.request.session.session_key

            try:
                if profile_id:
                    cart = Cart.objects.get(profile=profile_id)
                elif cookies_cart_id:
                    cart = Cart.objects.get(id=cookies_cart_id)
                else:
                    cart = Cart.objects.get(sessionid=sessionid)
            except Cart.DoesNotExist:
                cart = False

            if cart:
                try:
                    ems_city = EmsCity.objects.get(name__iexact=city)
                except:
                    ems_city = False
                if ems_city:
                    city_code = ems_city.value # из москвы!
                    carting_price_data = urllib.urlopen(
                        'http://emspost.ru/api/rest?method=ems.calculate&from=city--moskva&to=%s&weight=%s' % (
                            city_code, cart.get_products_count()))
                    json_data = json.load(carting_price_data)
                    return HttpResponse(json_data["rsp"]["price"])
                else: # не нашли город
                    return HttpResponse('NotFound')
            else:
                return HttpResponseBadRequest()

ems_calculate = csrf_exempt(EmsCalculateView.as_view())

class EmsSearch(View):
    def get(self, request, *args, **kwargs):
        if not request.is_ajax():
            return HttpResponseRedirect('/')
        else:
            if 'term' not in request.GET:
                return HttpResponseBadRequest()

            term = request.GET['term']

            ems_cities = EmsCity.objects.filter(name__istartswith=term)
            response_data = []
            if ems_cities:
                for city in ems_cities:
                    response_data.append(city.name.title())
                return HttpResponse(json.dumps(response_data), mimetype="application/json")
            else: # не нашли город
                return HttpResponse('NotFound')

search_ems_city = csrf_exempt(EmsSearch.as_view())