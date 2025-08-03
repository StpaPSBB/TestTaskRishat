from django.contrib import admin
from django.contrib import messages
from .models import Item, Order, OrderItem, Discount, Tax
import stripe
from django.conf import settings

admin.site.register(Item)
admin.site.register(Order)
admin.site.register(OrderItem)
@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    """
    Админка для модели Discount.
    Позволяет создавать скидки, автоматически создавая купоны в Stripe.
    """
    list_display = ['name', 'percent_off', 'duration', 'currency', 'stripe_coupon_id']

    def get_readonly_fields(self, request, obj=None):
        if obj: 
            return ['name', 'percent_off', 'duration', 'currency', 'stripe_coupon_id']
        return super().get_readonly_fields(request, obj)
    
    def save_model(self, request, obj, form, change):
        stripe.api_key = settings.STRIPE_KEYS[obj.currency]['secret']  
        if not obj.stripe_coupon_id:
            coupon = stripe.Coupon.create(
                percent_off=obj.percent_off,
                duration=obj.duration,
                name=obj.name,
                currency=obj.currency
            )
            obj.stripe_coupon_id = coupon.id
        elif change:
            messages.warning(
                request,
                "Изменение скидки в текущей реализации не обновит данные в Stripe. Для изменения скидки создайте новый объект."
            )

        super().save_model(request, obj, form, change)
        
    def delete_model(self, request, obj):
        stripe.api_key = settings.STRIPE_KEYS[obj.currency]['secret']  
        try:
            if obj.stripe_coupon_id:
                stripe.Coupon.delete(obj.stripe_coupon_id)
        except stripe.error.InvalidRequestError as e:
            messages.error(
                request,
                f"Ошибка удаления купона Stripe: {e.user_message}"
            )
        super().delete_model(request, obj)

@admin.register(Tax)
class TaxAdmin(admin.ModelAdmin):
    """
    Админка для модели Tax.
    Позволяет создавать иналоги, автоматически создавая налоговые ставки в Stripe.
    """
    list_display = ['name', 'percentage', 'currency', 'stripe_tax_rate_id']

    def get_readonly_fields(self, request, obj=None):
        if obj: 
            return ['name', 'percentage', 'currency', 'stripe_tax_rate_id']
        return super().get_readonly_fields(request, obj)

    def save_model(self, request, obj, form, change):
        stripe.api_key = settings.STRIPE_KEYS[obj.currency]['secret']  
        if not obj.stripe_tax_rate_id:
            tax_rate = stripe.TaxRate.create(
                display_name=obj.name,
                percentage=obj.percentage,
                inclusive=False,
            )
            obj.stripe_tax_rate_id = tax_rate.id
        elif change:
            messages.warning(
                request,
                "Налоговые ставки Stripe неизменяемы. Для обновления параметров создайте новую ставку."
            )
            
        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        stripe.api_key = settings.STRIPE_KEYS[obj.currency]['secret']  
        try:
            if obj.stripe_tax_rate_id:
                stripe.TaxRate.modify(
                    obj.stripe_tax_rate_id,
                    active=False
                )
        except stripe.error.StripeError as e:
            messages.error(
                request,
                f"Ошибка деактивации налоговой ставки: {e.user_message}"
            )
        super().delete_model(request, obj)