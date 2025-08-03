from rest_framework import serializers
from .models import Item, Order, OrderItem

class ItemSerializer(serializers.ModelSerializer):
    full_price = serializers.SerializerMethodField()
    
    class Meta:
        model = Item
        fields = '__all__'

    def get_full_price(self, obj):
        return "{0:.2f}".format(obj.price / 100)
    
class OrderItemSerializer(serializers.ModelSerializer):
    item = ItemSerializer()
    full_quantity_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = '__all__'

    def get_full_quantity_price(self, obj):
        return "{0:.2f}".format((obj.item.price * obj.quantity)/100)

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, source='orderitem_set')
    total_full_price = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = '__all__'
    
    def get_total_full_price(self, obj):
        return "{0:.2f}".format(obj.get_total_price() / 100)
