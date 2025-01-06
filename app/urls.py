from django.urls import path
from .views import ProductViewSet, OrderViewSet, index
from rest_framework.routers import DefaultRouter


urlpatterns = [
    path('',index, name='index'),

]

router = DefaultRouter()
router.register('products', ProductViewSet, basename='product')
router.register('orders', OrderViewSet, basename='order')

urlpatterns += router.urls
