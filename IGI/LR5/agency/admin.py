from django.contrib import admin
from django.db.models import Avg, Sum
from .models import (
    Article, ClientProfile, CompanyInfo, Deal, EmployeeProfile,
    FAQ, Owner, PromoCode, Property, PropertyType, Review, Vacancy
)


@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Deal model, including aggregate statistics on the changelist.
    """
    list_display = ('id', 'property', 'client', 'employee', 'deal_type', 'final_price', 'created_at_utc')
    list_filter = ('deal_type', 'created_at_utc', 'employee')
    search_fields = ('property__title', 'client__user__username')

    def changelist_view(self, request, extra_context=None):
        """
        Injects cumulative and average transaction financial statistics into the admin context.
        """
        result = Deal.objects.aggregate(
            total_sales_sum=Sum('final_price'),
            avg_deal_price=Avg('final_price')
        )
        extra_context = extra_context or {}
        extra_context['total_sales_sum'] = result['total_sales_sum'] or 0
        extra_context['avg_deal_price'] = result['avg_deal_price'] or 0
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    """
    Admin layout configuration for the Property listings catalog.
    """
    list_display = ('title', 'prop_type', 'price', 'owner', 'is_active')
    list_filter = ('prop_type', 'is_active')
    search_fields = ('title', 'description')


# Register remaining structural models to the Django administration interface
admin.site.register(PropertyType)
admin.site.register(Owner)
admin.site.register(ClientProfile)
admin.site.register(EmployeeProfile)
admin.site.register(PromoCode)
admin.site.register(Article)
admin.site.register(Review)
admin.site.register(CompanyInfo)
admin.site.register(FAQ)
admin.site.register(Vacancy)