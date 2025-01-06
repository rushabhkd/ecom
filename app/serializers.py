from rest_framework import serializers
from .models import Product, Order, OrderItem

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "id", "name", "description", "price", "stock"

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    class Meta:
        model = OrderItem
        fields = "product", "quantity"

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    discount = serializers.SerializerMethodField()
    class Meta:
        model = Order
        fields ="id", "items", "total_price", "status", "discount"

    
    def get_discount(self, obj):
        total_product_price = sum(
            item.product.price * item.quantity for item in obj.items.all()
        )
        return max(0, (total_product_price - obj.total_price)*100/total_product_price)
    