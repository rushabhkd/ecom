from django.test import TestCase

from app.models import Product  
from app.utils import create_order, process_order
from app.constants import OrderProcessingError

class UtilsTestCase(TestCase):
    def setUp(self):
        self.product1 = Product.objects.create(name='Product 1', description='Description 1', price=100, stock=10)
        self.product2 = Product.objects.create(name='Product 2', description='Description 2', price=200, stock=5)
        self.product_requirements = {
            self.product1.id: 2,
            self.product2.id: 1
        }

    def test_create_order_success(self):
        order, error = create_order(self.product_requirements)
        self.assertIsNotNone(order)
        self.assertIsNone(error)
        self.assertEqual(order.items.count(), 2)
        self.assertEqual(order.items.get(product=self.product1).quantity, 2)
        self.assertEqual(order.items.get(product=self.product2).quantity, 1)

    def test_create_order_product_not_found(self):
        invalid_product_requirements = {
            999: 1  # Non-existent product ID
        }
        order, error = create_order(invalid_product_requirements)
        self.assertIsNone(order)
        self.assertEqual(error, OrderProcessingError.PRODUCT_NOT_FOUND)

    def test_process_order_success(self):
        order, error = create_order(self.product_requirements)
        self.assertIsNone(error)
        error = process_order(order, self.product_requirements)
        self.assertIsNone(error)
        self.product1.refresh_from_db()
        self.product2.refresh_from_db()
        self.assertEqual(self.product1.stock, 8)  # 10 - 2
        self.assertEqual(self.product2.stock, 4)  # 5 - 1

    def test_process_order_insufficient_stock(self):
        self.product1.stock = 1
        self.product1.save()
        order, error = create_order(self.product_requirements)
        self.assertIsNone(error)
        error = process_order(order, self.product_requirements)
        self.assertIsNotNone(error)
        self.assertEqual(error, 'Not enough stock for product Product 1')