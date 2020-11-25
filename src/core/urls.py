from django.urls import path
from django.conf.urls import url
from core import views
from django.conf import settings
from django.conf.urls.static import static

app_name='core'

urlpatterns = [
    path('',views.home,name='home'),
    path('about/',views.about,name='about'),
    path('product/<slug>/',views.product.as_view(),name='product'),
    path('add-to-cart/<slug>/',views.add_to_cart,name='add-to-cart'),
    path('remove-from-cart/<slug>/',views.remove_from_cart,name='remove-from-cart'),
    path('remove-item/<slug>/',views.remove_single_item_from_cart,name='remove-single-item-from-cart'),
    path('order-summary/',views.ordersummary.as_view(),name='order-summary'),
    path('checkout/',views.checkout.as_view(),name='checkout'),
    path('payment-portal/<payment_option>/',views.paystackview.as_view(),name='paystack-portal'),
    path('<slug:category_slug>/',views.home,name='category'),
    
]

if settings.DEBUG:
    urlpatterns +=static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)
    urlpatterns +=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)