from django.core.exceptions import ValidationError
from django.db import transaction

from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.viewsets import ModelViewSet
from .models import OrderItem, Product, Order
from .serializers import ProductSerializer, OrderSerializer

@api_view(['GET'])
def index(request):
    """Return a simple welcome message."""
    return Response({'message': 'Welcome to the e-commerce API!'})

class ProductViewSet(ModelViewSet):
    queryset = Product.objects.filter(trashed=False).all()
    serializer_class = ProductSerializer

class OrderViewSet(ModelViewSet):
    queryset = Order.objects.filter(trashed=False).all()
    serializer_class = OrderSerializer

    def create(self, request, *args, **kwargs):
        """
        request.data = {
            "products": [
                {"product_id": 1, "quantity": 2},
                {"product_id": 2, "quantity": 1}
            ],
        }
        """
        product_requirements ={item['product_id']:item["quantity"] for item in request.data['products']}
        products = list(Product.objects.filter(trashed=False).filter(id__in=product_requirements.keys()).all())
        if len(products) != len(product_requirements):
            raise ValidationError('Some products do not exist')
        total_price = 0
        order = Order.objects.create(total_price=total_price)
        order_items = []
        for product in products:
            order_items.append(OrderItem(order=order, product=product, quantity=product_requirements[product.id]))
        OrderItem.objects.bulk_create(order_items)
        try:
            with transaction.atomic():
                products = list(Product.objects.select_for_update(nowait=True).filter(trashed=False).filter(id__in=product_requirements.keys()).all())
                for product in products:
                    if product.stock < product_requirements[product.id]:
                        raise ValidationError(f'Not enough stock for product {product.name}')
                    product.stock -= product_requirements[product.id]
                    # TODO: add discount logic here
                    total_price += product.price * product_requirements[product.id]
                    product.save()
                order.total_price = total_price
                order.status = Order.COMPLETED
                order.save()
        except ValidationError as e:
            order.status = Order.FAILED
            order.save()
            raise e

        return Response(status=201)