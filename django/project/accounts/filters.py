from cProfile import label
from cgitb import lookup
from sqlite3 import Date
#看上去有问题，但程序跑的很顺畅，找不到问题
import django_filters
from django_filters import DateFilter, CharFilter

from .models import *

class historyfilter(django_filters.FilterSet):
    actTo = CharFilter(field_name = 'actTo', lookup_expr='icontains',label='actTo')
    actBy = CharFilter(field_name = 'actBy', lookup_expr='icontains',label='actBy')
    start_date = DateFilter(field_name = 'actionDate', lookup_expr='gte',label='DateStartFrom')
    end_date = DateFilter(field_name = 'actionDate', lookup_expr='lte',label='DateEndBefore')

    class Meta:
        model = history
        fields = '__all__'
        exclude = ['recordTime','actionDate','actTo','actBy']
