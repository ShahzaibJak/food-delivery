from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Booking(models.Model):
    first_name = models.CharField(max_length=200)
    reservation_date = models.DateField()
    reservation_slot = models.TextField(default=10)
    user = models.OneToOneField(User, on_delete=models.CASCADE,default=None)
    def __str__(self): 
        return self.first_name + " " + self.reservation_date + ' ' + self.reservation_slot


# Add code to create Menu model
class Menu(models.Model):
   name = models.CharField(max_length=200) 
   price = models.IntegerField(null=False) 
   menu_item_description = models.TextField(max_length=1000, default='') 
   image = models.ImageField(null=True, blank=True, upload_to='images/')
   def __str__(self):
      return self.name
   

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    items = models.ManyToManyField(Menu, through='CartItem')

    def __str__(self):
        return f"Cart for {self.user.username}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.menu.name} - Quantity: {self.quantity}"

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    items = models.ManyToManyField(Menu, through='OrderItem')
    created_at = models.DateTimeField(auto_now_add=True)
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Preparing", "Preparing"),
        ("Enroute", "Enroute"),
        ("Rejected", "Rejected"),
        ("Completed", "Completed"),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pending"
    )
    def __str__(self):
        return f"Order #{self.id} for {self.user.username} at {self.created_at}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.menu.name} - Quantity: {self.quantity}"
    
class OrderSummary(Order):
    class Meta:
        proxy = True
        verbose_name = 'Order Summary'
        verbose_name_plural = 'Orders Summary'