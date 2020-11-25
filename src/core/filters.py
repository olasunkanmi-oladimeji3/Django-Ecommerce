import django_filters
from core.models import Item,OrderItem,Order,Category

class ProductFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')
    category = django_filters.CharFilter(lookup_expr='icontains')
    class Meta:
        model = Item
        fields = ['title', 'category',]