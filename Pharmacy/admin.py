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


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "medicine", "quantity", "status", "total_price", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("medicine__name",)
    ordering = ("-created_at",)


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
