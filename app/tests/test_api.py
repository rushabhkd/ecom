from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from app.models import Product, Order
from app.constants import OrderProcessingError

class ProductAPITestCase(APITestCase):
    def setUp(self):
        self.product1 = Product.objects.create(name='Product 1', description='Description 1', price=100, stock=10)
        self.product2 = Product.objects.create(name='Product 2', description='Description 2', price=200, stock=5)
        self.product_data = {
            'name': 'Product 3',
            'description': 'Description 3',
            'price': 300,
            'stock': 15
        }

    def test_get_products(self):
        response = self.client.get('/ecom/products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_create_product(self):
        response = self.client.post('/ecom/products/', data=self.product_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 3)

    def test_update_product(self):
        response = self.client.put(f'/ecom/products/{self.product1.id}/', data=self.product_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product1.refresh_from_db()
        self.assertEqual(self.product1.name, 'Product 3')

    def test_delete_product(self):
        response = self.client.delete(f'/ecom/products/{self.product1.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Product.objects.filter(trashed=True).count(), 1)

class OrderAPITestCase(APITestCase):
    def setUp(self):
        self.product1 = Product.objects.create(name='Product 1', description='Description 1', price=100, stock=10)
        self.product2 = Product.objects.create(name='Product 2', description='Description 2', price=200, stock=5)
        self.order_data = {
            'products': [
                {'product_id': self.product1.id, 'quantity': 2},
                {'product_id': self.product2.id, 'quantity': 1}
            ]
        }

    def test_get_orders(self):
        Order.objects.create(total_price=500)
        response = self.client.get('/ecom/orders/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_order(self):
        response = self.client.post('/ecom/orders/', data=self.order_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)
        self.product1.refresh_from_db()
        self.product2.refresh_from_db()
        self.assertEqual(self.product1.stock, 8)
        self.assertEqual(self.product2.stock, 4)

    def test_product_not_found(self):
        order_data = {
            'products': [
                {'product_id': 999, 'quantity': 1}
            ]
        }
        response = self.client.post('/ecom/orders/', data=order_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, OrderProcessingError.PRODUCT_NOT_FOUND)

    def test_insufficient_stock(self):
        order_data = {
            'products': [
                {'product_id': self.product1.id, 'quantity': 11}
            ]
        }
        response = self.client.post('/ecom/orders/', data=order_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data,OrderProcessingError.STOCK_NOT_ENOUGH.format(product_name=self.product1.name))

        self.product1.refresh_from_db()
        self.assertEqual(self.product1.stock, 10)

    def test_update_order(self):
        updated_order_data = {
            'products': [
                {'product_id': self.product1.id, 'quantity': 1},
                {'product_id': self.product2.id, 'quantity': 2}
            ]
        }
        response = self.client.put("/ecom/orders/1/", data=updated_order_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_order(self):
        response = self.client.delete("/ecom/orders/1/")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
