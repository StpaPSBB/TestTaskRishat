from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import F, Sum

class Item(models.Model):
    """
    Модель для представления товара в магазине.
    Содержит название, описание, валюту и цену товара.
    """

    name = models.CharField(max_length=200, verbose_name='name of item')
    description = models.TextField(max_length=50000, verbose_name='description of an item')
    price = models.PositiveIntegerField(verbose_name='price of an item')
    currency = models.CharField(max_length=10, choices=[('usd', 'USD'), ('eur', 'EUR')], default='usd', verbose_name='currency of item')

    class Meta:
        verbose_name = 'Item'
        verbose_name_plural = 'Items'

    def __str__(self):
        return self.name
    
class Discount(models.Model):
    """
    Модель для представления скидки.
    Содержит название скидки, процент скидки, длительность и идентификатор купона в Stripe.
    """
    name = models.CharField(max_length=255, verbose_name='name of discount')
    percent_off = models.PositiveIntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)], verbose_name='percent off')
    duration = models.CharField(
        max_length=10,
        choices=[("once", "Once"), ("repeating", "Repeating"), ("forever", "Forever")],
        default="once",
        verbose_name='duration of discount'
    )
    currency = models.CharField(max_length=3, choices=[('usd', 'USD'), ('eur', 'EUR')], default='usd')
    stripe_coupon_id = models.CharField(max_length=255, blank=True, null=True, verbose_name='stripe coupon id')

    class Meta:
        verbose_name = 'Discount'
        verbose_name_plural = 'Discounts'

    def __str__(self):
        return self.name

class Tax(models.Model):
    """
    Модель для представления налога.
    Содержит название налога, процент налога и идентификатор налоговой ставки в Stripe.
    """
    name = models.CharField(max_length=255, verbose_name='name of tax')
    percentage = models.PositiveIntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)],verbose_name='percentage of tax')
    currency = models.CharField(max_length=3, choices=[('usd', 'USD'), ('eur', 'EUR')], default='usd')
    stripe_tax_rate_id = models.CharField(max_length=255, blank=True, null=True, verbose_name='stripe tax rate id')

    class Meta:
        verbose_name = 'Tax'
        verbose_name_plural = 'Taxes'

    def __str__(self):
        return self.name
    
class Order(models.Model):
    """
    Модель для представления заказа.
    Содержит связь с товарами, скидкой и налогом.
    Содержит метод для расчета общей стоимости заказа с учетом скидки и налога.
    """
    items = models.ManyToManyField(Item, through='OrderItem', verbose_name='items in order')
    discount = models.ForeignKey(Discount, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='discount in order')
    tax = models.ForeignKey(Tax, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='tax in order')

    def get_total_price(self):
        base_total = self.orderitem_set.aggregate(
            total=Sum(F('item__price') * F('quantity'))
        )['total'] or 0
        
        total = base_total
        if self.discount:
            total -= total * self.discount.percent_off / 100
        
        if self.tax:
            total += total * self.tax.percentage / 100

        return total
        
    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
    
    def __str__(self):
        return f"Order: {self.id}"

class OrderItem(models.Model):
    """
    Промежуточная модель для связи заказа и товара.
    Содержит связь с заказом и товаром, а также количество товара в заказе.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name='order')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, verbose_name='item')
    quantity = models.PositiveIntegerField(default=1, verbose_name='quantity')

    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'

