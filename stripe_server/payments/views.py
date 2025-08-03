from django.shortcuts import get_object_or_404
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import stripe
from .models import Item, Order, OrderItem, Discount, Tax
from .serializers import ItemSerializer, OrderSerializer

def get_or_create_order(request):
    """
    Создает новый заказ, если он не существует, и сохраняет его в сессии.
    Возвращает существующий заказ, если он уже есть в сессии.
    """
    order_id = request.session.get('order_id')
    if order_id:
        try:
            return Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            pass
    order = Order.objects.create()
    request.session['order_id'] = order.id
    return order

def get_order_currency(order):
    """
    Возвращает валюту первого товара в заказе.
    Если заказ пуст, возвращает 'usd' по умолчанию.
    """
    order_items = order.orderitem_set.all()
    if order_items.exists():
        return order_items.first().item.currency
    return 'usd'

class ListItemAPIView(ListAPIView):
    """
    Возвращает список всех товаров.
    """
    queryset = Item.objects.all()
    renderer_classes = [TemplateHTMLRenderer]
    serializer_class = ItemSerializer
    permission_classes = [AllowAny]
    template_name = 'list.html'

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'object_list': serializer.data
        })

class OrderAPIView(APIView):
    """
    Возвращает текущий заказ(корзину) пользователя.
    Если заказ(корзина) не существует, создает новый.
    """
    renderer_classes=[TemplateHTMLRenderer]
    permission_classes=[AllowAny]
    template_name='order.html'
    def get(self, request):
        order = get_or_create_order(request)
        currency = get_order_currency(order)
        serializer = OrderSerializer(order)
        return Response({
            'order': serializer.data,
            'STRIPE_PUBLIC_KEY': settings.STRIPE_KEYS[currency]['public']
        })

class AddToOrderAPIView(APIView):
    """
    Добавляет товар в текущий заказ(корзину).
    Если товар уже есть в заказе(корзине), увеличивает его количество.
    Если заказа(корзины) нет, создает новый.
    Если товар с другой валютой, возвращает ошибку.
    """
    permission_classes=[AllowAny]
    renderer_classes=[TemplateHTMLRenderer]
    template_name='add_to_order.html'
    def post(self, request, item_id):
        item = get_object_or_404(Item, id=item_id)
        order = get_or_create_order(request)
        order_items = order.orderitem_set.all()
        for order_item in order_items:
            if order_item.item.currency != item.currency:
                return Response({
                    'error': 'Невозможно добавить товар с другой валютой в текущий заказ'
                }, status=400)
        order_item, created = OrderItem.objects.get_or_create(
            order=order,
            item=item,
            defaults={'quantity': 1}
        )
        if not created:
            order_item.quantity += 1
            order_item.save()
        return Response({
            'message': 'Предмет успешно добавлен в корзину'
        })
    
class ClearOrderAPIView(APIView):
    """
    Очищает текущий заказ(корзину) пользователя.
    Если заказа(корзины) нет, возвращает сообщение об этом.
    """
    permission_classes = [AllowAny]
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'clear_order.html'
    def post(self, request):
        if 'order_id' in request.session:
            order = Order.objects.filter(pk = request.session['order_id'])
            order.delete()
            del request.session['order_id']
            return Response({
                'message': 'Корзина успешно очищена'
            })
        else:
            return Response({
                'message': 'У вас пока нет корзины'
            })

class AddDiscountAPIView(APIView):
    """
    Добавляет скидку(купон) к текущему заказу(корзине).
    Если скидка уже есть в заказе(корзине), ничего не делает.
    Если заказа(корзины) нет, создает новый.
    """
    permission_classes = [AllowAny]
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'add_discount.html'
    def get(self, request):
        return Response({
            'message': 'Введите название скидки(купона) для добавления к заказу'
        })
    def post(self, request):
        order = get_or_create_order(request)
        discount_name = request.data.get('discount_name')
        discount = get_object_or_404(Discount, name=discount_name)
        if discount.currency != get_order_currency(order):
            return Response({
                'error': 'Невозможно добавить скидку с другой валютой в текущий заказ'
            }, status=400)
        order.discount = discount
        order.save()
        return Response({
            'message': f'Скидка {discount.name} успешно добавлена к заказу'
        })

class AddTaxAPIView(APIView):
    """
    Добавляет налог к текущему заказу(корзине).
    Если налог уже есть в заказе(корзине), ничего не делает.
    Если заказа(корзины) нет, создает новый.
    """
    permission_classes = [AllowAny]
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'add_tax.html'
    def get(self, request):
        return Response({
            'message': 'Введите название налога'
        })
    def post(self, request):
        order = get_or_create_order(request)
        tax_name = request.data.get('tax_name')
        tax = get_object_or_404(Tax, name=tax_name)
        if tax.currency != get_order_currency(order):
            return Response({
                'error': 'Невозможно добавить налог с другой валютой в текущий заказ'
            }, status=400)
        order.tax = tax
        order.save()
        return Response({
            'message': f'Налог {tax.name} успешно добавлен к заказу'
        })

