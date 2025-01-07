from typing import List, Tuple
from django.core.exceptions import ValidationError
from django.db import transaction

from .constants import OrderProcessingError
from .models import Order, OrderItem, Product

def create_order(product_requirements: dict) -> Tuple[Order|None, str|None ]:
        products = list(Product.objects.filter(trashed=False).filter(id__in=product_requirements.keys()).all())
        # If requested products are not available
        if len(products) != len(product_requirements):
            return None, OrderProcessingError.PRODUCT_NOT_FOUND
        total_price = 0
        order = Order.objects.create(total_price=total_price)
        order_items = []
        for product in products:
            order_items.append(OrderItem(order=order, product=product, quantity=product_requirements[product.id]))
        OrderItem.objects.bulk_create(order_items)
        return order, None

def process_order(order: Order, product_requirements: dict) -> str|None:
    """
    Process an order and update the stock of the products.
    """
    error = None
    try:
        with transaction.atomic():
            products = list(Product.objects.select_for_update(nowait=True).filter(trashed=False).filter(id__in=product_requirements.keys()).all())
            total_price = 0
            for product in products:
                if product.stock < product_requirements[product.id]:
                    raise ValidationError(OrderProcessingError.STOCK_NOT_ENOUGH.format(product_name=product.name))
                product.stock -= product_requirements[product.id]
                product.save()
                total_price += product.price * product_requirements[product.id]
            
            order.total_price = total_price
            order.status = Order.COMPLETED
            order.save()
    except (ValidationError, Exception) as e:
        error = e.message if hasattr(e, 'message') else 'An error occurred while processing the order'
        order.status = Order.FAILED
        order.save()
        print(e)
    return error
    