from django.contrib import admin
from django.db.models import Sum,Count,DateTimeField,Min,Max
from django.core import serializers
from django.db.models.functions import Trunc
# Register your models here.
from .models import Menu,Cart,CartItem,Order,OrderItem,Booking,OrderSummary
from django.utils.translation import gettext_lazy as _
from datetime import datetime
from django.db.models.functions import Coalesce
from django.db.models.functions import Cast
from django.db.models import IntegerField
from django.db.models import F
from django.db.models import FloatField
from django.http import JsonResponse
from django.urls import reverse
from django.utils.html import format_html

class PeriodFilter(admin.SimpleListFilter):
    title = _('Period')
    parameter_name = 'period'

    def lookups(self, request, model_admin):
        return (
            ('this_month', _('This Month')),
            ('last_month', _('Last Month')),
            ('this_year', _('This Year')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'this_month':
            return queryset.filter(created_at__month=datetime.now().month)
        elif self.value() == 'last_month':
            last_month = datetime.now().month - 1 if datetime.now().month > 1 else 12
            return queryset.filter(created_at__month=last_month)
        elif self.value() == 'this_year':
            return queryset.filter(created_at__year=datetime.now().year)
        return queryset


class MenuAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'total_sold', 'edit_link')
    readonly_fields = ('total_sold',)
    ordering = ('name',)
    change_list_template = 'admin/menu_summary_change_list.html'

    def total_sold(self, obj):
        return obj.orderitem_set.aggregate(total=Sum('quantity'))['total']
    total_sold.short_description = 'Total Sold'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(total_sold=Sum('orderitem__quantity'))
        queryset = queryset.order_by('-total_sold', 'name')
        return queryset

    def edit_link(self, obj):
        url = reverse('admin:restaurant_menu_change', args=[obj.pk])
        return format_html('<a href="{}">Edit</a>', url)
    edit_link.short_description = 'Edit'

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context=extra_context)

        if request.method == 'GET':
            queryset = self.get_queryset(request)
            menu_data = queryset.values('name', 'total_sold')
            menu_data_json = list(menu_data)

            response.context_data['menu_data_json'] = JsonResponse(menu_data_json, safe=False).content.decode('utf-8')
            response.context_data['result_list'] = queryset

        return response

admin.site.register(Menu, MenuAdmin)


@admin.register(OrderSummary)
class OrderSummaryAdmin(admin.ModelAdmin):
    change_list_template = 'admin/orders_summary_change_list.html'
    list_filter = (
        'user',
        'orderitem__menu__name',
        'status',
        PeriodFilter
    )
    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(
            request,
            extra_context=extra_context,
        )
        try:
            qs = response.context_data['cl'].queryset
        except (AttributeError, KeyError):
            return response

        metrics = {
            'total': Count('id'),
            'total_sales': Sum('items__price'),
        }
        response.context_data['summary'] = list(
            qs
            .values('id', 'user__username', 'created_at', 'status')
            .annotate(**metrics)
            .order_by('-created_at') # Retrieve the latest 5 orders
        )
        response.context_data['summary_total'] = dict(
            qs.aggregate(**metrics)
        )

        total = dict(
            qs.aggregate(**metrics)
        )

        summary_over_time = qs.annotate(
            period=Trunc(
                'created_at',
                'day',
                output_field=DateTimeField(),
            ),
        ).values('period').annotate(total=Sum('items__price')).order_by('period')
        summary_range = summary_over_time.aggregate(
            low=Min('total'),
            high=Max('total'),
        )
        high = summary_range.get('high', 0)
        low = summary_range.get('low', 0)
        

        t = [{
            'period': x['period'],
            'total': x['total'] or 0,
        } for x in summary_over_time]
        
        for obj in t:
            obj['percentage'] = (obj['total'] / total['total_sales']) * 100

        response.context_data['summary_over_time'] = t
        return response


admin.site.register(Booking)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)

