from django.urls import path
from . import views

urlpatterns = [
    # main pages
    path("", views.home, name="home"),
    path("pharmacy/", views.pharmacy, name="pharmacy"),
    path("admin-home/", views.admin_home, name="admin_home"),
    # Auth
    path("login/", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path("logout/", views.logout_view, name="logout"),
    path("contact/", views.contact, name="contact"),
    path("forgotpassword/", views.forgot_password, name="forgotpassword"),
    path("resetpassword/", views.reset_password, name="resetpassword"),
    # Medicine & Inventory
    path("medicines/", views.medicine_list, name="medicine_list"),
    path("inventory/", views.inventory_view, name="inventory_view"),
    # Orders, Sales, Bills
    path("orders/", views.order_list, name="order_list"),
    path("sales/", views.sales_view, name="sales_view"),
    path("bills/", views.bill_list, name="bill_list"),
    # Prebooking
    path("prebookings/", views.prebooking_list, name="prebooking_list"),
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('remove-from-cart/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('checkout-success/', views.checkout_success, name='checkout_success'),


]
