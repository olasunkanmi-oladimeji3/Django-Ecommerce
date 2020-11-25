from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils import timezone



# Create your models here.

DELIVERY_METHODS =(
    ('Pickup Station','Pickup Station'),
    ('Door Delivery','Door Delivery'),
)
Label_CHOICES =(
    ('blue','primary'),
    ('red','danger'),
    ('yellow','warning'),
)

class Category(models.Model):
    name= models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    

    class Meta:
        ordering=('-name',)
    def __str__(self):
        return self.name
    def get_absolute_url(self):
        return reverse("core:category",args=[self.slug])


class Item(models.Model):
    title= models.CharField(max_length=100)
    category = models.ForeignKey(Category,on_delete = models.CASCADE)
    price = models.DecimalField(max_digits=8,decimal_places=2)
    discount_price = models.DecimalField(max_digits=8,decimal_places=2,blank=True)
    description= models.TextField()
    label= models.CharField(choices=Label_CHOICES,max_length=8 )
    label_text= models.CharField(max_length=15,blank=True)
    slug = models.SlugField()
    image=models.ImageField(upload_to='pictures',blank=True)

    class Meta:
        ordering=('-title',)

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse("core:product",kwargs={'slug':self.slug})

    def get_add_to_cart(self):
        return reverse("core:add-to-cart",kwargs={'slug':self.slug})

    def get_remove_from_cart(self):
        return reverse("core:remove-from-cart",kwargs={'slug':self.slug})

#LINK OF ITEM MODEL AND ODER MODEL
class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete = models.CASCADE)
    item = models.ForeignKey(Item,on_delete = models.CASCADE)
    quantity=models.IntegerField(default=1)
    ordered = models.BooleanField(default=False)

    
    def __str__(self):
        return f"{self.quantity} of {self.item.title}"

    def get_total_item_price(self):
        return self.quantity * self.item.price
    
    def get_total_discount_item_price(self):
        return self.quantity * self.item.discount_price
    
    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()
#SHOOPING CART
class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete = models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    start_date =  models.DateTimeField(auto_now_add =True)
    ordered_date =  models.DateTimeField()
    ordered = models.BooleanField(default=False)
    payment  = models.ForeignKey('Payment', on_delete=models.SET_NULL, blank=True, null=True)
    billing_address = models.ForeignKey('BillingAddress', on_delete=models.SET_NULL, blank=True, null=True)
    
    def __str__(self):
        return self.user.username
    
    def get_total(self):
        total=0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        return total


class   BillingAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete = models.CASCADE)
    Address= models.CharField(max_length=100)
    DELIVERY_METHOD= models.CharField(choices= DELIVERY_METHODS,max_length=15,default='Door Delivery')

    def __str__(self):
        return self.user.username

class Payment(models.Model):
    user_charge_id=models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete = models.SET_NULL,blank=True,null=True)
    amount=models.DecimalField(max_digits=8,decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.user.username