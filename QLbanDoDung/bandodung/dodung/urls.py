from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include
from . import views
from .admin import admin_site
from rest_framework.routers import DefaultRouter
from .views import DiscountedProductListView, ProductViewSet, CartItemViewSet

router = DefaultRouter()

router.register('user', views.UserViewSet, basename='user')
router.register('category', views.CategoryViewSet, basename='category')
router.register('product', views.ProductViewSet, basename='product')
router.register('cart', views.CartViewSet, basename='cart')
router.register('cartitem', views.CartItemViewSet, basename='cartitem')
router.register('order', views.OrderViewSet, basename='order')
router.register('orderitem', views.OrderItemViewSet, basename='orderitem')
router.register('electronicnews', views.ElectronicNewsViewSet, basename='electronicnews')
router.register('review', views.ReviewViewSet, basename='review')

urlpatterns = [
    # path('', include(router.urls)),
    # path('admin/', admin_site.urls),
    # path('discounted-products/', DiscountedProductListView.as_view(), name='discounted-products-list'),
    # path('orderlist/', views.UserOrderListView.as_view({'get': 'list'}), name='user-order-list'),
    path('', views.thongke),
]
