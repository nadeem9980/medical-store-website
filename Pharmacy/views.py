from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from .models import (
    Medicine,
    Inventory,
    Sale,
    Order,
    Bill,
    PreBooking,
    UserProfile,
    Contact,
)
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import login
from django.conf import settings
from django.shortcuts import get_object_or_404, render
from .models import Doctor


# ✅ Home page
def home(request):
    return render(request, "home.html")


# ✅ Login view
def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            messages.success(request, "Logged in successfully!")
            return redirect("pharmacy")
        else:
            messages.error(request, "Invalid username or password")
            return redirect("login")
    return render(request, "login.html")


def signup_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password1 = request.POST["password1"]
        password2 = request.POST["password2"]

        if password1 != password2:
            return render(request, "signup.html", {"error": "Passwords do not match"})

        if User.objects.filter(username=username).exists():
            return render(request, "signup.html", {"error": "Username already exists"})

        user = User.objects.create_user(
            username=username, email=email, password=password1
        )
        login(request, user)
        return redirect("home")

    return render(request, "signup.html")


# ✅ Logout view
def logout_view(request):
    auth_logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect("home")


def contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        subject = request.POST.get("subject")
        message = request.POST.get("message")

        if name and email and subject and message:
            Contact.objects.create(
                name=name, email=email, subject=subject, message=message
            )
            # Optionally send email too
            return render(request, "contact.html", {"success": True})
        else:
            return render(
                request, "contact.html", {"error": "Please fill in all fields."}
            )

    return render(request, "contact.html")


def forgot_password(request):
    if request.method == "POST":
        email = request.POST["email"]
        try:
            user = User.objects.get(email=email)
            # Generate random token
            token = get_random_string(length=32)
            # Save the token to the UserProfile or model of your choice
            user_profile, created = UserProfile.objects.get_or_create(user=user)
            user_profile.reset_token = token
            user_profile.save()

            # Send password reset email
            reset_link = f"{request.build_absolute_uri('/resetpassword/')}{token}"
            send_mail(
                "Password Reset Request",
                f"Click on the link to reset your password: {reset_link}",
                "admin@pharmacy.com",
                [email],
                fail_silently=False,
            )

            messages.success(
                request, "Password reset link has been sent to your email."
            )
            return redirect("login")

        except User.DoesNotExist:
            messages.error(request, "No user found with this email address.")
            return redirect("forgotpassword")

    return render(request, "forgotpassword.html")


def reset_password(request, token):
    try:
        user_profile = UserProfile.objects.get(reset_token=token)
        user = user_profile.user

        if request.method == "POST":
            new_password = request.POST["new_password"]
            confirm_password = request.POST["confirm_password"]

            if new_password != confirm_password:
                messages.error(request, "Passwords do not match!")
                return redirect("resetpassword", token=token)

            # Update the password
            user.set_password(new_password)
            user.save()

            # Clear the token after successful reset
            user_profile.reset_token = None
            user_profile.save()

            update_session_auth_hash(request, user)  # Keep the user logged in

            messages.success(request, "Your password has been reset successfully.")
            return redirect("login")

        return render(request, "resetpassword.html", {"token": token})

    except UserProfile.DoesNotExist:
        messages.error(request, "Invalid reset link or token expired.")
        return redirect("login")


# ✅ Admin dashboard
def admin_home(request):
    return render(request, "admin.html")


# ✅ Pharmacy dashboard
def pharmacy(request):
    return render(request, "pharmacy.html")


# ✅ Medicine list
def medicine_list(request):
    query = request.GET.get("q", "")
    # medicines = Medicine.objects.all()
    medicines = (
        Medicine.objects.filter(name__icontains=query)
        if query
        else Medicine.objects.all()
    )
    # Pass MEDIA_URL to the template context
    return render(
        request,
        "medicine_list.html",
        {
            "medicines": medicines,
            "MEDIA_URL": settings.MEDIA_URL,  # Add MEDIA_URL here
        },
    )


def add_to_cart(request):
    if request.method == "POST":
        medicine_id = str(request.POST.get("medicine_id"))
        quantity = int(request.POST.get("quantity", 1))
        cart = request.session.get("cart", {})

        if medicine_id in cart:
            cart[medicine_id] += quantity
        else:
            cart[medicine_id] = quantity

        request.session["cart"] = cart
        return redirect("medicine_list")  # Change if needed


def view_cart(request):
    cart = request.session.get("cart", {})
    cart_items = []

    total_price = 0
    for med_id, qty in cart.items():
        try:
            medicine = Medicine.objects.get(pk=med_id)
            subtotal = medicine.price * qty
            cart_items.append(
                {"medicine": medicine, "quantity": qty, "total": subtotal}
            )
            total_price += subtotal
        except Medicine.DoesNotExist:
            pass

    return render(
        request, "cart.html", {"cart_items": cart_items, "total_price": total_price}
    )


def remove_from_cart(request):
    medicine_id = str(request.POST.get("medicine_id"))
    cart = request.session.get("cart", {})

    if medicine_id in cart:
        del cart[medicine_id]
        request.session["cart"] = cart

    return redirect("view_cart")


def checkout(request):
    cart = request.session.get("cart", {})
    if not cart:
        return redirect("cart")

    bill = Bill.objects.create(user_profile="Test Customer")  # Replace as needed

    for medicine_id, quantity in cart.items():
        try:
            medicine = Medicine.objects.get(id=medicine_id)
            price = medicine.price

            order = Order(
                bill=bill,
                medicine=medicine,
                quantity=quantity,
                price_per_unit=price,
                status="pending",
            )
            order.save()
        except Medicine.DoesNotExist:
            continue  # Or handle error: medicine was deleted from DB

    request.session["cart"] = {}
    return render(request, "checkout_success.html")


def checkout_success(request):
    return render(request, "checkout_success.html")


# ✅ Inventory display
def inventory_view(request):
    inventory = Inventory.objects.select_related("medicine").all()
    return render(request, "ainventory.html", {"inventory": inventory})


# ✅ Sales display
def sales_view(request):
    sales = Sale.objects.select_related("bill").all()
    return render(request, "asales.html", {"sales": sales})


# ✅ Orders display
def order_list(request):
    orders = Order.objects.select_related("medicine", "bill").all()
    return render(request, "order_list.html", {"orders": orders})


# ✅ Bill list
def bill_list(request):
    bills = Bill.objects.select_related("user_profile").all()
    return render(request, "bill_list.html", {"bills": bills})


# ✅ PreBookings list
def prebooking_list(request):
    prebookings = PreBooking.objects.select_related("user_profile", "medicine").all()
    return render(request, "aprebooklists.html", {"prebookings": prebookings})


def doctor_list(request):
    doctors = Doctor.objects.all()

    print("Doctors:", doctors)  # Debugging line to check the doctors queryset
    return render(request, "doctor_list.html", {"doctors": doctors})
