from django.contrib import admin
from .models import (
    Admin as AdminModel,
    UserProfile,
    Medicine,
    Inventory,
    Order,
    Sale,
    Bill,
    PreBooking,
    Doctor,
    Cosmetic,
    OrderItem,
)


@admin.register(AdminModel)
class AdminPanel(admin.ModelAdmin):
    list_display = ("id", "username")
    search_fields = ("username",)
    ordering = ("username",)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user_name", "user_phone_number")
    search_fields = ("user_name", "user_phone_number")


@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "brand", "group", "batch_no", "expiry_date")
    search_fields = ("name", "brand", "group")
    list_filter = ("brand", "group", "expiry_date")


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ("id", "medicine", "quantity", "price", "availability", "updated_at")
    search_fields = ("medicine__name",)
    list_filter = ("availability",)


# OrderAdmin for displaying order details in admin panel
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "customer_name",
        "status",
        "total_price",
        "created_at",
        "updated_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("customer_name", "customer_phone", "customer_address")
    ordering = ("-created_at",)

    # Inline display for OrderItem (this will allow you to see the order items inside each order)
    # inlines = [OrderItemInline]


# OrderItemAdmin for managing the items in the order
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0  # No extra empty fields by default
    fields = ("product_name", "quantity", "price_per_unit", "total_price")


# Register the OrderItem model separately if you want to manage it in the admin separately
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        "order",
        "product_name",
        "quantity",
        "price_per_unit",
        "total_price",
    )
    list_filter = ("order",)
    search_fields = ("product_name", "order__customer_name")
    ordering = ("order",)


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ("id", "user_profile", "total_amount", "date", "time")
    search_fields = ("user_profile__user_name",)
    ordering = ("-date", "-time")


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ("id", "bill", "total_sale", "date")
    ordering = ("-date",)


@admin.register(PreBooking)
class PreBookingAdmin(admin.ModelAdmin):
    list_display = ("id", "user_profile", "medicine", "quantity", "booking_date")
    search_fields = ("user_profile__user_name", "medicine__name")
    ordering = ("-booking_date",)


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "specialty", "phone", "email")
    search_fields = ("name", "specialty", "email")
    ordering = ("name",)


@admin.register(Cosmetic)
class CosmeticAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "details",
        "price",
        "category",
        "brand",
        "batch_no",
        "expiry_date",
    )
    search_fields = ("name", "category", "brand")
    list_filter = ("category", "brand", "expiry_date")
    ordering = ("name",)
