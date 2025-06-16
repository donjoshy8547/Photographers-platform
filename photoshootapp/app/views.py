from django.shortcuts import render,redirect
from django.contrib import messages
from . models import*
from django.http import HttpResponse
from django.conf import settings
import os
import concurrent.futures
from django.contrib.auth.hashers import check_password
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings
import random
import zipfile
import traceback
import csv
import json
# Create your views here.
def home(request):
    return render(request,'index.html')

def photohome(request):
    return render(request,'photograph/photohome.html')
def asphotohome(request):
    return render(request,'asphotograph/photohome.html')

########################################################
                #ADMIN
########################################################

def login(request):
    try:
        if request.method == 'POST':
            email = request.POST.get('email')
            request.session["email"]=email
            password = request.POST.get('password')
            user = Login.objects.filter(email=email, password=password).first()

            if user:
                if user.userType == 'admin':
                    messages.info(request, 'Welcome to Admin Home')
                    return redirect('/adminhome')
                elif user.userType == 'photographer':
                    phdata = PhotographrerReg.objects.filter(email=email).first()
                    if phdata: 
                        pid = phdata.id
                        request.session['pid'] = pid
                        messages.info(request, 'Welcome to Photographer Home')
                        return redirect('/photohome')
                    else:
                        messages.error(request, 'Photographer data not found.')
                        return render(request, 'login.html')
                elif user.userType == 'user':
                    usrdata = UserReg.objects.filter(email=email).first()
                    if usrdata:
                        # if usrdata.status == 'approved':
                            uid = usrdata.id
                            request.session['uid'] = uid
                            messages.info(request, 'Welcome to User Home')
                            return redirect('/userhome')
                        # else:
                        #     messages.info(request, 'Your account is not approved yet.')
                        #     return render(request, 'login.html')
                    else:
                        messages.info(request, 'User data not found.')
                        return render(request, 'login.html')
                elif user.userType == 'asiphotographer':
                    usrdata = PhotographrerReg.objects.filter(email=email).first()
                    if usrdata:
                        # if usrdata.status == 'approved':
                            uid = usrdata.id
                            request.session['uid'] = uid
                            messages.info(request, 'Welcome to User Home')
                            return redirect('/asphotohome')
                        # else:
                        #     messages.info(request, 'Your account is not approved yet.')
                        #     return render(request, 'login.html')
                    else:
                        messages.info(request, 'User data not found.')
                        return render(request, 'login.html')
                else:
                    messages.info(request, 'Invalid user type.')
                    return render(request, 'login.html')

            else:
                data=Guest.objects.get(email=email)
                print("##################################3")

                if data:
                    print(request.session.get("otp"))
                    if password=="":
                        otp=random.choice([2004,1234, 7894, 1000, 7003])
                        request.session["otp"]=otp
                        send_mail("OTP", str(otp), settings.EMAIL_HOST_USER, [email])
                    elif(str(password)==str(request.session.get("otp"))):
                        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
                        return redirect('/gustgallarylist')
                else:
                    messages.info(request, 'Invalid credentials.')
                    return render(request, 'login.html')
    except:
        messages.info(request, 'Invalid credentials.')
        return render(request, 'login.html')

    return render(request, 'login.html')

# def addphotographer(request):
#     if request.method == 'POST':
#         name = request.POST.get('name')
#         email = request.POST.get('email')
#         phone = request.POST.get('phone')
#         specialization = request.POST.get('specialization')
#         password = request.POST.get('password')

#         if Login.objects.filter(email=email).exists():
#             messages.info(request, 'A photographer with this email already exists.')
#             return render(request, 'Admin/addphotographer.html')
#         login = Login(email=email, password=password, userType='photographer')
#         login.save()
#         photograph = Photographer(login=login, name=name,email=email,phone=phone,
#                                   specialization=specialization,password = password)
#         photograph.save() 
        
#         messages.info(request, 'Photographer added successfully!')
#         return redirect('/adminhome')

#     return render(request, 'Admin/addphotographer.html')

def photographerview(request):
    pho = PhotographrerReg.objects.all()
    return render(request,"Admin/view.html",{'pho':pho})


def update(request):
    id = request.GET.get('id')
    photo = Photographer.objects.filter(id=id).first()
    if request.POST:
        # login_id = request.POST.get('login')
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        specialization = request.POST.get('specialization')

        photo.name=name
        photo.phone=phone
        photo.specialization=specialization

        photo.save()
        update = Photographer.objects.filter(id=id).update(name=name,
                                                specialization=specialization)
        messages.info(request,"updated successfully")
        return redirect('/photographerview')
    return render(request,'Admin/update.html',{'photo':photo})
        
def delete(request):
    id = request.GET.get('id')
    delete = Photographer.objects.filter(id=id).delete()
    messages.info(request,"sucessfully Deleted")
    return redirect('/photographerview')


def addphoto(request):
    photograph = PhotographrerReg.objects.all() 
    pid=request.session.get("pid")
    event=Events.objects.filter(rid__pid=pid)
    if request.POST:
        print("Hellooooo\n", request.POST, "\nhello")
        category = request.POST.get('category')
        image = request.FILES.getlist('image')
        photographer_id = request.POST.get('photographer_id')
        request.session['pid_id'] = photographer_id
        if image:
            photographer = PhotographrerReg.objects.get(id=request.session['pid'])
            for img in image:
                Photo.objects.create(category=category,image=img,photographer=photographer)
            messages.info(request, 'Photo uploaded successfully!')
            return redirect('/myphoto')

    return render(request, 'photograph/addphoto.html', {'photograph': photograph,"event":event})

def asaddphoto(request):
    photograph = PhotographrerReg.objects.all() 
    aid=request.session.get("uid")
    aid=PhotographrerReg.objects.get(id=aid)
    event=Assignassistance.objects.filter(asisst=aid.id)
    if request.POST:
        category = request.POST.get('category')
        image = request.FILES.get('image')
        photographer_id = request.POST.get('photographer_id')
        request.session['pid_id'] = photographer_id
        if image:
            photographer = PhotographrerReg.objects.get(id=request.session['pid'])
            Photo.objects.create(category=category,image=image,photographer=photographer)
            messages.info(request, 'Photo uploaded successfully!')
            return redirect('/myphoto')

    return render(request, 'asphotograph/addphoto.html', {'photograph': photograph,"event":event})

def myphoto(request):       
    pid = request.session['pid']
    
    # OPTION 1: Display all files in the directory (regardless of database)
    # Get the directory path for this photographer
    photographer_dir = os.path.join(settings.MEDIA_ROOT, f'photos/photographer_{pid}')
    
    # Check if directory exists
    if not os.path.exists(photographer_dir):
        print(f"Directory does not exist: {photographer_dir}")
        return render(request, 'photograph/gallery.html', {'images': []})
    
    # Get all image files in the directory
    images = []
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
    media_url = settings.MEDIA_URL
    
    print(f"Scanning directory for gallery: {photographer_dir}")
    for filename in os.listdir(photographer_dir):
        file_path = os.path.join(photographer_dir, filename)
        if os.path.isfile(file_path) and any(filename.lower().endswith(ext) for ext in valid_extensions):
            # Create a dictionary with the same structure as the Photo model objects
            relative_path = f'photos/photographer_{pid}/{filename}'
            url = f"{media_url}{relative_path}"
            images.append({
                'image': {'url': url, 'name': relative_path},
                'id': filename,  # Use filename as ID since these aren't in the database
            })
            print(f"Added to gallery: {url}")
    
    return render(request, 'photograph/gallery.html', {'images': images})

def gallery(request):
    """
    View function to display the gallery of photos.
    """
    pid = request.session.get('pid')
    if not pid:
        messages.error(request, "Please login to view the gallery")
        return redirect('login')
    
    # OPTION 1: Display all files in the directory (regardless of database)
    # Get the directory path for this photographer
    photographer_dir = os.path.join(settings.MEDIA_ROOT, f'photos/photographer_{pid}')
    
    # Check if directory exists
    if not os.path.exists(photographer_dir):
        print(f"Directory does not exist: {photographer_dir}")
        return render(request, 'photograph/gallery.html', {'images': []})
    
    # Get all image files in the directory
    images = []
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
    media_url = settings.MEDIA_URL
    
    print(f"Scanning directory for gallery: {photographer_dir}")
    for filename in os.listdir(photographer_dir):
        file_path = os.path.join(photographer_dir, filename)
        if os.path.isfile(file_path) and any(filename.lower().endswith(ext) for ext in valid_extensions):
            # Create a dictionary with the same structure as the Photo model objects
            relative_path = f'photos/photographer_{pid}/{filename}'
            url = f"{media_url}{relative_path}"
            images.append({
                'image': {'url': url, 'name': relative_path},
                'id': filename,  # Use filename as ID since these aren't in the database
            })
            print(f"Added to gallery: {url}")
    
    return render(request, 'photograph/gallery.html', {'images': images})

def asmyphoto(request):       
    pid = request.session['pid']
    
    # OPTION 1: Display all files in the directory (regardless of database)
    # Get the directory path for this photographer
    photographer_dir = os.path.join(settings.MEDIA_ROOT, f'photos/photographer_{pid}')
    
    # Check if directory exists
    if not os.path.exists(photographer_dir):
        print(f"Directory does not exist: {photographer_dir}")
        return render(request, 'asphotograph/gallery.html', {'images': []})
    
    # Get all image files in the directory
    images = []
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
    media_url = settings.MEDIA_URL
    
    print(f"Scanning directory for gallery: {photographer_dir}")
    for filename in os.listdir(photographer_dir):
        file_path = os.path.join(photographer_dir, filename)
        if os.path.isfile(file_path) and any(filename.lower().endswith(ext) for ext in valid_extensions):
            # Create a dictionary with the same structure as the Photo model objects
            relative_path = f'photos/photographer_{pid}/{filename}'
            url = f"{media_url}{relative_path}"
            images.append({
                'image': {'url': url, 'name': relative_path},
                'id': filename,  # Use filename as ID since these aren't in the database
            })
            print(f"Added to gallery: {url}")
    
    return render(request, 'asphotograph/gallery.html', {'images': images})

def deleteimage(request):
    id = request.GET.get('id')
    pid = request.session.get("pid")
    
    # Check if id is a number (database record) or a filename
    try:
        # Try to convert to integer (database ID)
        photo_id = int(id)
        # Delete from database
        Photo.objects.filter(id=photo_id).delete()
    except ValueError:
        # If not a number, treat as filename
        # Get the full path to the file
        file_path = os.path.join(settings.MEDIA_ROOT, 'photos', f'photographer_{pid}', id)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"Deleted file: {file_path}")
            except Exception as e:
                print(f"Error deleting file: {str(e)}")
    
    messages.info(request, "Successfully Deleted")
    return redirect('/myphoto')


