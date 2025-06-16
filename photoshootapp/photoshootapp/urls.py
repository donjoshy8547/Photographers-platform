"""
URL configuration for photoshootapp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings  
from django.conf.urls.static import static
from app import views
from app.views import process_ai, check_ai_status, editor_dashboard, test_view, get_matching_face_images


urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    path("",views.home, name='home'),
    path("login/",views.login, name='login'),
    path("test/", test_view, name='test_view'),
    
    path("adminhome/",views.adminhome, name='adminhome'),
    path("add_product/",views.add_product, name='add_product'),
    path("productlist/",views.productlist, name='productlist'),
    path("delete_dataadmin/",views.delete_dataadmin, name='delete_dataadmin'),
    path("orderlist/",views.orderlist, name='orderlist'),
    path("shipped/",views.shipped, name='shipped'),
    path("delivered/",views.delivered, name='delivered'),
    path("productreviewlist/",views.productreviewlist, name='productreviewlist'),
    path("deleteriv/",views.deleteriv, name='deleteriv'),

    path("photographerview/",views.photographerview, name='photographerview'),
    path("update/",views.update, name='update'),
    path("delete/",views.delete, name='delete'),
    path("addphoto/",views.addphoto, name='addphoto'),
    path("deleteimage/",views.deleteimage, name='deleteimage'),
    path("userview/",views.userview, name='userview'),
    path("reject/",views.reject, name='reject'),
    path("accept/",views.accept, name='accept'),
    path("viewfeedback/",views.viewfeedback, name='viewfeedback'),
    path("deletefeedback/",views.deletefeedback, name='deletefeedback'),
    path("myphoto/",views.myphoto, name='myphoto'),
    path("gallery/",views.gallery, name='gallery'),
    path("productlistoo/",views.productlistoo, name='productlistoo'),
    path("photouserreg/",views.photouserreg, name='photouserreg'),
    path("photouserrequest/",views.photouserrequest, name='photouserrequest'),
    
    path("portpholio/",views.portpholio, name='portpholio'),
    path("userrequest/",views.userrequest, name='userrequest'),
    path("viewrequestuser/",views.viewrequestuser, name='viewrequestuser'),
    path("delete_request/",views.delete_request, name='delete_request'),
    path("replyrequest/",views.replyrequest, name='replyrequest'),
    path("addcart/",views.addcart, name='addcart'),
    path("cartview/",views.cartview, name='cartview'),
    path("deletecart/",views.deletecart, name='deletecart'),
    path("order/",views.order, name='order'),
    path("payment/",views.payment, name='payment'),
    path("orderdetails/",views.orderdetails, name='orderdetails'),
    path("cancelorder/",views.cancelorder, name='cancelorder'),
    path("productreview/",views.productreview, name='productreview'),

    path("aphotoreg/",views.aphotoreg, name='aphotoreg'),
    path("asaddphoto/",views.asaddphoto, name='asaddphoto'),
    path("asphotohome/",views.asphotohome, name='asphotohome'),
    path("asmyphoto/",views.asmyphoto, name='asmyphoto'),
    path("Addevent/",views.Addevent, name='addevent'),
    path("photohome/",views.photohome, name='photohome'),
    path("userhome/",views.userhome, name='userhome'),
    path("userreg/",views.userreg, name='userreg'),
    path("editimage/",views.editimage, name='editimage'),
    path("gallarylist/",views.gallarylist, name='gallarylist'),
    path("addfeedback/",views.addfeedback, name='addfeedback'),
    path("download/",views.download, name='download'),
    path("photoreg/",views.photoreg, name='photoreg'),
    path("userproductlist/",views.userproductlist, name='userproductlist'),
    path("cartviewuser/",views.cartviewuser, name='cartviewuser'),
    path("deletecartuser/",views.deletecartuser, name='deletecartuser'),
    path("orderuser/",views.orderuser, name='orderuser'),
    path("paymentuser/",views.paymentuser, name='paymentuser'),
    path("orderdetailsuser/",views.orderdetailsuser, name='orderdetailsuser'),
    path("cancelorderuser/",views.cancelorderuser, name='cancelorderuser'),
    path("productreviewuser/",views.productreviewuser, name='productreviewuser'),
    path("viewevent/",views.Viewevent, name='viewevent'),
    path("publish_event/",views.publish_event, name='publish_event'),
    path("unpublish_event/",views.unpublish_event, name='unpublish_event'),
    path("view_published_events/",views.view_published_events, name='view_published_events'),
    path("event_details/",views.event_details, name='event_details'),
    path("apply_event/",views.apply_event, name='apply_event'),
    path("delete_event/",views.delete_event, name='delete_event'),
    path("downloadusergalary/",views.downloadusergalary, name='downloadusergalary'),
    path("assistance/",views.Assistance, name='assistance'),
    path("addguest/",views.Addguest, name='addguest'),
    path("gustgallarylist/",views.gustgallarylist, name='gustgallarylist'),
    path("photoprofile/",views.photoprofile, name='photoprofile'),
    path('test-session/', views.test_session, name='test_session'),
    path('test-login/', views.test_login, name='test_login'),
    path('test-login-action/', views.test_login_action, name='test_login_action'),
    path('my-photographers/', views.my_photographers, name='my_photographers'),
    path('download-exported-images/', views.download_exported_images, name='download_exported_images'),
    
    
    path("ban_photographer/", views.ban_photographer, name="ban_photographer"),
    path("unban_photographer/", views.unban_photographer, name="unban_photographer"),
    
    path("process-ai/", process_ai, name="process_ai"),
    path("check-ai-status/", check_ai_status, name="check_ai_status"),
    path("editor-dashboard/", editor_dashboard, name="editor_dashboard"),
    path("export-images/", views.export_images, name="export_images"),
    path("get-matching-faces/", get_matching_face_images, name="get_matching_faces"),
    path("run-face-recognition/", views.run_face_recognition, name="run_face_recognition"),
    path("save-face-labels/", views.save_face_labels, name="save_face_labels"),
    path("ai-test/", views.ai_test_view, name="ai_test"),
    path("ai-simple-test/", views.ai_simple_test_view, name="ai_simple_test"),
    path('export-selected-photos/', views.export_selected_photos, name='export_selected_photos'),
]

if settings.DEBUG:  
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
