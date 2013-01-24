$(function(){

    $('#carousel').jcarousel({
        wrap: 'circular',
        scroll: 1
    });

    $('.item_imgs_menu li').live('click',function(){
        var el = $(this)
        var link = el.find('div.replace_img a').clone()
        var rel = $('.item_img_zl a').attr('rel')
        el.parent().find('a').attr('rel',rel)
        el.find('div.replace_img a').removeAttr('rel')
        el.parent().find('li').removeClass('curr');
        el.toggleClass('curr');
        link.attr('rel',rel)
        $('.item_img_zl a').replaceWith(link)
        $('.item_img_zl').append('<script type="text/javascript">$(".fancybox").fancybox()</script>')
        return false;
    });

    $('.item_r .item_sizes li').live('click',function(){
        $(this).parent().find('li').removeClass('curr');
        $(this).toggleClass('curr');
        return false;
    });

    $('.order_menu li').live('click',function(){
        var curr_class = $(this).find('a').attr('class');
        $(this).parent().find('li').removeClass('curr');
        $(this).toggleClass('curr');

        $('#id_order_carting [value="'+curr_class+'"]').attr('selected','selected');

        var block_country = $('div.country');
        var block_moscow = $('div.moscow');

        if (curr_class=='moscow') {
            $('input[name="cart_submit"]').removeAttr('disabled');
            $('#id_address').val('');
            $('#id_city').val('Москва');
            $('.input_note').val('');
            block_moscow.prepend(block_country.find('.input_address'));
            block_moscow.append(block_country.find('.input_note'));
        }

        if (curr_class=='country') {

            $('#id_address').val('');
            $('#id_city').val('');
            EmsPrice($('#id_city').val());
            $('.input_note').val('');
            $('.input_index').after(block_moscow.find('.input_address'));
            block_country.append(block_moscow.find('.input_note'));
        }


        $('.contact_info').hide();
        $('div.'+curr_class).show();
        return false;
    });

    $('.ul_sizes li').live('click',function(){
        var el = $(this)
        var value = el.find('a').attr('name')
        var cat_id = $('#categ_id').val()
        el.parent().find('li').removeClass('curr');
        el.toggleClass('curr');
        $.ajax({
            url: "/load_catalog/",
            data: {
                size:value,
                id_cat:cat_id
            },
            type: "POST",
            success: function(data)
            {
                $('.items').replaceWith(data);
                $('.item_tocart').fancybox();

            }
        });
        return false;
    });

    $('.fancybox, .item_tocart').fancybox();

    $('#send_question').live('click',function(){
        $.ajax({
            url: "/faq/checkform/",
            data: {
                name:$('#id_name').val(),
                question:$('#id_question').val(),
                email:$('#id_email').val()
            },
            type: "POST",
            success: function(data) {
                if (data=='success')
                    {$('.faq_form').replaceWith("<div style='height: 150px;text-align: center;padding-top: 75px;'>Спасибо за вопрос, мы постараемся ответить на него в самое ближайшее время!</div>");}
                else{
                    $('.faq_form').replaceWith(data);
                }
            }
        });
        return false;
    });

    $('#send_review').live('click',function(){
        $.ajax({
            url: "/faq/checkreviewform/",
            data: {
                name:$('#id_name').val(),
                text:$('#id_text').val(),
                city:$('#id_city').val()
            },
            type: "POST",
            success: function(data) {
                if (data=='success')
                    {$('.faq_form').replaceWith("<div style='height: 150px;text-align: center;padding-top: 75px;'>Благодарим вас за отзыв для нашего сайта!</div>");}
                else{
                    $('.faq_form').replaceWith(data);
                }
            }
        });
        return false;
    });

    $('#add_subscr_email').live('click',function(){
        $.ajax({
            url: "/add_subscribe_email/",
            data: {
                email:$('#id_subscribe_email').val()
            },
            type: "POST",
            success: function(data) {
                if (data=='success')
                    {$('#id_subscribe_email').val('');
                    $('#fancybox-error').html('Вы успешно подписаны на рассылку.')}
                else
                    {$('#fancybox-error').html(data)}
            }
        });
        return false;
    });

    $('.load_items').live('click',function(){

        var el = $(this);
        var parent = $(this).parents('.load_block');
        $.ajax({
            url: "/load_items/",
            data: {
                load_ids: parent.find('#loaded_ids').val(),
                m_name: parent.find('#m_name').val(),
                a_name: parent.find('#a_name').val()
            },
            type: "POST",
            success: function(data) {

                parent.append(data)
                parent.find('.loaded:eq(0)').fadeIn("fast", function (){ //появление по очереди
                        $(this).next().fadeIn("fast", arguments.callee);
                    });
                //parent.find('.loaded').fadeIn('slow')  //простое появление
                parent.find('#loaded_ids').val(parent.find('#new_load_ids').val())
                parent.find('div').removeClass('loaded')
                parent.find('.more').appendTo(parent)
                var rctxt = parent.find('#remaining_count_text').val()
                var rc = parent.find('#remaining_count').val()
                if (rctxt!=undefined)
                    {el.html(rctxt)}
                if (rc<=0)
                    {parent.find('.more').remove()}
                parent.find('#remaining_count_text').remove()
                parent.find('#new_load_ids').remove()
                parent.find('#remaining_count').remove()

            }
        });

        return false;
    });

    //Анимация корзины при изменении
    function animate_cart(){

        $('.cartbox').animate({
                opacity: 0.25
            }, 200, function() {
                $(this).animate({
                    opacity: 1
                },200);
            }
        );

    }

    function create_img_fly(el)
    {
        var img = el.html();
        var offset = el.find('img').offset();
        element = "<div class='img_fly'>"+img+"</div>";
        $('body').append(element);
        $('.img_fly').css({
            'position': "absolute",
            'z-index': "1000",
            'left': offset.left,
            'top': offset.top
        });

    }

    //Добавление товара в корзину

    $('.buy_btn').live('click',function(){
        var product_id = $(this).attr('name');
        var pr_count = $('.cart_qty_btn').val();

         var parent_blk = $(this).parents('.parent_blk')

        if (product_id){
            $.ajax({
                type:'post',
                url:'/add_product_to_cart/',
                data:{
                    'product_id': product_id,
                    'count': pr_count,
                },
                success:function(data){
                    $.fancybox.close();
                    $('.img_fly').remove();
                    create_img_fly(parent_blk.find('.product_img'));

                    $('.cartbox').replaceWith(data);

                    var fly = $('.img_fly');
                    var left_end = $('.cartbox').offset().left;
                    var top_end = $('.cartbox').offset().top;

                    fly.animate(
                        {
                            left: left_end,
                            top: top_end
                        },
                        {
                            queue: false,
                            duration: 600,
                            easing: "swing"
                        }
                    ).fadeOut(600);

                    setTimeout(function(){
                        animate_cart();
                    } ,600);

                },
                error:function(jqXHR,textStatus,errorThrown){}
            });
        }

    });



/*
    $('.item_tocart').live('click',function(){
        var product_id = $(this).attr('name')
        var size_id = $('.item_sizes li[class="curr"]').find('a').attr('name')
        var parent_blk = $(this).parents('.parent_blk')

        if (!size_id)
            {size_id='empty'}

        if (product_id){
            $.ajax({
                type:'post',
                url:'/add_product_to_cart/',
                data:{
                    'product_id':product_id,
                    'size_id':size_id
                },
                success:function(data){
                    $('.img_fly').remove();
                    create_img_fly(parent_blk.find('.product_img'));

                    $('.cartbox').replaceWith(data);

                    var fly = $('.img_fly');
                    var left_end = $('.cartbox').offset().left;
                    var top_end = $('.cartbox').offset().top;

                    fly.animate(
                        {
                            left: left_end,
                            top: top_end
                        },
                        {
                            queue: false,
                            duration: 600,
                            easing: "swing"
                        }
                    ).fadeOut(600);

                    setTimeout(function(){
                        animate_cart();
                    } ,600);

                },
                error:function(jqXHR,textStatus,errorThrown){

                }
            });
        }

    });
*/
    $('.cart_qty_btn').live('click',function(){
        $('.cart_qty_btn').attr('disabled', true);
        $(this).attr('disabled', false);
        $(this).parents('.cart_qty').find('.cart_qty_modal').show();
        $(this).find('.cart_qty_modal_ok').attr('disabled', false);
        $('.cart_submit').attr('disabled', true);
        $('.cart_item_restore_btn').attr('disabled', true);
        $('.delete_cart_id').attr('disabled', true);
    });

    $('.cart_qty_modal_text').live('keypress',function(e){
        if(e.which == 13)
            $('.cart_qty_modal_ok').trigger("click");
        else
        if( e.which!=8 && e.which!=0 && (e.which<48 || e.which>57))
        {
            alert("Только цифры");
            return false;
        }
    });

    //Подсчёт стоимости
    $('.cart_qty_modal_text').live('keyup',function(){
        var el = $(this)
        var count = el.val();
        if (count){
            count = parseInt(count);
            if (count==0){
                $('.cart_qty_modal_text').val('1');
                count = 1;
            }
            if (count > 999){
                $('.cart_qty_modal_text').val('999');
                count = 999;
            }

            var product_price = el.parent().find('.cart_qty_price span').html().replace(' ','');

            product_price = parseFloat(product_price);

            var sum = product_price*count;
            if ((sum % 1)==0){
                sum = sum.toFixed(0);
            }
            else{
                sum = sum.toFixed(2);
            }
            el.parent().find('.cart_qty_total_price span').text(sum);
        }
    });

        //Кнопка Созранить в изменении количества в корзине
    $('.cart .cart_qty_modal_ok').live('click', function(){
        var el = $(this);
        var parent = el.parents('.cart_qty_modal');
        var cart_item = el.parents('.cart_item');
        var initial_count = parent.find('.initial_count').val();
        var new_count = parent.find('.cart_qty_modal_text').val();
        var cart_product_id = parent.find('.cart_qty_item_id').val();

        if (new_count && cart_product_id && initial_count){
            if (new_count != initial_count){
                $.ajax({
                    type:'post',
                    url:'/change_cart_product_count/',
                    data:{
                        'cart_product_id':cart_product_id,
                        'new_count':new_count
                    },
                    success:function(data){
                        data = eval('(' + data + ')');
                        cart_item.find('.cart_price .item_price').html(data.tr_str_total+" <span>руб.</span>");
                        cart_item.find('.cart_qty_btn').val(new_count);
                        parent.find('.initial_count').val(new_count);
                        parent.find('.cart_qty_modal_text').val(new_count);
                        parent.find('.cart_qty_total_price span').text(data.tr_str_total);
                        $('.cart_total .item_price').html(data.cart_str_total+" <span>руб.</span>");

                        $('.cart_submit').attr('disabled', false);
                        $('.cart_qty_btn').attr('disabled', false);
                        $('.cart_item_restore_btn').attr('disabled', false);
                        parent.hide();
                    },
                    error:function(data){
                        $('.cart_submit').attr('disabled', false);
                        $('.cart_qty_btn').attr('disabled', false);
                        $('.cart_item_restore_btn').attr('disabled', false);
                    }
                });
            }

        }
        return false;

    });

        //Кнопка Созранить в изменении количества у товара
    $('.item_page .cart_qty_modal_ok').live('click', function(){
        var el = $(this);
        var parent = el.parents('.cart_qty_modal');
        var new_count = parent.find('.cart_qty_modal_text').val();
        var new_total = parent.find('.cart_qty_total_price span').html();
        $('.cart_qty_btn').val(new_count);
        $('.item_cart_price div').html(new_total);
        parent.hide();
        return false;

    });

    $('.cart_qty_modal_cancel').live('click', function(){
        var el = $(this)
        var parent = el.parents('.cart_qty_modal')
        parent.hide();
        parent.find('.cart_qty_modal_ok').attr('disabled', true);
        $('.cart_submit').attr('disabled', false);
        $('.cart_qty_btn').attr('disabled', false);
        $('.cart_item_restore_btn').attr('disabled', false);
    });

    $('.delete_cart_id').live('click', function(){
        var el = $(this);
        var cart_product_id = el.attr('rel');
        var parent = el.parents('.cart_item');
        if (cart_product_id){
            $.ajax({
                type:'post',
                url:'/delete_product_from_cart/',
                data:{
                    'cart_product_id':cart_product_id
                },
                success:function(data){
                    data = eval('(' + data + ')');
                    $('.cart_total .item_price').html(data.cart_total+" <span>руб.</span>");
                    parent.addClass('cart_item_deleted')
                    parent.find('.cart_item_restore_fade').show()
                    //parent.appendTo(".load_blk")
                },
                error:function(data){
                }
            });
        }
        return false;
    });

    $('.cart_item_restore_btn').live('click', function(){
        var el = $(this);
        var cart_product_id = el.attr('name');
        var parent = el.parents('.cart_item');
        if (cart_product_id){
            $.ajax({
                type:'post',
                url:'/restore_product_to_cart/',
                data:{
                    'cart_product_id':cart_product_id
                },
                success:function(data){
                    data = eval('(' + data + ')');
                    $('.cart_total .item_price').html(data.cart_total+" <span>руб.</span>");
                    parent.removeClass('cart_item_deleted')
                    parent.find('.cart_item_restore_fade').hide()
                },
                error:function(data){
                }
            });
        }
        return false;
    });

    $('.cart_add_other').live('click', function(){
        var el = $(this);
        var cart_product_id = el.find('a').attr('rel');
        var parent = el.parents('.cart_item');
        if (cart_product_id){
            $.ajax({
                type:'post',
                url:'/add_same_product_to_cart/',
                data:{
                    'cart_product_id':cart_product_id
                },
                success:function(data){
                    parent.after(data);
                    $('.cart_total .item_price').html($('#cart_str_total').val()+" <span>руб.</span>");
                    $('#cart_str_total').remove();
                    $('.loaded').show('slow');
                    $('.loaded').removeClass('loaded');
                },
                error:function(data){
                }
            });
        }
        return false;
    });

    function log( message ) {
        $( "<div/>" ).text( message ).prependTo( "#log" );
        $( "#log" ).scrollTop( 0 );
    }

    $('#id_city').autocomplete({
        source: "/search_ems_city/",
        minLength: 1,
        select: function( event, ui ) {
            log( ui.item ?
                "Selected: " + ui.item.value + " aka " + ui.item.id :
                "Nothing selected, input was " + this.value );
            EmsPrice(ui.item.value);
            $('#id_address').focus();
        },
        change: function( event, ui ) {
            EmsPrice($(this).val());
        }
    });

});

// вычисления по EMS
function EmsPrice(city){
    $.ajax({
        url: "/ems_calculate/",
        data: {
            city: city
        },
        type: "POST",
        beforeSend: function ( xhr ) {
            if ($('.country .ems_div').is(':hidden')) {
            } else {
                $('.country .ems_price').html('<img src="/media/img/ajax-loader.gif">');
            }
        },
        success: function(data)
        {
            if (data=="NotFound"){
                $('.country .ems_div').html('Неверно выбран город').show();
                $('input[name="cart_submit"]').attr('disabled', 'disabled');
            } else {
                $('.country .ems_div').html('Доставка: <span class="ems_price"></span> руб.').show();
                $('.country .ems_price').html(data);
                $('input[name="cart_submit"]').removeAttr('disabled');
            }
        },
        error:function(jqXHR,textStatus,errorThrown){
            $('.country .ems_div').hide();
            $('input[name="cart_submit"]').attr('disabled', 'disabled');
        }
    });
}
