from django.contrib import admin
from django.db.models import Avg, Sum
from .models import (
    Article, Cart, CartItem, ClientProfile, CompanyInfo, Deal,
    EmployeeProfile, FAQ, Owner, Partner, PromoCode, Property,
    PropertyType, Review, Vacancy
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


# Настройка отображения элементов корзины прямо внутри корзины пользователя
class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'get_total_price')
    search_fields = ('user__username',)
    inlines = [CartItemInline]

    def get_total_price(self, obj):
        return obj.total_price
    get_total_price.short_description = "Общая стоимость"


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'item_property', 'quantity', 'get_cost')
    search_fields = ('cart__user__username', 'item_property__title')

    def get_cost(self, obj):
        return obj.get_cost
    get_cost.short_description = "Стоимость позиции"


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ('name', 'website_url')
    search_fields = ('name',)


# Регистрация остальных стандартных моделей
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