def userview(request):
    usr = UserReg.objects.all()
    return render(request,'Admin/userview.html',{'usr':usr})

def adminhome(request):
    # Get real statistics from database
    user_count = UserReg.objects.all().count()
    photographer_count = PhotographrerReg.objects.all().count()
    assistant_count = PhotographrerReg.objects.filter(specialization='Assistant').count()
    product_count = Product.objects.all().count()
    event_count = Events.objects.all().count()
    
    context = {
        'user_count': user_count,
        'photographer_count': photographer_count,
        'assistant_count': assistant_count,
        'product_count': product_count,
        'event_count': event_count
    }
    
    return render(request, 'Admin/adminhome.html', context)


def accept(request):
    userid = request.GET.get("id")
    user = UserReg.objects.filter(id=userid).first()
    if user:
        user.status = "approved"
        user.save() 
        messages.info(request,'Approved successfully')
    return redirect('/userview')

def reject(request):
    userid = request.GET.get("id")
    user = UserReg.objects.filter(id=userid).first()
    if user:
        user.status = "rejected" 
        user.save() 
    messages.info(request,'User will Rejected Sucess')
    return redirect('/userview')

def viewfeedback(request):
    phfg = Feedback.objects.all()
    print(phfg)
    return render(request,'Admin/feedbacklist.html',{'phfg':phfg})

def deletefeedback(request):
    if request.GET.get('id'):
        feedback_id = request.GET.get('id')
        try:
            feedback = Feedback.objects.get(id=feedback_id)
            feedback.delete()
            messages.success(request, 'Feedback deleted successfully')
        except Feedback.DoesNotExist:
            messages.error(request, 'Feedback not found')
        except Exception as e:
            messages.error(request, f'Error deleting feedback: {str(e)}')
    return redirect('/viewfeedback')

def productlistoo(request):
    pro = Product.objects.all()
    return render(request,"photograph/productlist.html",{"pro":pro})



def addcart(request):
    id =request.GET.get("id")
    uid = request.session.get("uid")
    login = UserReg.objects.get(id=uid)  
    product = Product.objects.get(id=id)
   
    cart=CartItem.objects.create(login=login,product=product)
    cart.save()
    return redirect('/productlistoo',{'product':product})


import datetime


def cartview(request):
    id=request.POST.get('discount_value')
    uid = request.session.get("uid")
    view = CartItem.objects.filter(login=uid)
    total = 0
    
    for item in view:
        item.total = item.product.price * item.quantity
        total += item.total  # Accumulate total price of all items
    
    # Handle coupon application
    code = request.POST.get('code')  # Get the coupon code from POST request
    discount = 0  # Initialize discount value
       
    discounted_total = total - discount
    return render(request, "photograph/cart.html", {
        'view': view,
        'total': total,  # Original total before discount
        'discounted_total': discounted_total,  # Final total after discount
        'coupon_code': code,  
    })

def deletecart(request):
    id = request.GET.get('id')
    dee = CartItem.objects.filter(id=id).delete()
    messages.info(request,"sucessfully Remove")
    return redirect('/cartview')

def order(request):
    price = request.GET.get('price')
    uid = request.session.get("uid")
    if not uid:
        return redirect('/login')

    login = UserReg.objects.get(id=uid)
    cart = CartItem.objects.filter(login=login)

    total = sum(i.product.price * i.quantity for i in cart)

    if request.POST:
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        postal_code = request.POST.get('postal_code')
        country = request.POST.get('country')

        order_ids = []  
        for item in cart:
            order = Order.objects.create(
                product=item.product,
                login=login,
                name=name,
                phone=phone,
                address=address,
                city=city,
                state=state,
                postal_code=postal_code,
                country=country
            )
            order_ids.append(order.id)

        cart.update(status="ordered")
        
        return redirect(f'/payment?order_id={order_ids[-1]}&total={total}')

    return render(request, 'photograph/createorder.html', {'cart': cart, 'discounted_total':total })


def payment(request):
    order_id = request.GET.get('order_id') 
    total = request.GET.get('total')  
    uid = request.session.get('uid') 

    if order_id:
        try:
            order = Order.objects.get(id=order_id, login_id=uid)
            if not total:
                total = sum(item.product.price * item.quantity for item in order.items.all())
           
            if request.method == 'POST':
                order.payment_status = 'paid'
                order.save()

                cart_items = CartItem.objects.filter(login=order.login)
                cart_items.delete() 
                messages.success(request, 'Payment successfully')
                return redirect('/orderdetails')

        except Order.DoesNotExist:
            messages.error(request, 'Order not found or invalid order ID')
            return redirect('/orderdetails')
    else:
        messages.error(request, 'Payment successfully')
        return redirect('/orderdetails')
    return render(request, "photograph/payment.html", {'total': total})


def orderdetails(request):
    id = request.GET.get("id")  
    uid = request.session.get('uid')
    login = UserReg.objects.get(id=uid) 
    order = Order.objects.filter(login=login).first()
    ord = Order.objects.filter(login=login)  
    return render(request, 'photograph/details.html', {'ord': ord ,'login':login,'order':order})


def cancelorder(request):
    order_id = request.GET.get("id")  
    login_id = request.session.get('uid')
    login = UserReg.objects.get(id=login_id)
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return redirect('/orderdetails')
    if order.login != login:
        return redirect('/orderdetails')  
    if order.status in ["Shipped", "delivered", "Pending"]:
        order.status = "Cancelled"
        order.save()
        return redirect('/orderdetails')
    
def productreview(request):
    # product_id = request.GET.get("id")
    uid = request.session.get('uid')
    login = UserReg.objects.get(id=uid)
    product = Product.objects.filter().first()
   
    if request.POST:
        rating = request.POST.get('rating')
        review_text = request.POST.get('review_text')

        proriv=ProductReview.objects.create(login=login,product=product,rating=rating,review_text=review_text)
        proriv.save()
        messages.info(request,"sucessfully add the review")
        return redirect('/orderdetails')
    
    return render(request,"photograph/rating.html", {'product': product})
#####################################################################################
                             #   USER
#####################################################################################



