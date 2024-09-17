from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from .models import User, Category, Product, Cart, CartItem, Order, ElectronicNews, Review, OrderItem

class UserSerializer(ModelSerializer):
    avatar_url = serializers.SerializerMethodField()
    avatar = serializers.ImageField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'username', 'password', 'avatar', 'avatar_url']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def get_avatar_url(self, instance):
        if instance.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(instance.avatar.url)
            return instance.avatar.url
        return None

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['avatar_url'] = self.get_avatar_url(instance)
        return rep

    def create(self, validated_data):
        avatar = validated_data.pop('avatar', None)
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        if avatar:
            user.avatar = avatar
        user.save()
        return user


class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'product', 'rating', 'comment', 'created_at', 'first_name', 'last_name', 'username']

    def create(self, validated_data):
        user = self.context['request'].user
        if user.is_anonymous:
            raise serializers.ValidationError('You must be logged in to submit a review.')
        validated_data['user'] = user
        return super().create(validated_data)

class ProductSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    image = serializers.ImageField(write_only=True, required=False)

    class Meta:
        model = Product
        fields = '__all__'

    def get_image_url(self, instance):
        if instance.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(instance.image.url)
            return instance.image.url
        return None

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['image_url'] = self.get_image_url(instance)
        return rep


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = CartItem
        fields = '__all__'


class CartSerializer(ModelSerializer):
    cart_items = CartItemSerializer(many=True)  # Hiển thị các mặt hàng trong giỏ hàng

    class Meta:
        model = Cart
        fields = '__all__'

class ElectronicNewsSerializer(ModelSerializer):
    class Meta:
        model = ElectronicNews
        fields = '__all__'

# serializers.py

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'


from decimal import Decimal


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'priceTong']

class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)  # Read-only field for output purposes
    bank_transfer_image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'order_items', 'created_at', 'status', 'shipping_address', 'payment_method',
                  'total_amount', 'name', 'email', 'note', 'bank_transfer_image']

    def create(self, validated_data):
        user = self.context['request'].user if self.context['request'].user.is_authenticated else None
        shipping_address = validated_data['shipping_address']
        payment_method = validated_data['payment_method']
        note = validated_data.get('note', '')
        name = validated_data.get('name', '') if not user else (user.username if user else '')
        email = validated_data.get('email', '') if not user else (user.email if user else '')
        status = validated_data.get('status', 'Đang chờ')  # Set default value for status

        # Create the order
        order = Order.objects.create(
            user=user,
            shipping_address=shipping_address,
            payment_method=payment_method,
            note=note,
            name=name,
            email=email,
            status=status
        )

        total_amount = Decimal('0.000')

        # Get the cart for the user if authenticated
        if user:
            try:
                cart = Cart.objects.get(user=user)
            except Cart.DoesNotExist:
                cart = None
        else:
            # If user is not authenticated, use a fixed cart ID
            try:
                cart = Cart.objects.get(id=11)  # Fixed cart ID
            except Cart.DoesNotExist:
                cart = None

        if cart:
            # Get all CartItems from the cart
            cart_items = cart.cart_items.all()
            for cart_item in cart_items:
                # Create OrderItem from CartItem
                order_item = OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    priceTong=cart_item.priceTong
                )
                total_amount += order_item.priceTong

            # Update the total amount for the order
            order.total_amount = total_amount
            order.save()

            # Delete CartItems after creating OrderItems
            cart.cart_items.all().delete()

            # Xử lý ảnh chuyển khoản ngân hàng nếu có
            if 'bank_transfer_image' in validated_data:
                order.bank_transfer_image = validated_data['bank_transfer_image']
                order.save()

        return order
