from django.core.exceptions import ValidationError
from django.db import transaction

from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.viewsets import ModelViewSet
from .models import OrderItem, Product, Order
from .utils import create_order, process_order
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
    http_method_names = ['get', 'post']

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
        order, creation_error = create_order(product_requirements=product_requirements)
        if creation_error is not None:
            return Response(creation_error, status=400)
        processing_error = process_order(order, product_requirements)
        if processing_error is not None:
            return Response(processing_error, status=400)
        return Response(status=201)