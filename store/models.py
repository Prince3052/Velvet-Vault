from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from decimal import Decimal
# Create your models here.
class JewelryItem(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(max_length=250, null=True)

    price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    stock = models.PositiveIntegerField(default=0)
    slug = models.SlugField(unique=True, null=True, blank=True)
    category = models.CharField(max_length=50)
    brand = models.CharField(max_length=100, blank=True, null=True)

    image = models.ImageField(upload_to='products/', blank=True, null=True)
    sku = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1

            while JewelryItem.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

#cart model
class Cart(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart {self.id}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(JewelryItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

def total_price(self):
    if self.product.discount_price:
        return self.product.discount_price * self.quantity
    elif self.product.price:
        return self.product.price * self.quantity
    return 0

#TEAM MEMBER MODEL
class TeamMember(models.Model):
    bgImage = models.ImageField(upload_to='team/', null=True, blank=True)
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=50)
    experience = models.PositiveBigIntegerField()
    image = models.ImageField(upload_to='team/')

    twitter = models.URLField(blank=True, null=True)
    facebook = models.URLField(blank=True, null=True)
    pinterest = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name
    
#COLLECTION MODEL
class Collection(models.Model):
    name = models.CharField(max_length=20, unique=True)
    description = models.TextField(max_length=200, blank=True, null=True)
    image = models.ImageField(upload_to='collections/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    products = models.ManyToManyField(
        'JewelryItem',
        related_name='collections',
        blank=True
    )

    def __str__(self):
        return self.name


#Blog Model


class Blog(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    content = models.TextField()
    image = models.ImageField(upload_to='blogs/', blank=True, null=True)
    author = models.CharField(max_length=100, default="Admin")
    created_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    
class ProductImage(models.Model):
    product = models.ForeignKey(
        JewelryItem,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='product_gallery/')
    is_featured = models.BooleanField(default=False)

class ProductVideo(models.Model):
    product = models.ForeignKey(
        JewelryItem,
        on_delete=models.CASCADE,
        related_name='videos'
    )
    video = models.FileField(upload_to='product_videos/')
    thumbnail = models.ImageField(upload_to='video_thumbnails/', blank=True, null=True)

    def __str__(self):
        return self.product.name