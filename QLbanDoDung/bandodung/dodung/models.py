from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from cloudinary.models import CloudinaryField

# Create your models here.
class User(AbstractUser):
    avatar = CloudinaryField('avatar',null=True)

    def __str__(self):
        return self.username

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    image = CloudinaryField('avatar', null=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', blank=True, null=True)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, null=True)  # Phần trăm giảm giá
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True)  # Giá đã giảm

    def save(self, *args, **kwargs):
        # Tính toán giá đã giảm và cập nhật trường discounted_price
        if self.discount:
            discount_percentage = self.discount
            self.discounted_price = self.price * (1 - discount_percentage)
        else:
            self.discounted_price = self.price
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.user:
            return f"Cart của {self.user.username} (ID: {self.id})"
        return f"Cart không có người dùng (ID: {self.id})"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    priceTong = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        # Cập nhật giá dựa trên số lượng và giá của sản phẩm
        self.priceTong = self.product.discounted_price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} - Số lượng: {self.quantity} - Tổng giá: {self.priceTong}"


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20,
                              choices=[('Đang chờ', 'Đang chờ'),
                                       ('Đang giao', 'Đang giao'),
                                       ('Đã giao', 'Đã giao'),
                                       ('Đã hủy', 'Đã hủy')])
    shipping_address = models.TextField()  # Địa chỉ giao hàng
    payment_method = models.CharField(
        max_length=100,
        choices=[
            ('Thanh toán khi nhận hàng', 'Thanh toán khi nhận hàng'),
            ('Chuyển khoản ngân hàng', 'Chuyển khoản ngân hàng'),
            ('Thanh toán trực tuyến', 'Thanh toán trực tuyến')
        ],
        default='Thanh toán khi nhận hàng'
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Tổng số tiền đơn hàng
    name = models.CharField(max_length=255, null=True, blank=True)  # Tên người đặt hàng
    email = models.EmailField(max_length=255, null=True, blank=True)
    note = models.TextField(blank=True, null=True)
    bank_transfer_image = CloudinaryField('imagebank', null=True, blank=True)  # Hình ảnh chuyển khoản

    def __str__(self):
        return f"Đơn hàng {self.id} của {self.user.username if self.user else self.name}"



class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    quantity = models.PositiveIntegerField( default=0)
    priceTong = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Mã {self.id} - Sản phẩm: {self.product.name} - của đơn : {self.order.id}"


class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()  # Số sao, ví dụ từ 1 đến 5
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')  # Đảm bảo mỗi người dùng chỉ có một đánh giá cho một sản phẩm

    def __str__(self):
        return f"Đánh giá của {self.user.username} cho {self.product.name}"


class ElectronicNews(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    published_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

