from django.shortcuts import render
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, generics, decorators, status, permissions
from . import serializers
from .models import User, Category, Product, Cart, CartItem, Order, ElectronicNews, Review, OrderItem
from .serializers import UserSerializer, CategorySerializer,ProductSerializer, CartSerializer, CartItemSerializer, OrderSerializer, ElectronicNewsSerializer, ReviewSerializer, OrderItemSerializer
# Create your views here.

class UserViewSet(viewsets.ViewSet, generics.CreateAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action.__eq__('current_user'):
            return [permissions.IsAuthenticated()]

        return [permissions.AllowAny()]

    @action(methods=['get'], detail=False, url_path='current-user')
    def current_user(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    @action(methods=['get'], url_path='products', detail=True)
    def get_products(self, request, pk=None):
        category = self.get_object()
        products = category.products.order_by('id')  # Use related_name 'products'
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_queryset(self):
        queries = self.queryset

        q = self.request.query_params.get("q")
        if q:
            queries = queries.filter(name__icontains=q)

        return queries

class DiscountedProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        # Trả về các sản phẩm có discount lớn hơn 0
        return Product.objects.filter(discount__gt=0)

class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

    @action(methods=['get'], detail=False, url_path='current')
    def get_current_user_cart(self, request):
        user = request.user

        if not user.is_authenticated:
            return Response({'detail': 'Bạn cần đăng nhập để xem giỏ hàng.'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            cart = Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            return Response({'detail': 'Giỏ hàng không tồn tại.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(cart)
        return Response(serializer.data)

class CartItemViewSet(viewsets.ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer

    def create(self, request, *args, **kwargs):
        product_id = request.data.get('product')
        quantity = int(request.data.get('quantity', 1))  # Số lượng mặc định là 1

        if not product_id:
            return Response({'detail': 'Thiếu thông tin sản phẩm.'}, status=status.HTTP_400_BAD_REQUEST)

        # Xác định giỏ hàng
        if request.user.is_authenticated:
            # Người dùng đã đăng nhập, tạo hoặc lấy giỏ hàng của người dùng
            cart, created = Cart.objects.get_or_create(user=request.user)
        else:
            # Người dùng không đăng nhập, sử dụng giỏ hàng cố định có ID là 11
            try:
                cart = Cart.objects.get(id=11)
            except Cart.DoesNotExist:
                return Response({'detail': 'Giỏ hàng không tồn tại.'}, status=status.HTTP_400_BAD_REQUEST)

        # Xử lý sản phẩm
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'detail': 'Sản phẩm không tồn tại.'}, status=status.HTTP_400_BAD_REQUEST)

        # Tạo hoặc cập nhật CartItem
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, product=product,
            defaults={'quantity': quantity, 'priceTong': product.discounted_price * quantity}
        )
        if not created:
            # Nếu đã tồn tại, tăng số lượng và cập nhật giá tổng
            cart_item.quantity += quantity
            cart_item.priceTong = product.discounted_price * cart_item.quantity
            cart_item.save()

        serializer = self.get_serializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer

import logging

logger = logging.getLogger(__name__)

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            logger.error(f"Order creation failed: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ElectronicNewsViewSet(viewsets.ModelViewSet):
    queryset = ElectronicNews.objects.all()
    serializer_class = ElectronicNewsSerializer

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def get_queryset(self):
        product_id = self.request.query_params.get('product_id')
        if product_id:
            return Review.objects.filter(product_id=product_id)
        return Review.objects.all()


class UserOrderListView(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        user = request.user

        if not user.is_authenticated:
            return Response({'detail': 'Bạn cần đăng nhập để xem danh sách hóa đơn.'}, status=status.HTTP_401_UNAUTHORIZED)

        # Lọc đơn hàng dựa trên user ID
        orders = Order.objects.filter(user=user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

def thongke(request):
    return render(request, 'admin/thongke.html')