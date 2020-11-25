from django.shortcuts import render,redirect,get_object_or_404
from core.models import Item,OrderItem,Order,Category,BillingAddress,Payment 
from django.views.generic import DetailView,View,ListView,CreateView,FormView
from django.utils import timezone
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from core.forms import checkoutform
from django.conf import settings
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from pypaystack import Transaction,Customer,Plan
from django.http import JsonResponse
import json

# Create your views here.
def about(request):
    
    return render(request,'about-page.html')

class product(DetailView):
    model = Item
    template_name = 'core/product-page.html'

def home(request,category_slug=None):
    category=None
    categories =Category.objects.all()
    item =Item.objects.all()
    
    user_list = Item.objects.all()
    page = request.GET.get('page', 1)

    paginator = Paginator(user_list, 10)
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)

    if category_slug:
        category=get_object_or_404(Category,slug=category_slug)
        item=item.filter(category=category)
    
    query = request.GET.get('q','')
    #The empty string handles an empty "request"
    if query:
            queryset = (Q(title__icontains=query) | Q(category__name__icontains=query))
            #I assume "text" is a field in your model
            #i.e., text = model.TextField()
            #Use | if searching multiple fields, i.e., 
            #queryset = (Q(text__icontains=query))|(Q(other__icontains=query))
            results = Item.objects.filter(queryset).distinct()
    else:
       results = []
        
    return render (request,'core/home-page.html',{'categories': categories,
                                                'category':category,
                                                'items':item,'results':results, 'query':query,
                                                'users':users,
                                                })


@login_required
def add_to_cart(request,slug):
    item =get_object_or_404(Item,slug=slug) 
    order_item,created=OrderItem.objects.get_or_create(item=item,
                                                user=request.user,
                                                ordered=False)
    order_qs= Order.objects.filter(
        user=request.user,
        ordered=False,
        )

    # if item exists
    if  order_qs.exists():
        order=order_qs[0]

        #check if order item is in order

        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity +=1
            order_item.save()
            messages.info(request,"this item quantity was updated. ")
            return redirect('core:order-summary')

        else:
            messages.info(request,"this item was added to your cart.")
            order.items.add(order_item)
            return redirect('core:order-summary')

    # if it does not exist
    else:
        ordered_date=timezone.now()
        order =Order.objects.create(user=request.user,ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request,"this item added to your cart. ")
        return redirect('core:order-summary')
    
@login_required
def remove_from_cart(request,slug):
    item =get_object_or_404(Item,slug=slug)
    order_qs= Order.objects.filter(
        user=request.user,
        ordered=False,
        )
     # if item exists
    if  order_qs.exists():
        order=order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item=OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            order_item.delete()
            messages.info(request,"this item was removed from your cart")
            return redirect('core:order-summary')

        else:
            messages.info(request,"this item was not in your cart")
            return redirect('core:product',slug=slug)
    else :
        messages.info(request,"You Do not Have An Active Order")
        return redirect('core:product',slug=slug)
 
@login_required
def remove_single_item_from_cart(request,slug):
    item =get_object_or_404(Item,slug=slug)
    order_qs= Order.objects.filter(
        user=request.user,
        ordered=False,
        )
     # if item exists
    if  order_qs.exists():
        order=order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item=OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity>1:
                order_item.quantity -=1
                order_item.save()
            else:
                order.items.remove(order_item)
                order_item.delete()
            messages.info(request,"this item quantity was updated")
            return redirect('core:order-summary')
        else:
            messages.info(request,"this item was not in your cart")
            return redirect('core:product',slug=slug)
    else :
        messages.info(request,"You Do not Have An Active Order")
        return redirect('core:product',slug=slug)
 
class ordersummary(LoginRequiredMixin,View):
    def get(self,*args,**kwargs):

            order= Order.objects.get(
                user=self.request.user,
                ordered=False,
                )
            context={
                'object' : order
            }
            return render(self.request,'core/ordersummary.html',context)


class checkout(LoginRequiredMixin,View):
    def get(self,*args,**kwargs):
        order= Order.objects.get(user=self.request.user,ordered=False)
        form=checkoutform()
        context={
            'form':form,
            'order':order,
        }
        return render(self.request,'checkout-page.html',context)
 
    def post(self, *args, **kwargs):
        form =checkoutform(self.request.POST or None)
        try:
            order= Order.objects.get(user=self.request.user,ordered=False)
            if form.is_valid():
                Address = form.cleaned_data.get('Address')
                DELIVERY_METHOD=form.cleaned_data.get('DELIVERY_METHOD')
                payment_option = form.cleaned_data.get('payment_option')
                billing_address=BillingAddress(
                    user=self.request.user,
                    Address=Address,
                    DELIVERY_METHOD=DELIVERY_METHOD,
                )
                
                billing_address.save()
                order.billing_address = billing_address
                order.save()

                

                if payment_option == 'S':
                    return redirect('core:checkout', payment_option='stripe')
                elif payment_option == 'P':
                    return redirect('core:paystack-portal', payment_option='paystack')
                else:
                    messages.warning(self.request, "Invalid payment option selected")
                    return redirect('core:ordersummary')


                messages.error(self.request,"Checkout Failed")
                return redirect('core:order-summary')
                
            
                
        except ObjectDoesNotExist:
            messages.error(self.request,"You do not have an active order")
            return redirect("core:order-summary")

       
           

        return redirect('core:order-summary')

 
class paystackview(LoginRequiredMixin,View):
    def get(self,*args,**kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        context={
            'order': order,
            'pk_public':settings.PAYSTACK_PUBLIC_KEY,
        }
        return render(self.request,'paystack.html',context)
    
    def post(self, *args, **kwargs):
         order = Order.objects.get(user=self.request.user, ordered=False)
     
    


def verify(request,id):
    order = Order.objects.get(user=request.user, ordered=False)
    transaction=Transaction(authorization_key=settings.PAYSTACK_SECRET_KEY)
    response=transaction.verify(id)
    data =JsonResponse(response,safe=False)
    order.ordered=True
    order.save()
    return redirect('core:order-summary')

 
    