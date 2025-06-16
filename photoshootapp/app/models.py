from django.db import models

# Function to determine upload path for photographer photos
def photographer_directory_path(instance, filename):
    # File will be uploaded to MEDIA_ROOT/photos/photographer_<id>/<filename>
    return f'photos/photographer_{instance.photographer.id}/{filename}'

# Create your models here.
class Login(models.Model):
    email = models.EmailField(max_length=100, null=True)
    password = models.CharField(max_length=100, null=True)
    userType = models.CharField(max_length=100, null=True)
   

class Photographer(models.Model):
    login = models.ForeignKey(Login, on_delete=models.CASCADE,null=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    password = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100)


class UserReg(models.Model):
    login = models.ForeignKey(Login, on_delete=models.CASCADE,null=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=100,default="")
    address = models.CharField(max_length=500,default="")
    location = models.CharField(max_length=100,default="")
    password = models.CharField(max_length=128,default="") 
    pimage=models.ImageField("profile",null=True)

class PhotographrerReg(models.Model):
    login = models.ForeignKey(Login, on_delete=models.CASCADE,null=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128) 
    phone = models.CharField(max_length=100,default="")
    address = models.CharField(max_length=500,default="")
    location = models.CharField(max_length=100,default="")
    password = models.CharField(max_length=128,default="") 
    specialization = models.CharField(max_length=100,default="")
    pimage=models.ImageField(upload_to="'media/profile/",default="")
    status = models.CharField(max_length=50,  default='pending')

class Userrequest(models.Model):
    pid = models.ForeignKey(PhotographrerReg, on_delete=models.CASCADE,null=True)
    uid = models.ForeignKey(UserReg, on_delete=models.CASCADE,null=True)
    req = models.CharField(max_length=500)
    reply = models.CharField(max_length=500)
    date = models.DateTimeField(auto_now_add=True)
class AsiPhotographrerReg(models.Model):
    login = models.ForeignKey(Login, on_delete=models.CASCADE,null=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=100,default="")
    address = models.CharField(max_length=500,default="")
    location = models.CharField(max_length=100,default="")
    password = models.CharField(max_length=128,default="") 
    specialization = models.CharField(max_length=100,default="")
    pimage=models.ImageField(upload_to="'media/profile/")
    # status = models.CharField(max_length=50,  default='pending')




class Feedback(models.Model):
    user = models.ForeignKey(UserReg, on_delete=models.CASCADE)
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)


class Product(models.Model):
    CATEGORY_CHOICES = [
        ('Camera', 'Camera'),
        ('Accessory', 'Accessory'),
    ]
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)

class CartItem(models.Model):
    login = models.ForeignKey(UserReg, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, default='Pending')
    quantity = models.IntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

class Order(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    login = models.ForeignKey(UserReg, on_delete=models.CASCADE)
    name = models.CharField(max_length=50,null=True)
    phone = models.CharField(max_length=50,null=True)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    order_date = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=50, default='Pending')
    status = models.CharField(max_length=50, default='Pending') 


class ProductReview(models.Model):
    product = models.ForeignKey(Product, related_name='product_reviews', on_delete=models.CASCADE)
    login = models.ForeignKey(UserReg, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')])
    review_text = models.TextField()
    review_date = models.DateTimeField(auto_now_add=True)

class Events(models.Model):
    rid = models.ForeignKey(Userrequest, on_delete=models.CASCADE,null=True)
    Event = models.CharField(max_length=500)
    Dis = models.CharField(max_length=500)
    date = models.DateTimeField(auto_now_add=True)
    time=models.CharField(max_length=100)
    location=models.CharField(max_length=100)
    submitted_to_client = models.BooleanField(default=False)
    submission_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=50, choices=[('draft', 'Draft'), ('published', 'Published')], default='draft')

class Assignassistance(models.Model):
    pid = models.ForeignKey(PhotographrerReg, on_delete=models.CASCADE,null=True)
    evid= models.ForeignKey(Events, on_delete=models.CASCADE,null=True)
    asisst=models.IntegerField(default=0)
class Guest(models.Model):
    uid = models.ForeignKey(UserReg, on_delete=models.CASCADE,null=True)
    name = models.CharField(max_length=500)
    email = models.CharField(max_length=500)
class Photo(models.Model):
    PHOTO_CATEGORY_CHOICES = [
        ('wedding', 'Wedding'),
        ('portrait', 'Portrait'),
        ('nature', 'Nature'),
        ('fashion', 'Fashion'),
        ('other', 'other'),
    ]
    category = models.CharField(max_length=50, choices=PHOTO_CATEGORY_CHOICES)
    image = models.ImageField(upload_to=photographer_directory_path)
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField()
    photographer = models.ForeignKey(PhotographrerReg, on_delete=models.CASCADE) 
    eventid=models.ForeignKey(Events, on_delete=models.CASCADE,null=True)

class EventApplication(models.Model):
    """
    Model to track applications from secondary photographers for published events.
    """
    event = models.ForeignKey(Events, on_delete=models.CASCADE, related_name='applications')
    photographer = models.ForeignKey(AsiPhotographrerReg, on_delete=models.CASCADE, related_name='event_applications')
    message = models.TextField(default="No message provided", help_text="Message from the photographer explaining why they are interested in the event")
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected')
        ],
        default='pending'
    )
    
    class Meta:
        # Ensure a photographer can only apply once for each event
        unique_together = ('event', 'photographer')
