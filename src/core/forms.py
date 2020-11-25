from django import forms
from core.models import Item,OrderItem,Order,Category


PAYMENT_CHOICES =(
    ('S','Stripe'),
    ('P','Paystack')
)

Delivery_CHOICES =(
    ('D','Door delivery'),
    ('P','Pick up')
)

class checkoutform(forms.Form): 
    Address= forms.CharField(widget=forms.TextInput(attrs=
    {'class':'form-control',
    'placeholder':'Address'}))
    DELIVERY_METHOD=forms.ChoiceField(widget=forms.RadioSelect(),choices=Delivery_CHOICES)
    payment_option=forms.ChoiceField(widget=forms.RadioSelect,choices=PAYMENT_CHOICES)