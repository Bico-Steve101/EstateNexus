from django.contrib import admin
from django.core.exceptions import PermissionDenied
from .models import User, Manager, Property, Tenant, Review, ChatMessage, MPesaPayment, CreditCardPayment, \
    PaypalPayment, ManagerRequest, TenantRequest, Testimonial, ScheduledMessage, Message


class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'is_staff', 'is_active']
    search_fields = ['username', 'email']
    list_filter = ['is_staff', 'is_active']


admin.site.register(User, UserAdmin)

admin.site.register(Message)


class ManagerAdmin(admin.ModelAdmin):
    list_display = ['email', 'first_name', 'last_name']
    search_fields = ['email', 'first_name', 'last_name']


admin.site.register(Manager, ManagerAdmin)

admin.site.register(ManagerRequest)

admin.site.register(TenantRequest)

admin.site.register(Testimonial)

admin.site.register(ScheduledMessage)

admin.site.register(Review)


class PropertyAdmin(admin.ModelAdmin):
    list_display = ['name', 'option', 'type', 'price', 'user', 'manager']
    search_fields = ['name', 'option', 'type', 'user__username', 'manager__email']
    list_filter = ['option', 'type']


admin.site.register(Property, PropertyAdmin)


class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'property', 'created_at']
    search_fields = ['user__username', 'property__name']
    list_filter = ['created_at']


# admin.site.register(Review, ReviewAdmin)


class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'receiver', 'property', 'timestamp']
    search_fields = ['sender__username', 'receiver__username', 'property__name']
    list_filter = ['timestamp']


admin.site.register(ChatMessage, ChatMessageAdmin)


class MPesaPaymentInline(admin.StackedInline):
    model = MPesaPayment


class CreditCardPaymentInline(admin.StackedInline):
    model = CreditCardPayment


class PaypalPaymentInline(admin.StackedInline):
    model = PaypalPayment


class TenantAdmin(admin.ModelAdmin):
    inlines = [MPesaPaymentInline, CreditCardPaymentInline, PaypalPaymentInline]
    list_display = ['first_name', 'last_name', 'email']
    search_fields = ['first_name', 'last_name', 'email']

    def save_model(self, request, obj, form, change):
        if request.user == obj.property.user or request.user == obj.property.manager.user:
            obj.save()
        else:
            raise PermissionDenied("You are not authorized to add tenants to this property.")


admin.site.register(Tenant, TenantAdmin)

admin.site.register(MPesaPayment)
admin.site.register(CreditCardPayment)
admin.site.register(PaypalPayment)