class ItemAPIView(APIView):
    """
    Возвращает информацию о товаре по его ID и публичный ключ Stripe.
    Если товар не найден, возвращает 404 ошибку.
    """
    renderer_classes=[TemplateHTMLRenderer]
    permission_classes=[AllowAny]
    template_name='item.html'
    def get(self, request, id):
        item = get_object_or_404(Item, pk=id)
        serializer = ItemSerializer(item)
        return Response({
            'item': serializer.data,
            'STRIPE_PUBLIC_KEY': settings.STRIPE_KEYS[item.currency]['public'],
        })

class BuyAPIView(APIView):
    """
    Создает сессию Stripe Checkout для покупки товара по его ID.
    Возвращает ID сессии, который используется для перенаправления пользователя на страницу оплаты.
    Если товар не найден, возвращает 404 ошибку.
    Если возникает ошибка при создании сессии, возвращает сообщение об ошибке.
    """
    permission_classes=[AllowAny]
    def get(self, request, id):
        item = get_object_or_404(Item, pk=id)
        try:
            stripe.api_key = settings.STRIPE_KEYS[item.currency]['secret']
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        'price_data': {
                            'currency': item.currency,
                            'unit_amount': item.price,
                            'product_data': {
                                'name': item.name,
                                'description': item.description,
                            },
                        },
                        'quantity': 1,
                    }
                ],
                mode='payment',
                success_url=settings.SITE_URL + '/success/',
                cancel_url=settings.SITE_URL + '/cancel/',
            )
            return Response({'id': checkout_session.id})
        except Exception as e:
            return Response({'error': str(e)}, status=500)

class BuyIntentAPIView(APIView):
    """
    Создает платежное намерение для покупки товара по его ID.
    Возвращает client_secret платежного намерения, который используется для подтверждения оплаты на клиенте.
    Если товар не найден, возвращает 404 ошибку.
    Если возникает ошибка при создании платежного намерения, возвращает сообщение об ошибке.
    """
    permission_classes=[AllowAny]
    renderer_classes=[JSONRenderer]
    def get(self, request, item_id):
        item = get_object_or_404(Item, pk=item_id)
        try:
            stripe.api_key = settings.STRIPE_KEYS[item.currency]['secret']
            payment_intent = stripe.PaymentIntent.create(
                amount=item.price,
                currency=item.currency,
                automatic_payment_methods={'enabled': True},
            )
            return Response({
                             'clientSecret': payment_intent.client_secret,
                             'STRIPE_PUBLIC_KEY': settings.STRIPE_KEYS[item.currency]['public']})
        except Exception as e:
            return Response({'error': str(e)}, status=500) 
        
class BuyIntentTemplateAPIView(APIView):
    """
    Возвращает HTML-шаблон для страницы оплаты с использованием платежного намерения.
    Используется для отображения формы оплаты на клиенте.
    """
    renderer_classes = [TemplateHTMLRenderer]
    permission_classes = [AllowAny]
    template_name = 'buy_intend.html'

    def get(self, request, item_id):
        item = get_object_or_404(Item, pk=item_id)
        return Response({'item': item,
                         'STRIPE_PUBLIC_KEY': settings.STRIPE_KEYS[item.currency]['public']})

class BuyOrderAPIView(APIView):
    """
    Создает сессию Stripe Checkout для покупки текущего заказа(корзины).
    Возвращает ID сессии, который используется для перенаправления пользователя на страницу оплаты.
    Если заказ(корзина) пуст, возвращает сообщение об ошибке.
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        order = get_or_create_order(request)
        order_items = order.orderitem_set.all()
        
        if not order_items.exists():
            return Response({'error': 'Заказ пуст'}, status=400)
        currencies = {item.item.currency for item in order_items}
        if len(currencies) > 1:
            return Response({'error': 'Все товары в заказе должны быть в одной валюте'}, status=400)
        currency = order_items.first().item.currency
        try:
            stripe.api_key = settings.STRIPE_KEYS[currency]['secret']
            line_items = []
            for order_item in order_items:
                line_item = {
                    'price_data': {
                        'currency': currency,
                        'unit_amount': order_item.item.price,
                        'product_data': {
                            'name': order_item.item.name,
                            'description': order_item.item.description,
                        },
                    },
                    'quantity': order_item.quantity,
                }

                # Добавляем налог, если он есть
                if order.tax and order.tax.stripe_tax_rate_id:
                    line_item['tax_rates'] = [order.tax.stripe_tax_rate_id]

                line_items.append(line_item)

            checkout_data = {
                'payment_method_types': ['card'],
                'line_items': line_items,
                'mode': 'payment',
                'success_url': settings.SITE_URL + '/success/',
                'cancel_url': settings.SITE_URL + '/cancel/',
            }

            # Добавляем скидку, если она есть
            if order.discount and order.discount.stripe_coupon_id:
                checkout_data['discounts'] = [{
                    'coupon': order.discount.stripe_coupon_id
                }]

            checkout_session = stripe.checkout.Session.create(**checkout_data)

            return Response({'id': checkout_session.id})
        except Exception as e:
            return Response({'error': str(e)}, status=500)

