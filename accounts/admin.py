from django.contrib import admin

from django.contrib.auth.models import User
from django.db.models import Sum
from .models import UserProxy
from django.db.models import Value
from django.db.models.functions import Coalesce


class UserPurchaseAdmin(admin.ModelAdmin):

    list_display = ('username', 'get_purchase_count')
    search_fields = ('username', 'email')
    list_filter = ('is_active', 'is_staff')
    change_list_template = 'admin/accounts/userproxy/change_list.html'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(purchase_count=Coalesce(Sum('order__item__quantity'), Value(0))).order_by('-purchase_count')
    
    def get_purchase_count(sef,obj):
        return obj.purchase_count
    get_purchase_count.short_description = 'Purchase Count'
    get_purchase_count.admin_order_field = 'purchase_count'

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        qs = self.get_queryset(request)
        top_user = qs.first()
        extra_context['top_purchaser'] = top_user
        return super().changelist_view(request, extra_context=extra_context)


admin.site.register(UserProxy, UserPurchaseAdmin)
