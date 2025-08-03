from django.urls import path
from django.views.generic import TemplateView
from .views import ItemAPIView, BuyAPIView, ListItemAPIView, OrderAPIView, AddToOrderAPIView, BuyIntentAPIView, BuyIntentTemplateAPIView, ClearOrderAPIView, BuyOrderAPIView, AddDiscountAPIView, AddTaxAPIView

urlpatterns = [
    path('', ListItemAPIView.as_view(), name='list-items'),
    path('item/<int:id>/', ItemAPIView.as_view(), name='item'),
    path('buy/<int:id>/', BuyAPIView.as_view(), name='buy'),
    path('buy_intent/<int:item_id>/', BuyIntentAPIView.as_view(), name='buy-intent'),
    path('buy_intent_html/<int:item_id>/', BuyIntentTemplateAPIView.as_view(), name='buy-intent-html'),
    path('order/', OrderAPIView.as_view(), name='order'),
    path('add_to_order/<int:item_id>/', AddToOrderAPIView.as_view(), name='add-to-order'),
    path('buy_order/', BuyOrderAPIView.as_view(), name='buy-order'),
    path('clear_order/', ClearOrderAPIView.as_view(), name='clear-order'),
    path('add_discount/', AddDiscountAPIView.as_view(), name='add-discount'),
    path('add_tax/', AddTaxAPIView.as_view(), name='add-tax'),
    path('success/', TemplateView.as_view(template_name='success.html')), 
    path('cancel/', TemplateView.as_view(template_name='cancel.html')),
]