def userreg(request):
    if request.POST:
        name = request.POST.get("name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        phone = request.POST.get("phone")
        address = request.POST.get("address")
        location = request.POST.get("location")
        pimage = request.FILES.get("pimage")
        password = request.POST.get("password")
        if UserReg.objects.filter(email=email).exists():
            messages.info(request,"email allready exist")
        else:
            log = Login.objects.create(email=email, password=password, userType='user')
            regs = UserReg.objects.create(login=log,name=name,email=email,password=password,phone=phone,address=address,location=location,pimage=pimage)
            regs.save()
            messages.info(request,"Register Sucessfully")
        return redirect('/login')
    return render(request,'user/register.html')

def photouserreg(request):
    if request.POST:
        name = request.POST.get("name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        phone = request.POST.get("phone")
        address = request.POST.get("address")
        location = request.POST.get("location")
        pimage = request.FILE.get("pimage")
        password = request.POST.get("password")
        if UserReg.objects.filter(email=email).exists():
            messages.info(request,"email allready exist")
        else:
            log = Login.objects.create(email=email, password=password, userType='user')
            regs = UserReg.objects.create(login=log,name=name,email=email,password=password,phone=phone,address=address,location=location,pimage=pimage)
            regs.save()
            messages.info(request,"Register Sucessfully")
        # return redirect('/login')
    return render(request,'photograph/userregister.html')
def userhome(request):
    uid = request.session.get('uid')
    uname=UserReg.objects.get(id=uid)
    print("----------------------")
    print(uname.name)
    return render(request,'user/userhome.html',{"uname":uname})


def addfeedback(request):
    uid = request.session.get('uid')
    if request.method == 'POST':
        content = request.POST.get("content")
        user_id = UserReg.objects.get(id=uid)
        efg = Feedback.objects.create(content=content, user=user_id)
        efg.save()
        messages.info(request,"Add Feedback success")
        return redirect('/userhome')

    return render(request, 'user/feedbackform.html')
def Addguest(request):
    uid = request.session.get('uid')
    if request.method == 'POST':
        name = request.POST.get("name")
        email = request.POST.get("email")
        user_id = UserReg.objects.get(id=uid)
        # log = Login.objects.create(email=email, password=password, userType='user')
        efg = Guest.objects.create(name=name, uid=user_id,email=email)
        efg.save()
        
        messages.info(request,"Add Guest success")
        return redirect('/userhome')

    return render(request, 'user/Addguest.html')

def gustgallarylist(request):
    email=request.session.get("email")
    uid=Guest.objects.get(email=email)
    paths=""
    print(uid)
    aha = Photo.objects.filter(eventid__rid__uid=uid.uid.id)
    return render(request, 'user/gustphotolist.html', {'aha': aha})

def gallarylist(request):
    uid=request.session.get("uid")
    myevent=Events.objects.filter(rid__uid=uid)
    paths=""
    print(myevent)
    aha = Photo.objects.filter(eventid__rid__uid=uid)
    return render(request, 'user/photolist.html', {'aha': aha})
def downloadgallarylist(request):

    aha = Photo.objects.all()
    return render(request, 'user/photolist.html', {'aha': aha})
def editimage(request):
    # aha = Photo.objects.all()
    return render(request, 'user/Editimage.html')

def download(request):
    id = request.GET.get('id')
    image = Photo.objects.get(id=id)
    image_path = os.path.join(settings.MEDIA_ROOT, image.image.name)
    if "mod" in request.POST:
        import moodcat
    elif "face" in request.POST:
        import facecata
    elif "spot" in request.POST:
        import spotdetection
    if os.path.exists(image_path):
        with open(image_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type="application/force-download")
            messages.info(request,'download successfully')
            response['Content-Disposition'] = f'attachment; filename={os.path.basename(image_path)}'
            return response
    return redirect("/gallarylist")


def photoreg(request):
    if request.POST:
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        address = request.POST.get("address")
        location = request.POST.get("location")
        pimage = request.FILES["pimage"]
        password = request.POST.get("password")
        spec=request.POST.get("spe")
        if UserReg.objects.filter(email=email).exists():
            messages.info(request,"email allready exist")
        else:
            log = Login.objects.create(email=email, password=password, userType='photographer')
            regs = PhotographrerReg.objects.create(login=log,name=name,email=email,phone=phone,address=address,location=location,pimage=pimage,password=password,specialization=spec)
            regs.save()
            messages.info(request,"Register Sucessfully")
        return redirect('/login')
    return render(request,'pho-reg.html')
def portpholio(request):
    if request.GET["id"] :

        id=request.GET["id"]
        data=PhotographrerReg.objects.get(id=id)
    return render(request,"user/Portpholio.html",{"data":data})
def photouserrequest(request):
    uid = request.session.get("uid")
    
    if request.POST:
        pid=request.session['pid'] 
        
        
        id=PhotographrerReg.objects.get(id=pid)
        requests=request.POST.get("req")
        uname=request.POST.get("uname")
        uid=UserReg.objects.get(email=uname)
        obj=Userrequest.objects.create(pid=id,uid=uid,req=requests)
        obj.save()
        messages.info(request,"Request Send Successfully")
    data=Userrequest.objects.filter(uid=uid)
    return render(request,"photograph/Saverequest.html",{"data":data})
    
def userrequest(request):
    uid = request.session.get("uid")
    if "rid" in request.GET:
        id=request.GET.get("rid")
        requests=request.POST.get("req")
        Userrequest.objects.filter(id=id).update(req=requests)
    if request.POST:
        
        id=request.GET["id"]
        id=PhotographrerReg.objects.get(id=id)
        requests=request.POST.get("req")
        uid=UserReg.objects.get(id=uid)
        obj=Userrequest.objects.create(pid=id,uid=uid,req=requests)
        obj.save()
        messages.info(request,"Request Send Successfully")
        return redirect('/userhome')  # Redirect to userhome page after successful form submission
    data=Userrequest.objects.filter(uid=uid)
    return render(request,"user/Saverequest.html",{"data":data})


def aphotoreg(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        location = request.POST.get('location')
        pimage = request.FILES.get('pimage')
        password = request.POST.get("password")
        # Set a default value for specialization since it's not in the form
        spec = "General"  # Default value for specialization
        if Login.objects.filter(email=email).exists():
            messages.info(request,"email allready exist")
        else:
            log = Login.objects.create(email=email, password=password, userType='asiphotographer')
            regs = PhotographrerReg.objects.create(login=log,name=name,email=email,phone=phone,address=address,location=location,pimage=pimage,password=password,specialization=spec)
            regs.save()
            messages.info(request,"Register Sucessfully")
        return redirect('/login')
    return render(request,'aspho-reg.html')
def userhome(request):
    uid = request.session.get('uid')
    uname=UserReg.objects.get(id=uid)
    print("----------------------")
    print(uname.name)
    return render(request,'user/userhome.html',{"uname":uname})


def add_product(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        category = request.POST.get('category')
        price = request.POST.get('price')
        description = request.POST.get('description')
        image = request.FILES.get('image')

        product = Product(name=name, category=category, price=price, description=description, image=image)
        product.save()

        return redirect('/adminhome/')  

    return render(request, 'admin/add_product.html')

def productlist(request):
    print("+++++++++++++++++++++++++++++")
    if "sub" in request.POST:
        data=request.POST.get("datas")
        print("########")
        print(data)
        if data:
            pro = PhotographrerReg.objects.filter(Q(name__icontains=data) | 
                    Q(location__icontains=data) | 
                    Q(specialization__icontains=data))
        else:
            pro = PhotographrerReg.objects.all()
    else:
        pro = PhotographrerReg.objects.all()
    return render(request,"admin/productlist.html",{"pro":pro})


def delete_dataadmin(request):
    id=request.GET.get('id')
    PhotographrerReg.objects.filter(id=id).delete()
    messages.info(request,"Deteted")
    return redirect('/productlist')


#user

def userproductlist(request):
    print("+++++++++++++++++++++++++++++")
    if "sub" in request.POST:
        data=request.POST.get("datas")
        print("########")
        print(data)
        if data:
            # Filter only main photographers, excluding assistant photographers
            pro = PhotographrerReg.objects.filter(
                Q(name__icontains=data) | 
                Q(location__icontains=data) | 
                Q(specialization__icontains=data)
            ).filter(login__userType='photographer')
        else:
            # Get all main photographers, excluding assistant photographers
            pro = PhotographrerReg.objects.filter(login__userType='photographer')
    else:
        # Get all main photographers, excluding assistant photographers
        pro = PhotographrerReg.objects.filter(login__userType='photographer')
    return render(request,"user/productlist.html",{"pro":pro})

def cartviewuser(request):
    id=request.POST.get('discount_value')
    uid = request.session.get("uid")
    view = CartItem.objects.filter(login=uid)
    total = 0
    
    for item in view:
        item.total = item.product.price * item.quantity
        total += item.total  # Accumulate total price of all items
    
    # Handle coupon application
    code = request.POST.get('code')  # Get the coupon code from POST request
    discount = 0  # Initialize discount value
       
    discounted_total = total - discount
    return render(request, "user/cart.html", {
        'view': view,
        'total': total,  # Original total before discount
        'discounted_total': discounted_total,  # Final total after discount
        'coupon_code': code,  
    })

def deletecartuser(request):
    id = request.GET.get('id')
    dee = CartItem.objects.filter(id=id).delete()
    messages.info(request,"sucessfully Remove")
    return redirect('/cartview')


def orderuser(request):
    price = request.GET.get('price')
    uid = request.session.get("uid")
    if not uid:
        return redirect('/login')

    login = UserReg.objects.get(id=uid)
    cart = CartItem.objects.filter(login=login)

    total = sum(i.product.price * i.quantity for i in cart)

    if request.POST:
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        postal_code = request.POST.get('postal_code')
        country = request.POST.get('country')

        order_ids = []  
        for item in cart:
            order = Order.objects.create(
                product=item.product,
                login=login,
                name=name,
                phone=phone,
                address=address,
                city=city,
                state=state,
                postal_code=postal_code,
                country=country
            )
            order_ids.append(order.id)

        cart.update(status="ordered")
        
        return redirect(f'/paymentuser?order_id={order_ids[-1]}&total={total}')

    return render(request, 'user/createorder.html', {'cart': cart, 'discounted_total':total })


def paymentuser(request):
    order_id = request.GET.get('order_id') 
    total = request.GET.get('total')  
    uid = request.session.get('uid') 

    if order_id:
        try:
            order = Order.objects.get(id=order_id, login_id=uid)
            if not total:
                total = sum(item.product.price * item.quantity for item in order.items.all())
           
            if request.method == 'POST':
                order.payment_status = 'paid'
                order.save()

                cart_items = CartItem.objects.filter(login=order.login)
                cart_items.delete() 
                messages.success(request, 'Payment successfully')
                return redirect('/orderdetailsuser')

        except Order.DoesNotExist:
            messages.error(request, 'Order not found or invalid order ID')
            return redirect('/orderdetails')
    else:
        messages.error(request, 'Payment successfully')
        return redirect('/orderdetailsuser')
    return render(request, "user/payment.html", {'total': total})


def orderdetailsuser(request):
    id = request.GET.get("id")  
    uid = request.session.get('uid')
    login = UserReg.objects.get(id=uid) 
    order = Order.objects.filter(login=login).first()
    ord = Order.objects.filter(login=login)  
    return render(request, 'user/detail.html', {'ord': ord ,'login':login,'order':order})


def cancelorderuser(request):
    order_id = request.GET.get("id")  
    login_id = request.session.get('uid')
    login = UserReg.objects.get(id=login_id)
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return redirect('/orderdetails')
    if order.login != login:
        return redirect('/orderdetails')  
    if order.status in ["Shipped", "delivered", "Pending"]:
        order.status = "Cancelled"
        order.save()
        return redirect('/orderdetailsuser')
    

def productreviewuser(request):
    # product_id = request.GET.get("id")
    uid = request.session.get('uid')
    login = UserReg.objects.get(id=uid)
    product = Product.objects.filter().first()
   
    if request.POST:
        rating = request.POST.get('rating')
        review_text = request.POST.get('review_text')

        proriv=ProductReview.objects.create(login=login,product=product,rating=rating,review_text=review_text)
        proriv.save()
        messages.info(request,"sucessfully add the review")
        return redirect('/orderdetailsuser')
    
    return render(request,"user/rating.html", {'product': product})


# admin order management

def orderlist(request):
    ordersli = Order.objects.all()  
    return render(request, 'admin/listorders.html', {'ordersli': ordersli})

def shipped(request):
    id = request.GET.get("id")
    order = Order.objects.filter(id=id).first()
    if order:
        order.status = "Shipped"
        order.save() 
        messages.info(request,'Shipped successfully')
    return redirect('/orderlist')

def delivered(request):
    id = request.GET.get("id")
    order = Order.objects.filter(id=id).first()
    if order:
        order.status = "delivered"
        order.save() 
        messages.info(request,'delivered successfully')
    return redirect('/orderlist')

def productreviewlist(request):
    rrv = ProductReview.objects.all()
    return render(request,"admin/reviewlist.html",{'rrv':rrv})

def deleteriv(request):
    id = request.GET.get('id')
    delete = ProductReview.objects.filter(id=id).delete()
    messages.info(request,"sucessfully Remove")
    return redirect('/productreviewlist')

###################################################################

def viewrequestuser(request):
    id=request.session['pid']
    requ = Userrequest.objects.filter(pid_id=id)
    return render(request,"photograph/Viewrequest.html",{'requ':requ})

def delete_request(request):
    request_id = request.GET.get('id')
    if request_id:
        try:
            # Get the request to delete
            user_request = Userrequest.objects.get(id=request_id)
            # Check if the request belongs to the logged-in photographer
            if user_request.pid.id == request.session.get('pid'):
                user_request.delete()
                messages.success(request, "Request deleted successfully!")
            else:
                messages.error(request, "You don't have permission to delete this request.")
        except Userrequest.DoesNotExist:
            messages.error(request, "Request not found.")
    return redirect('/viewrequestuser')

def replyrequest(request):
    id=request.session['pid']
    if request.POST:
        rep=request.POST.get("rep")
        id=request.GET.get("id")
        requ = Userrequest.objects.filter(id=id).update(reply=rep)
    data=Userrequest.objects.filter(pid=id)
    return render(request,"photograph/replyrequest.html",{"data":data})
def Viewevent(request):
    id=request.session.get('pid')
    print(id)
    data=Events.objects.filter(rid__pid=id)
    print(data)
    return render(request,"photograph/Viewevent.html",{"data":data})

def publish_event(request):
    event_id = request.GET.get('id')
    if event_id:
        event = Events.objects.get(id=event_id)
        event.status = 'published'
        event.save()
        messages.success(request, f"Event '{event.Event}' has been published successfully!")
    return redirect('/viewevent')

def unpublish_event(request):
    event_id = request.GET.get('id')
    if event_id:
        event = Events.objects.get(id=event_id)
        event.status = 'unpublished'
        event.save()
        messages.success(request, f"Event '{event.Event}' has been unpublished successfully!")
    return redirect('/viewevent')

def event_details(request):
    event_id = request.GET.get('id')
    if not event_id:
        messages.error(request, "No event specified")
        return redirect('/view_published_events')
    
    try:
        # Get the event details
        event = Events.objects.get(id=event_id)
        
        # Get assigned photographers if any
        assigned_photographers = []
        assignments = Assignassistance.objects.filter(evid=event)
        for assignment in assignments:
            if assignment.pid:
                assigned_photographers.append({
                    'name': assignment.pid.name,
                    'specialization': assignment.pid.specialization,
                    'location': assignment.pid.location
                })
            
            # Get assistant photographer details if assigned
            if assignment.asisst:
                try:
                    assistant = AsiPhotographrerReg.objects.get(id=assignment.asisst)
                    assigned_photographers.append({
                        'name': assistant.name,
                        'specialization': assistant.specialization,
                        'location': assistant.location,
                        'is_assistant': True
                    })
                except AsiPhotographrerReg.DoesNotExist:
                    pass
        
        # Get event applications if any
        applications = EventApplication.objects.filter(event=event)
        
        # Get related photos if any
        photos = Photo.objects.filter(eventid=event)
        
        context = {
            "event": event,
            "assigned_photographers": assigned_photographers,
            "applications": applications,
            "photos": photos
        }
        
        return render(request, "asphotograph/event_details.html", context)
    
    except Events.DoesNotExist:
        messages.error(request, "Event not found")
        return redirect('/view_published_events')
def view_published_events(request):
    events = Events.objects.filter(status='published')
    return render(request, "asphotograph/view_events.html", {"events": events})

def apply_event(request):
    event_id = request.GET.get('id')
    if not event_id:
        messages.error(request, "No event specified")
        return redirect('/view_published_events')
    
    try:
        event = Events.objects.get(id=event_id)
        uid = request.session.get('uid')
        
        if not uid:
            messages.error(request, "You must be logged in to apply for events")
            return redirect('/login')
        
        # Get the assistant photographer using AsiPhotographrerReg model
        try:
            photographer = AsiPhotographrerReg.objects.get(id=uid)
        except AsiPhotographrerReg.DoesNotExist:
            # If the user is not an assistant photographer
            photographer_reg = PhotographrerReg.objects.get(id=uid)
            # Create or get an AsiPhotographrerReg instance for this photographer
            photographer, created = AsiPhotographrerReg.objects.get_or_create(
                email=photographer_reg.email,
                defaults={
                    'login': photographer_reg.login,
                    'name': photographer_reg.name,
                    'phone': photographer_reg.phone,
                    'address': photographer_reg.address,
                    'location': photographer_reg.location,
                    'password': photographer_reg.password,
                    'specialization': photographer_reg.specialization,
                    'pimage': photographer_reg.pimage
                }
            )
        
        if request.method == 'POST':
            message = request.POST.get('message', '')
            
            # Check if already applied
            existing_application = EventApplication.objects.filter(
                event=event, 
                photographer=photographer
            ).first()
            
            if existing_application:
                messages.info(request, "You have already applied for this event")
            else:
                # Create new application
                EventApplication.objects.create(
                    event=event,
                    photographer=photographer,
                    message=message
                )
                messages.success(request, f"Successfully applied for event: {event.Event}")
            
            return redirect('/view_published_events')
        
        return render(request, "asphotograph/apply_event.html", {"event": event})
    
    except Events.DoesNotExist:
        messages.error(request, "Event not found")
        return redirect('/view_published_events')
    except PhotographrerReg.DoesNotExist:
        messages.error(request, "Photographer profile not found")
        return redirect('/login')

def Addevent(request):
    uid = request.session.get("pid")
    
    if request.POST:
        
        rid=request.GET["rid"]
        rid=Userrequest.objects.get(id=rid)
        name=request.POST.get("title")
        dis=request.POST.get("description")
        date=request.POST.get("date")
        time=request.POST.get("time")
        location=request.POST.get("location")
        obj=Events.objects.create(rid=rid,Event=name,Dis=dis,date=date,time=time,location=location)
        obj.save()
        messages.info(request,"Event Created Successfully")
        return redirect('/photohome')  # Redirect to photohome after successful event creation
    data=Userrequest.objects.filter(uid=uid)
    return render(request,"photograph/AddEvent.html",{"data":data})
def Assistance(request):
    id=request.GET.get('id')
    uid=request.session.get("pid")
    
    # Get the event
    event = Events.objects.get(id=id)
    
    # Get assistant photographers who have applied for this event
    applied_assistants = []
    applications = EventApplication.objects.filter(event=event)
    
    for application in applications:
        # Get the corresponding PhotographrerReg record if it exists
        try:
            photographer_reg = PhotographrerReg.objects.get(email=application.photographer.email)
            applied_assistants.append({
                'id': photographer_reg.id,  # Use the PhotographrerReg ID for assignment
                'name': application.photographer.name,
                'applied': True,
                'message': application.message,
                'email': application.photographer.email
            })
        except PhotographrerReg.DoesNotExist:
            # If no matching PhotographrerReg exists, create one
            login_obj = application.photographer.login
            if not login_obj:
                # Create a login object if needed
                login_obj, created = Login.objects.get_or_create(
                    email=application.photographer.email,
                    defaults={
                        'password': application.photographer.password,
                        'userType': 'asiphotographer'
                    }
                )
            
            # Create a PhotographrerReg record
            photographer_reg = PhotographrerReg.objects.create(
                login=login_obj,
                name=application.photographer.name,
                email=application.photographer.email,
                phone=application.photographer.phone,
                address=application.photographer.address,
                location=application.photographer.location,
                password=application.photographer.password,
                specialization=application.photographer.specialization,
                pimage=application.photographer.pimage
            )
            
            applied_assistants.append({
                'id': photographer_reg.id,
                'name': application.photographer.name,
                'applied': True,
                'message': application.message,
                'email': application.photographer.email
            })
    
    # Only show assistant photographers who have applied
    assistants_list = applied_assistants
    
    if request.POST:
        asid=request.POST.get("ass")
        
        # Create assignment
        Assignassistance.objects.create(pid_id=uid, evid_id=id, asisst=asid)
        messages.success(request, "Assistant photographer assigned successfully!")
    
    data=Assignassistance.objects.filter(evid_id=id)
    return render(request, "photograph/AssignAssistance.html", {
        "assistants": assistants_list,
        "data": data,
        "event": event
    })

def downloadusergalary(request):
    uid=request.session.get("uid")
    myevent=Events.objects.filter(rid__uid=uid)
    paths=""
    print(myevent)
    if "id" in request.GET:
        id=request.GET.get("id")
    
        # Get event images
        event_images = Photo.objects.filter(eventid_id=id)
        
        # Get photographer ID from the event
        event = Events.objects.get(id=id)
        photographer_id = event.rid.pid.id
        
        # Get exported images from selected_photos folder
        export_dir = os.path.join(settings.MEDIA_ROOT, 'selected_photos', f'pid_{photographer_id}')
        exported_images = []
        if os.path.exists(export_dir):
            exported_images = [os.path.join(export_dir, f) for f in os.listdir(export_dir) 
                             if os.path.isfile(os.path.join(export_dir, f))]
        
        # Create unique zip filename
        zip_filename = f"event_{id}_images.zip"
        zip_path = os.path.join(settings.MEDIA_ROOT, zip_filename)
        
        # Create ZIP file with both event images and exported images
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            # Add event images
            for image in event_images:
                image_path = os.path.join(settings.MEDIA_ROOT, image.image.name)
                if os.path.exists(image_path):
                    zipf.write(image_path, f'event_images/{os.path.basename(image_path)}')
            
            # Add exported images
            for image_path in exported_images:
                if os.path.exists(image_path):
                    zipf.write(image_path, f'exported_images/{os.path.basename(image_path)}')
        
        return redirect('/media/'+str(zip_filename))

    return render(request,"user/Downloadimagegalary.html",{"event":myevent})

def photoprofile(request):
    print("Accessing photoprofile view")
    pid = request.session.get("pid")
    print(f"Session pid: {pid}")
    
    # Check if user is logged in
    if not pid:
        print("No pid found in session, redirecting to login")
        messages.error(request, "Please login to view your profile")
        return redirect('/photographerlogin')
    
    try:
        print(f"Attempting to fetch photographer with id: {pid}")
        uname = PhotographrerReg.objects.get(id=pid)
        print(f"Photographer found: {uname.name}, ID: {pid}")
        print(f"Rendering profile template with photographer data")
        return render(request, 'photograph/profile.html', {'uname': uname})
    except Exception as e:
        print(f"Error loading profile: {str(e)}")
        messages.error(request, f"Error loading profile data: {str(e)}")
        return redirect('/photohome')

def test_session(request):
    # Debug view to check session data
    pid = request.session.get("pid")
    session_data = {
        'pid': pid,
        'is_logged_in': pid is not None
    }
    
    if pid:
        try:
            photographer = PhotographrerReg.objects.get(id=pid)
            session_data['photographer'] = {
                'name': photographer.name,
                'email': photographer.email,
                'id': photographer.id
            }
        except Exception as e:
            session_data['error'] = str(e)
    
    return render(request, 'test_session.html', {'session_data': session_data})

def test_login(request):
    return render(request, 'test_login.html')

def test_login_action(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        print(f"Test login attempt with email: {email}")
        
        try:
            user = PhotographrerReg.objects.get(email=email, password=password)
            print(f"User found: {user.name}, ID: {user.id}")
            
            # Set session data
            request.session['pid'] = user.id
            print(f"Session pid set to: {user.id}")
            
            messages.success(request, f"Welcome {user.name}! You are now logged in.")
            return redirect('/photoprofile')
        except Exception as e:
            print(f"Login error: {str(e)}")
            messages.error(request, "Invalid email or password. Please try again.")
            return redirect('/test-login')
    else:
        return redirect('/test-login')

# AI Processing Functions
import json
import os
import time
import uuid
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import threading
import sys

# Add the AI module to the path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'ai'))

# Import the processor module
try:
    from ai.processor import web_interface_process, process_images_async
except ImportError as e:
    print(f"Error importing processor module: {e}")

def test_view(request):
    """
    A simple test view to verify routing is working.
    """
    return render(request, 'test.html')

def ai_test_view(request):
    """
    View function for testing AI processing functionality.
    """
    return render(request, 'ai_test.html')

def ai_simple_test_view(request):
    """
    A simpler view function for testing AI processing with minimal UI.
    """
    return render(request, 'ai_simple_test.html')

@csrf_exempt
@require_POST
def process_ai(request):
    """
    Process AI requests for image analysis.
    """
    try:
        # Create a unique ID for this processing job
        job_id = str(uuid.uuid4())
        
        # For debugging
        print(f"Request method: {request.method}")
        print(f"Request FILES: {request.FILES}")
        print(f"Request POST: {request.POST}")
        
        # Check if we're processing for a specific photographer
        photographer_id = request.POST.get('photographer_id')
        
        if photographer_id:
            print(f"Processing images for photographer ID: {photographer_id}")
            
            # Create directory for this job
            job_dir = os.path.join(settings.MEDIA_ROOT, 'ai', job_id)
            os.makedirs(job_dir, exist_ok=True)
            
            # Create a status file to track progress
            status_file = os.path.join(job_dir, 'status.json')
            with open(status_file, 'w') as f:
                json.dump({
                    'status': 'processing',
                    'progress': 0,
                    'started_at': time.time(),
                    'photographer_id': photographer_id
                }, f)
            
            # Start processing in a background thread using processor.py
            def run_processor():
                try:
                    print(f"Starting web_interface_process for photographer {photographer_id}")
                    # Update status to indicate we're starting
                    update_status(job_id, 'processing', 10, message="Starting AI processing")
                    
                    # OPTION 1: Process all files in the directory (regardless of database)
                    # Get the directory path for this photographer
                    photographer_dir = os.path.join(settings.MEDIA_ROOT, f'photos/photographer_{photographer_id}')
                    
                    # Check if directory exists
                    if not os.path.exists(photographer_dir):
                        print(f"Directory does not exist: {photographer_dir}")
                        update_status(job_id, 'failed', 0, error=f"Directory not found: {photographer_dir}")
                        return
                    
                    # Get all image files in the directory
                    image_paths = []
                    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
                    
                    print(f"Scanning directory for gallery: {photographer_dir}")
                    for filename in os.listdir(photographer_dir):
                        file_path = os.path.join(photographer_dir, filename)
                        if os.path.isfile(file_path) and any(filename.lower().endswith(ext) for ext in valid_extensions):
                            image_paths.append(file_path)
                            print(f"Added to processing list: {file_path}")
                    
                    # Check if we have any images to process
                    if not image_paths:
                        print("No valid images found in the directory for this photographer")
                        update_status(job_id, 'failed', 0, error="No valid images found in the directory")
                        return
                    
                    print(f"Found {len(image_paths)} valid images to process")
                    
                    # Ensure output directory exists
                    output_dir = os.path.join(settings.MEDIA_ROOT, 'ai', str(photographer_id))
                    if not os.path.exists(output_dir):
                        print(f"Output directory does not exist, creating: {output_dir}")
                        os.makedirs(output_dir, exist_ok=True)
                    
                    # Run the processor with the list of image paths
                    print(f"About to call web_interface_process with {len(image_paths)} images...")
                    result = web_interface_process(photographer_id, image_paths=image_paths)
                    print(f"web_interface_process returned: {result}")
                    
                    # Update status based on result
                    if result['status'] == 'success':
                        update_status(job_id, 'completed', 100, message=result['message'], result=result)
                    else:
                        update_status(job_id, 'failed', 0, error=result['message'], result=result)
                        
                except Exception as e:
                    print(f"Error in run_processor: {str(e)}")
                    traceback.print_exc()
                    update_status(job_id, 'failed', 0, error=str(e))
            # Start the background thread
            threading.Thread(target=run_processor).start()
            
            # Return response immediately with processing status
            return JsonResponse({
                'status': 'started',
                'message': f'Processing started for photographer {photographer_id}',
                'job_id': job_id
            })
            
        # Get the image file from the request
        image_file = request.FILES.get('image')
        
        # If no image file is provided, check if we have a job_id parameter for testing
        if not image_file:
            # For testing purposes, allow creating a job without an image
            if request.POST.get('test_mode') == 'true':
                job_id = request.POST.get('job_id', job_id)
                
                # Create directory for this job
                job_dir = os.path.join(settings.MEDIA_ROOT, 'ai', job_id)
                os.makedirs(job_dir, exist_ok=True)
                
                # Create a status file to track progress
                status_file = os.path.join(job_dir, 'status.json')
                with open(status_file, 'w') as f:
                    json.dump({
                        'status': 'processing',
                        'progress': 0,
                        'started_at': time.time()
                    }, f)
                
                # Start a simulated processing task
                threading.Thread(target=lambda: simulate_ai_processing(job_id)).start()
                
                return JsonResponse({
                    'job_id': job_id,
                    'status': 'processing',
                    'message': 'Test processing started'
                })
            else:
                return JsonResponse({'error': 'No image file provided and no photographer_id specified'}, status=400)
        
        # Create directory for this job
        job_dir = os.path.join(settings.MEDIA_ROOT, 'ai', job_id)
        os.makedirs(job_dir, exist_ok=True)
        
        # Save the image
        image_path = os.path.join(job_dir, image_file.name)
        with open(image_path, 'wb+') as destination:
            for chunk in image_file.chunks():
                destination.write(chunk)
        
        # Create a status file to track progress
        status_file = os.path.join(job_dir, 'status.json')
        with open(status_file, 'w') as f:
            json.dump({
                'status': 'processing',
                'progress': 0,
                'started_at': time.time()
            }, f)
        
        # Start processing in a background thread
        threading.Thread(target=lambda: process_image_task(job_id, image_path)).start()
        
        return JsonResponse({
            'job_id': job_id,
            'status': 'processing',
            'message': 'Processing started'
        })
        
    except Exception as e:
        print(f"Error in process_ai: {str(e)}")
        return JsonResponse({
            'error': str(e)
        }, status=500)

def simulate_ai_processing(job_id):
    """
    Simulate AI processing for testing purposes.
    """
    try:
        # Simulate AI processing with delays
        update_status(job_id, 'processing', 25)
        time.sleep(2)  # Simulate processing time
        
        update_status(job_id, 'processing', 50)
        time.sleep(2)
        
        update_status(job_id, 'processing', 75)
        time.sleep(2)
        
        # Create a sample result file
        job_dir = os.path.join(settings.MEDIA_ROOT, 'ai', job_id)
        result_file = os.path.join(job_dir, 'result.json')
        with open(result_file, 'w') as f:
            json.dump({
                'analysis': 'Sample AI analysis results',
                'objects_detected': ['person', 'car', 'tree'],
                'confidence_scores': [0.95, 0.87, 0.76]
            }, f)
        
        # Mark as complete
        update_status(job_id, 'completed', 100)
        
    except Exception as e:
        # Handle errors
        update_status(job_id, 'failed', 0, error=str(e))

def process_image_task(job_id, image_path):
    """
    Process an image in a background thread.
    """
    try:
        # Simulate AI processing with delays
        update_status(job_id, 'processing', 25)
        time.sleep(2)  # Simulate processing time
        
        update_status(job_id, 'processing', 50)
        time.sleep(2)
        
        update_status(job_id, 'processing', 75)
        time.sleep(2)
        
        # Create a sample result file
        job_dir = os.path.join(settings.MEDIA_ROOT, 'ai', job_id)
        result_file = os.path.join(job_dir, 'result.json')
        with open(result_file, 'w') as f:
            json.dump({
                'analysis': 'Sample AI analysis results',
                'objects_detected': ['person', 'car', 'tree'],
                'confidence_scores': [0.95, 0.87, 0.76]
            }, f)
        
        # Mark as complete
        update_status(job_id, 'completed', 100)
        
    except Exception as e:
        # Handle errors
        update_status(job_id, 'failed', 0, error=str(e))

def update_status(job_id, status, progress, error=None, message=None, result=None):
    """
    Update the status file for an AI processing job.
    """
    # Get the job directory
    job_dir = os.path.join(settings.MEDIA_ROOT, 'ai', str(job_id))
    status_file = os.path.join(job_dir, 'status.json')
    
    # Create the status data
    status_data = {
        'status': status,
        'progress': progress,
        'updated_at': time.time()
    }
    
    if error:
        status_data['error'] = error
    if message:
        status_data['message'] = message
    if result:
        status_data['result'] = result
    
    with open(status_file, 'w') as f:
        json.dump(status_data, f)

def check_ai_status(request):
    """
    Check the status of an AI processing job.
    """
    job_id = request.GET.get('job_id')
    if not job_id:
        return JsonResponse({
            'status': 'error',
            'message': 'No job ID provided'
        })
    
    # This is a placeholder for actual status checking
    # In a real implementation, you would look up the job status in a database or cache
    
    # For demo purposes, just return a success status
    return JsonResponse({
        'status': 'completed',
        'message': 'Processing completed successfully'
    })

# Get matching images for a face group
def get_matching_face_images(request):
    """API view to retrieve all matching images for a selected face group"""
    # Get parameters from request
    group_id = request.GET.get('group_id')
    photographer_id = request.session.get("pid")
    
    if not group_id or group_id == 'None':
        return JsonResponse({
            'status': 'error',
            'message': 'No valid group ID provided'
        })
    
    if not photographer_id:
        return JsonResponse({
            'status': 'error',
            'message': 'User not authenticated'
        })
    
    try:
        # Import the face_matcher module
        sys.path.append(os.path.join(settings.BASE_DIR, 'ai', 'face', 'repeted_cropped'))
        from face_matcher import get_matching_images_for_face, get_face_group_info
        
        # Get photographer's photo directory
        photographer_dir = os.path.join(settings.MEDIA_ROOT, f'photos/photographer_{photographer_id}')
        
        # Create temporary output directory for matching face images
        output_dir = os.path.join(settings.MEDIA_ROOT, 'matching_faces', str(photographer_id), f'group_{group_id}')
        os.makedirs(output_dir, exist_ok=True)
        
        # Get group info
        group_info = get_face_group_info(group_id)
        
        # Get matching images
        matching_images = get_matching_images_for_face(
            group_id=group_id,
            photographer_directory=photographer_dir, 
            output_directory=output_dir
        )
        
        # Format results for JSON response
        result_images = []
        for img_path, face_locations in matching_images:
            # Create a relative URL for the image
            img_filename = os.path.basename(img_path)
            img_rel_path = os.path.join('photos', f'photographer_{photographer_id}', img_filename)
            img_url = f"{settings.MEDIA_URL}{img_rel_path}"
            img_url = img_url.replace('\\', '/')
            
            result_images.append({
                'url': img_url,
                'name': img_filename,
                'faces': len(face_locations)
            })
        
        # Handle group name safely
        try:
            if group_info and 'label' in group_info:
                group_name = group_info.get('label')
            else:
                # Try to convert group_id to int safely
                int_group_id = int(group_id)
                group_name = f'Person {int_group_id + 1}'
        except (ValueError, TypeError):
            # If conversion fails, use a generic name
            group_name = f'Person (ID: {group_id})'
        
        # Return success response
        return JsonResponse({
            'status': 'success',
            'message': f'Found {len(result_images)} matching images',
            'group_id': group_id,
            'group_name': group_name,
            'images': result_images
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        
        return JsonResponse({
            'status': 'error',
            'message': f'Error retrieving matching face images: {str(e)}'
        })

# AI test view
def ai_test_view(request):
    """
    View function for testing AI processing functionality.
    """
    return render(request, 'ai_test.html')

def ai_simple_test_view(request):
    """
    A simpler view function for testing AI processing with minimal UI.
    """
    return render(request, 'ai_simple_test.html')

def editor_dashboard(request):
    pid = request.session.get("pid")
    if pid is None:
        return redirect('/')
    
    # OPTION 1: Display all files in the directory (regardless of database)
    # Get the directory path for this photographer
    photographer_dir = os.path.join(settings.MEDIA_ROOT, f'photos/photographer_{pid}')
    photos = []
    
    # Check if directory exists
    if os.path.exists(photographer_dir):
        # Get all image files in the directory
        valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
        media_url = settings.MEDIA_URL
        
        print(f"Scanning directory for editor dashboard: {photographer_dir}")
        for filename in os.listdir(photographer_dir):
            file_path = os.path.join(photographer_dir, filename)
            if os.path.isfile(file_path) and any(filename.lower().endswith(ext) for ext in valid_extensions):
                # Create a dictionary with the same structure as expected by the template
                relative_path = f'photos/photographer_{pid}/{filename}'
                url = f"{media_url}{relative_path}"
                photos.append({
                    'url': url,
                    'name': filename,
                    'id': filename  # Use filename as ID since these aren't in the database
                })
                print(f"Added to editor dashboard: {url}")
    
    # Check if AI processing has been done
    ai_processed = False
    captions = []
    
    # Output CSV from AI processing
    output_csv = os.path.join(settings.MEDIA_ROOT, 'ai', str(pid), 'image_captions.csv')
    
    if os.path.exists(output_csv):
        ai_processed = True
        try:
            with open(output_csv, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                headers = next(reader)  # Skip header row
                for row in reader:
                    if len(row) >= 5:  # Make sure the row has enough columns (path, caption, emotion, age, gender, race)
                        img_path = row[0]
                        caption = row[1]
                        emotion = row[2]
                        age = row[3]
                        gender = row[4]
                        race = row[5] if len(row) > 5 else ""
                        
                        # Get just the filename from the path
                        img_filename = os.path.basename(img_path)
                        
                        # Create the relative URL
                        img_rel_path = f'photos/photographer_{pid}/{img_filename}'
                        img_url = f"{settings.MEDIA_URL}{img_rel_path}"
                        img_url = img_url.replace('\\', '/')
                        
                        captions.append({
                            'url': img_url,
                            'name': img_filename,
                            'caption': caption,
                            'emotion': emotion,
                            'age': age,
                            'gender': gender,
                            'race': race
                        })
        except Exception as e:
            print(f"Error reading AI output CSV: {str(e)}")
    
    # Get detected faces
    face_groups = []
    random_faces = []
    
    detected_faces_dir = os.path.join(settings.BASE_DIR, 'ai', 'face', 'repeted_cropped', 'detected_faces')
    random_faces_dir = os.path.join(settings.BASE_DIR, 'ai', 'face', 'repeted_cropped', 'random_selection')
    
    # Check if random faces directory exists and load those images
    if os.path.exists(random_faces_dir):
        # Import emotion detection function
        try:
            import sys
            # Add the parent directory to the path if not already there
            parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            if parent_dir not in sys.path:
                sys.path.insert(0, parent_dir)
            
            from integrated_model import detect_emotion
            has_emotion_detection = True
            print("Successfully imported emotion detection for face analysis")
        except Exception as e:
            has_emotion_detection = False
            print(f"Error importing emotion detection: {e}")
        
        # Group counter for face groups
        face_group_counter = {}
        face_counter = 1  # Counter for simple "Face 1", "Face 2" naming
        
        # Try to load face group information from selection_metadata.json
        metadata_file = os.path.join(settings.BASE_DIR, 'media', 'ai', 'face', 'repeted_cropped', 'random_selection', 'selection_metadata.json')
        face_groups_metadata = {}
        
        try:
            if os.path.exists(metadata_file):
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                    if 'groups' in metadata:
                        face_groups_metadata = metadata['groups']
                        print(f"Loaded face groups metadata: {len(face_groups_metadata)} groups")
        except Exception as e:
            print(f"Error loading selection_metadata.json: {str(e)}")
        
        for filename in os.listdir(random_faces_dir):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
                # Analyze filename pattern - could be one of these patterns:
                # 1. "group_X_face_Y_groupZ.jpg" or 
                # 2. "Test_Person_face_X_groupY.jpg" or similar
                
                # First, try to find "face_" in the filename as that's common in both patterns
                group_id = None
                if 'face_' in filename:
                    # Extract the part after "face_"
                    face_part = filename.split('face_')[1]
                    # The first number after face_ should be the group ID
                    face_parts = face_part.split('_')
                    if face_parts and face_parts[0].isdigit():
                        group_id = face_parts[0]
                        print(f"Extracted group_id {group_id} from filename {filename}")
                
                # Face files are named face_X_Y.jpg where X is the group number and Y is the instance number
                parts = filename.split('_')
                face_group_counter_key = group_id if group_id else "unknown"
                
                if face_group_counter_key not in face_group_counter:
                    face_group_counter[face_group_counter_key] = 0
                face_group_counter[face_group_counter_key] += 1
                
                # Extract group information from the filename
                group_name = "Unknown Face"  # Default face group name
                
                # Group ID should have been extracted earlier when parsing the filename
                # If we have a valid group_id, use that
                if group_id:
                    # Check if we have a label for this group in metadata
                    if group_id in face_groups_metadata:
                        group_label = face_groups_metadata[group_id].get('label')
                        if group_label and group_label.strip():
                            group_name = group_label
                        else:
                            group_name = f"Face {group_id}"
                    else:
                        group_name = f"Face {group_id}"
                
                # If the filename starts with "Test_Person", use that as the group name
                if filename.startswith("Test_Person"):
                    group_name = "Test Person"
                    # If we didn't get a group_id but it's a Test_Person, use "0" as default
                    if not group_id and "0" in face_groups_metadata:
                        group_id = "0"
                
                # For filenames starting with "group_X", use that as the group name if no better name
                elif filename.startswith("group_") and parts[0] == "group" and len(parts) > 1 and parts[1].isdigit():
                    if group_name == "Unknown Face":  # Only override if we don't have a better name
                        group_name = f"Group {parts[1]}"
                    if not group_id:  # If we still don't have a group_id, use this
                        group_id = parts[1]
                
                random_faces.append({
                    'url': f"/media/ai/face/repeted_cropped/random_selection/{filename}",
                    'name': filename,
                    'group': group_name,  # Using group name from metadata if available
                    'group_id': group_id,  # Add group_id for linking with detected faces
                    'emotion': 'Unknown',
                    'age': 0,
                    'emotion_scores': {}
                })
                
                face_counter += 1  # Increment the face counter
        random_faces.sort(key=lambda x: (x['group_id'] if x['group_id'] is not None else float('inf')))
        print(f"Loaded {len(random_faces)} random face images")
    else:
        print(f"Random faces directory not found: {random_faces_dir}")
    
    # Load face groups if directory exists
    if os.path.exists(detected_faces_dir):
        # Group the face files by their prefix (face_X_Y.jpg where X is the group number)
        group_files = {}
        for filename in os.listdir(detected_faces_dir):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
                # Face files are named face_X_Y.jpg where X is the group number and Y is the instance number
                parts = filename.split('_')
                face_group_counter_key = parts[1] if len(parts) > 1 and parts[0] == 'face' else "unknown"
                
                if face_group_counter_key not in group_files:
                    group_files[face_group_counter_key] = []
                
                # Get the source image path if available (format: face_X_Y_source.jpg)
                source_image = None
                if len(parts) > 3:
                    source_parts = parts[3:]
                    if source_parts:
                        source_image = "_".join(source_parts)
                        # Remove the file extension if it's in the source parts
                        if "." in source_image:
                            source_image = source_image.split(".")[0]
                
                face_path = os.path.join('ai', 'face', 'repeted_cropped', 'detected_faces', filename)
                face_url = os.path.join(settings.MEDIA_URL, face_path).replace('\\', '/')
                
                # For local development, construct the URL correctly
                if settings.DEBUG:
                    face_url = f"/media/ai/face/repeted_cropped/detected_faces/{filename}"
                
                # Analyze face for emotion and age if emotion detection is available
                emotion_data = {
                    'dominant_emotion': 'Unknown',
                    'age': 0,
                    'emotion_scores': {}
                }
                
                if has_emotion_detection:
                    try:
                        # Get the full path to the face image
                        full_face_path = os.path.join(settings.BASE_DIR, 'ai', 'face', 'repeted_cropped', 'detected_faces', filename)
                        
                        # Analyze the face
                        print(f"Analyzing face in group {face_group_counter_key}: {filename}")
                        result = detect_emotion(full_face_path)
                        
                        if result:
                            emotion_data = {
                                'dominant_emotion': result.get('dominant_emotion', 'Unknown'),
                                'age': result.get('age', 0),
                                'emotion_scores': result.get('emotion', {})
                            }
                            print(f"Face analysis result: {emotion_data['dominant_emotion']}, Age: {emotion_data['age']}")
                    except Exception as e:
                        print(f"Error analyzing face {filename}: {str(e)}")
                
                group_files[face_group_counter_key].append({
                    'url': face_url,
                    'name': filename,
                    'source_image': source_image,
                    'emotion': emotion_data['dominant_emotion'],
                    'age': emotion_data['age'],
                    'emotion_scores': emotion_data['emotion_scores']
                })
                
        # Sort groups by group number
        sorted_group_nums = sorted(group_files.keys())
        
        # Convert the grouped files to our face_groups format
        for group_num in sorted_group_nums:
            group_name = f"Person {group_num}"  # Make it human-readable
            if group_num == 0:
                group_name = "Test Person"  # Group 0 is the test person
            
            # Sort faces within the group by their instance number (face_X_Y.jpg - sort by Y)
            try:
                # More robust sorting that handles different filename formats
                def get_sort_key(face_item):
                    try:
                        parts = face_item['name'].split('_')
                        # Check for face_X_Y.jpg format
                        if len(parts) > 2 and parts[0] == 'face':
                            # Try to extract the instance number (Y in face_X_Y.jpg)
                            return int(parts[2].split('.')[0])
                        # For other formats, fall back to alphabetical sorting
                        return 0
                    except (ValueError, IndexError):
                        # If any parsing errors occur, just return 0 as fallback
                        return 0
                
                group_files[group_num].sort(key=get_sort_key)
            except Exception as e:
                print(f"Error sorting face group {group_num}: {str(e)}")
                # If sorting fails, keep the original order
            
            face_groups.append({
                'name': group_name,
                'faces': group_files[group_num],
                'count': len(group_files[group_num]),
                'group_id': group_num  # Add group_id for linking with random faces
            })
    
    # Organize photos by emotion
    emotions_dict = {}
    for caption in captions:
        emotion = caption.get('emotion', 'Unknown')
        if emotion not in emotions_dict:
            emotions_dict[emotion] = []
        emotions_dict[emotion].append(caption)
    
    # Convert to list for template
    emotions_categorized = []
    for emotion, items in emotions_dict.items():
        emotions_categorized.append({
            'name': emotion,
            'count': len(items),
            'photos': items
        })
    
    # Sort emotions by count (descending)
    emotions_categorized.sort(key=lambda x: x['count'], reverse=True)
    
    # Prepare template context
    context = {
        'photos': photos,
        'ai_processed': ai_processed,
        'captions': captions,
        'face_groups': face_groups,
        'random_faces': random_faces,
        'emotions_categorized': emotions_categorized  # Add categorized emotions
    }
    
    return render(request, 'photograph/editor_dashboard.html', context)

def ban_photographer(request):
    """
    Temporarily ban a photographer from the platform
    """
    if request.GET.get('id'):
        photographer_id = request.GET.get('id')
        try:
            photographer = PhotographrerReg.objects.get(id=photographer_id)
            photographer.status = 'banned'
            photographer.save()
            messages.success(request, f'Photographer {photographer.name} has been banned successfully')
        except PhotographrerReg.DoesNotExist:
            messages.error(request, 'Photographer not found')
    return redirect('/productlist/')

def unban_photographer(request):
    """
    Unban a temporarily banned photographer
    """
    if request.GET.get('id'):
        photographer_id = request.GET.get('id')
        try:
            photographer = PhotographrerReg.objects.get(id=photographer_id)
            photographer.status = 'approved'
            photographer.save()
            messages.success(request, f'Photographer {photographer.name} has been unbanned successfully')
        except PhotographrerReg.DoesNotExist:
            messages.error(request, 'Photographer not found')
    return redirect('/productlist/')

# Face recognition functions
def run_face_recognition(request):
    """
    Run face recognition on uploaded images.
    """
    if request.method == 'POST':
        job_id = request.POST.get('job_id')
        if not job_id:
            return JsonResponse({'error': 'No job ID provided'}, status=400)
        
        job_dir = os.path.join(settings.MEDIA_ROOT, 'ai', job_id)
        if not os.path.exists(job_dir):
            return JsonResponse({'error': 'Job not found'}, status=404)
        
        # Simulate face recognition processing
        # In a real app, you would use a library like face_recognition here
        faces_data = {
            'faces': [
                {'id': 1, 'box': [100, 120, 200, 220], 'label': ''},
                {'id': 2, 'box': [300, 150, 400, 250], 'label': ''},
                {'id': 3, 'box': [500, 200, 600, 300], 'label': ''}
            ]
        }
        
        # Save faces data
        faces_file = os.path.join(job_dir, 'faces.json')
        with open(faces_file, 'w') as f:
            json.dump(faces_data, f)
        
        return JsonResponse({
            'success': True,
            'faces_count': len(faces_data['faces']),
            'faces': faces_data['faces']
        })
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

def save_face_labels(request):
    """
    Save labels for detected faces.
    """
    if request.method == 'POST':
        try:
            # Extract data from the request
            data = json.loads(request.body)
            face_labels = data.get('faceLabels', {})
            
            # In a real implementation, you would save these labels to your database
            # For example:
            # for face_id, label in face_labels.items():
            #     face = Face.objects.get(id=face_id)
            #     face.label = label
            #     face.save()
            
            # For now, we'll just return success
            return JsonResponse({'success': True})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

# Export selected images to exported_images folder
@csrf_exempt  # Temporarily exempt from CSRF to debug the issue
def export_images(request):
    """
    Export selected images to the exported_images folder.
    
    This endpoint handles POST requests with:
    - photos: A list of photo objects containing name and url
    
    Returns JSON response with:
    - success/failure status
    - message with export results
    - list of exported image filenames
    - list of skipped (duplicate) image filenames
    """
    print("Export images endpoint called")
    
    if request.method == 'POST':
        try:
            print("Request headers:", request.headers)
            print("Request body:", request.body.decode('utf-8'))
            
            # Parse the JSON request body
            data = json.loads(request.body)
            photos = data.get('photos', [])
            
            print(f"Received {len(photos)} photos to export")
            
            if not photos:
                return JsonResponse({
                    'success': False,
                    'message': 'No photos provided for export'
                })
            
            # Get photographer ID from session
            pid = request.session.get('pid')
            if not pid:
                print("No photographer ID found in session, using default")
                pid = "unknown"
                
            print(f"Photographer ID: {pid}")
                
            # Create export directory if it doesn't exist
            export_dir = os.path.join(settings.MEDIA_ROOT, 'exported_images')
            if not os.path.exists(export_dir):
                os.makedirs(export_dir, exist_ok=True)
                
            print(f"Export directory: {export_dir}")
                
            # Track statistics
            exported = []
            skipped = []
            failed = []
            
            # Process each selected photo
            for photo in photos:
                try:
                    photo_name = photo.get('name')
                    photo_url = photo.get('url')
                    
                    print(f"Processing photo: {photo_name}, URL: {photo_url}")
                    
                    # Skip if any required field is missing
                    if not photo_name or not photo_url:
                        failed.append(photo_name or "Unknown")
                        print(f"Missing required fields for photo: {photo}")
                        continue
                    
                    # Destination path
                    dest_path = os.path.join(export_dir, photo_name)
                    print(f"Destination path: {dest_path}")
                    
                    # Check if file already exists in destination (avoid duplicates)
                    if os.path.exists(dest_path):
                        skipped.append(photo_name)
                        print(f"Skipping duplicate file: {photo_name}")
                        continue
                    
                    # Try multiple approaches to find the source file
                    source_found = False
                    
                    # Approach 1: Use URL to find path (remove /media/ prefix)
                    if photo_url.startswith('/media/'):
                        url_path = photo_url[7:]  # Remove /media/ prefix
                        source_path = os.path.join(settings.MEDIA_ROOT, url_path)
                        print(f"Trying URL path: {source_path}")
                        if os.path.exists(source_path):
                            source_found = True
                    
                    # Approach 2: Look in photographer's directory
                    if not source_found:
                        photographer_dir = os.path.join(settings.MEDIA_ROOT, f'photos/photographer_{pid}')
                        source_path = os.path.join(photographer_dir, photo_name)
                        print(f"Trying photographer dir: {source_path}")
                        if os.path.exists(source_path):
                            source_found = True
                    
                    # Approach 3: Search in AI directory for face-matched photos
                    if not source_found:
                        ai_dir = os.path.join(settings.BASE_DIR, 'ai', 'face', 'matched_images')
                        source_path = os.path.join(ai_dir, photo_name)
                        print(f"Trying AI matched directory: {source_path}")
                        if os.path.exists(source_path):
                            source_found = True
                    
                    # Approach 4: Look for file directly in media folder
                    if not source_found:
                        source_path = os.path.join(settings.MEDIA_ROOT, photo_name)
                        print(f"Trying media root: {source_path}")
                        if os.path.exists(source_path):
                            source_found = True
                    
                    # Approach 5: Search recursively through the media folder
                    if not source_found:
                        print(f"Searching recursively for {photo_name} in {settings.MEDIA_ROOT}")
                        for root, dirs, files in os.walk(settings.MEDIA_ROOT):
                            if photo_name in files:
                                source_path = os.path.join(root, photo_name)
                                print(f"Found file at: {source_path}")
                                source_found = True
                                break
                    
                    if not source_found:
                        failed.append(photo_name)
                        print(f"Could not find source file for: {photo_name}")
                        continue
                    
                    # Copy the file
                    import shutil
                    print(f"Copying file from {source_path} to {dest_path}")
                    shutil.copy2(source_path, dest_path)
                    exported.append(photo_name)
                    print(f"Successfully exported: {photo_name}")
                    
                except Exception as e:
                    print(f"Error exporting {photo.get('name', 'Unknown')}: {str(e)}")
                    traceback.print_exc()
                    failed.append(photo.get('name', 'Unknown'))
            
            # Prepare response message
            if exported:
                message = f"Successfully exported {len(exported)} image(s)."
                if skipped:
                    message += f" Skipped {len(skipped)} duplicate(s)."
                if failed:
                    message += f" Failed to export {len(failed)} image(s)."
                success = True
            else:
                if skipped and not failed:
                    message = f"All {len(skipped)} selected image(s) were already exported."
                    success = True
                else:
                    message = "No images were exported."
                    if failed:
                        message += f" Failed to export {len(failed)} image(s)."
                    success = False
            
            print(f"Export result: {message}")
            
            # Return success response with stats
            response_data = {
                'success': success,
                'message': message,
                'exported': exported,
                'skipped': skipped,
                'failed': failed
            }
            print(f"Sending response: {response_data}")
            return JsonResponse(response_data)
                
        except Exception as e:
            error_message = f"Error in export_images view: {str(e)}"
            print(error_message)
            traceback.print_exc()
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}'
            })
    
    # Return error for non-POST requests
    return JsonResponse({
        'success': False,
        'message': 'Only POST requests are accepted'
    })

# Export selected photos from face matching modal to selected_photos folder
@csrf_exempt  # Consider removing this after debugging
def export_selected_photos(request):
    """
    Export selected photos from the face matching modal to the selected_photos folder.
    
    This endpoint handles POST requests with:
    - photos: A list of photo objects containing name and url
    
    Returns JSON response with:
    - success/failure status
    - message with export results
    - list of exported image filenames
    - list of skipped (duplicate) image filenames
    """
    print("Export selected photos endpoint called")
    
    if request.method == 'POST':
        try:
            print("Request headers:", request.headers)
            print("Request body:", request.body.decode('utf-8'))
            
            # Parse the JSON request body
            data = json.loads(request.body)
            photos = data.get('photos', [])
            
            print(f"Received {len(photos)} photos to export")
            
            if not photos:
                return JsonResponse({
                    'success': False,
                    'message': 'No photos provided for export'
                })
            
            # Get photographer ID from session
            pid = request.session.get('pid')
            if not pid:
                print("No photographer ID found in session, using default")
                pid = "unknown"
                
            print(f"Photographer ID: {pid}")
                
            # Create export directory with photographer ID prefix
            export_dir = os.path.join(settings.MEDIA_ROOT, 'selected_photos', f'pid_{pid}')
            if not os.path.exists(export_dir):
                os.makedirs(export_dir, exist_ok=True)
                
            print(f"Export directory: {export_dir}")
                
            # Track statistics
            exported = []
            skipped = []
            failed = []
            
            # Process each selected photo
            for photo in photos:
                try:
                    photo_name = photo.get('name')
                    photo_url = photo.get('url')
                    
                    print(f"Processing photo: {photo_name}, URL: {photo_url}")
                    
                    # Skip if any required field is missing
                    if not photo_name or not photo_url:
                        failed.append(photo_name or "Unknown")
                        print(f"Missing required fields for photo: {photo}")
                        continue
                    
                    # Destination path
                    dest_path = os.path.join(export_dir, photo_name)
                    print(f"Destination path: {dest_path}")
                    
                    # Check if file already exists in destination (avoid duplicates)
                    if os.path.exists(dest_path):
                        skipped.append(photo_name)
                        print(f"Skipping duplicate file: {photo_name}")
                        continue
                    
                    # Try multiple approaches to find the source file
                    source_found = False
                    
                    # Approach 1: Use URL to find path (remove /media/ prefix)
                    if photo_url.startswith('/media/'):
                        url_path = photo_url[7:]  # Remove /media/ prefix
                        source_path = os.path.join(settings.MEDIA_ROOT, url_path)
                        print(f"Trying URL path: {source_path}")
                        if os.path.exists(source_path):
                            source_found = True
                    
                    # Approach 2: Look in photographer's directory
                    if not source_found:
                        photographer_dir = os.path.join(settings.MEDIA_ROOT, f'photos/photographer_{pid}')
                        source_path = os.path.join(photographer_dir, photo_name)
                        print(f"Trying photographer dir: {source_path}")
                        if os.path.exists(source_path):
                            source_found = True
                    
                    # Approach 3: Search in AI directory for face-matched photos
                    if not source_found:
                        ai_dir = os.path.join(settings.BASE_DIR, 'ai', 'face', 'matched_images')
                        source_path = os.path.join(ai_dir, photo_name)
                        print(f"Trying AI matched directory: {source_path}")
                        if os.path.exists(source_path):
                            source_found = True
                    
                    # Approach 4: Look for file directly in media folder
                    if not source_found:
                        source_path = os.path.join(settings.MEDIA_ROOT, photo_name)
                        print(f"Trying media root: {source_path}")
                        if os.path.exists(source_path):
                            source_found = True
                    
                    # Approach 5: Search recursively through the media folder
                    if not source_found:
                        print(f"Searching recursively for {photo_name} in {settings.MEDIA_ROOT}")
                        for root, dirs, files in os.walk(settings.MEDIA_ROOT):
                            if photo_name in files:
                                source_path = os.path.join(root, photo_name)
                                print(f"Found file at: {source_path}")
                                source_found = True
                                break
                    
                    if not source_found:
                        failed.append(photo_name)
                        print(f"Could not find source file for: {photo_name}")
                        continue
                    
                    # Copy the file
                    import shutil
                    print(f"Copying file from {source_path} to {dest_path}")
                    shutil.copy2(source_path, dest_path)
                    exported.append(photo_name)
                    print(f"Successfully exported: {photo_name}")
                    
                except Exception as e:
                    print(f"Error exporting {photo.get('name', 'Unknown')}: {str(e)}")
                    traceback.print_exc()
                    failed.append(photo.get('name', 'Unknown'))
            
            # Prepare response message
            if exported:
                message = f"Successfully exported {len(exported)} image(s) to pid_{pid} folder."
                if skipped:
                    message += f" Skipped {len(skipped)} duplicate(s)."
                if failed:
                    message += f" Failed to export {len(failed)} image(s)."
                success = True
            else:
                if skipped and not failed:
                    message = f"All {len(skipped)} selected image(s) were already exported."
                    success = True
                else:
                    message = "No images were exported."
                    if failed:
                        message += f" Failed to export {len(failed)} image(s)."
                    success = False
            
            print(f"Export result: {message}")
            
            # Return success response with stats
            response_data = {
                'success': success,
                'message': message,
                'exported': exported,
                'skipped': skipped,
                'failed': failed
            }
            print(f"Sending response: {response_data}")
            return JsonResponse(response_data)
                
        except Exception as e:
            error_message = f"Error in export_selected_photos view: {str(e)}"
            print(error_message)
            traceback.print_exc()
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}'
            })
    
    # Return error for non-POST requests
    return JsonResponse({
        'success': False,
        'message': 'Only POST requests are accepted'
    })

def my_photographers(request):
    """
    View function to display all photographers assigned to the client's events.
    This includes both the main photographer and assistant photographers.
    """
    uid = request.session.get('uid')
    if not uid:
        messages.error(request, "You must be logged in to view your photographers")
        return redirect('/login')
    
    # Get all events for this user
    user_events = Events.objects.filter(rid__uid=uid)
    
    # List to store event data with photographer information
    events_with_photographers = []
    
    for event in user_events:
        # Get the main photographer
        main_photographer = event.rid.pid
        
        # Get assistant photographers assigned to this event
        assistants = Assignassistance.objects.filter(evid=event)
        
        assistant_photographers = []
        for assistant in assistants:
            if assistant.asisst:  # Check if assistant ID is valid
                try:
                    assistant_photographer = PhotographrerReg.objects.get(id=assistant.asisst)
                    assistant_photographers.append({
                        'id': assistant_photographer.id,  # Use the PhotographrerReg ID for assignment
                        'name': assistant_photographer.name,
                        'email': assistant_photographer.email,
                        'phone': assistant_photographer.phone,
                        'specialization': assistant_photographer.specialization,
                        'image': assistant_photographer.pimage.url if assistant_photographer.pimage else None
                    })
                except PhotographrerReg.DoesNotExist:
                    # Skip if assistant photographer doesn't exist
                    pass
        
        # Add event with photographer information to the list
        events_with_photographers.append({
            'event': {
                'id': event.id,
                'name': event.Event,
                'description': event.Dis,
                'date': event.date,
                'time': event.time,
                'location': event.location
            },
            'main_photographer': {
                'id': main_photographer.id,
                'name': main_photographer.name,
                'email': main_photographer.email,
                'phone': main_photographer.phone,
                'specialization': main_photographer.specialization,
                'image': main_photographer.pimage.url if main_photographer.pimage else None
            },
            'assistant_photographers': assistant_photographers
        })
    
    return render(request, 'user/my_photographers.html', {
        'events_with_photographers': events_with_photographers
    })

def download_exported_images(request):
    """
    View function to download exported images from the selected_photos folder as a zip file.
    This allows clients to download images that photographers have exported for them.
    """
    uid = request.session.get('uid')
    if not uid:
        messages.error(request, "You must be logged in to download images")
        return redirect('/login')
    
    # Get the photographer ID from the request
    photographer_id = request.GET.get('photographer_id')
    if not photographer_id:
        messages.error(request, "Photographer ID is required")
        return redirect('/my-photographers')
    
    # Define the path to the exported images folder
    export_dir = os.path.join(settings.MEDIA_ROOT, 'selected_photos', f'pid_{photographer_id}')
    
    # Check if the directory exists
    if not os.path.exists(export_dir):
        messages.error(request, "No exported images found for this photographer")
        return redirect('/my-photographers')
    
    # Create a unique filename for the zip file
    zip_filename = f"exported_images_photographer_{photographer_id}_{int(time.time())}.zip"
    zip_path = os.path.join(settings.MEDIA_ROOT, zip_filename)
    
    # Get all image files in the directory
    image_files = []
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
    
    for filename in os.listdir(export_dir):
        file_path = os.path.join(export_dir, filename)
        if os.path.isfile(file_path) and any(filename.lower().endswith(ext) for ext in valid_extensions):
            image_files.append(file_path)
    
    # Check if there are any images to download
    if not image_files:
        messages.error(request, "No images found in the exported folder")
        return redirect('/my-photographers')
    
    # Create ZIP file
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for image_path in image_files:
            if os.path.exists(image_path):  # Ensure file exists
                zipf.write(image_path, os.path.basename(image_path))  # Add to ZIP
    
    # Serve the zip file for download
    if os.path.exists(zip_path):
        with open(zip_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type="application/zip")
            response['Content-Disposition'] = f'attachment; filename={zip_filename}'
            
            # Delete the zip file after it's been sent to save space
            # Note: This won't execute until after the response is sent
            import threading
            def delete_file():
                time.sleep(60)  # Wait a minute before deleting
                if os.path.exists(zip_path):
                    os.remove(zip_path)
            threading.Thread(target=delete_file).start()
            
            return response
    
    # If we get here, something went wrong
    messages.error(request, "Error creating zip file")
    return redirect('/my-photographers')

def delete_event(request):
    event_id = request.GET.get('id')
    try:
        # Get the event
        event = Events.objects.get(id=event_id)
        # Delete the event
        event.delete()
        messages.success(request, "Event deleted successfully")
    except Events.DoesNotExist:
        messages.error(request, "Event not found")
    except Exception as e:
        messages.error(request, f"Error deleting event: {str(e)}")
    
    # Redirect back to the events page
    return redirect('/viewevent')
