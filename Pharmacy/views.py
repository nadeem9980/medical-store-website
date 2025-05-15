from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from .models import (
    Medicine,
    Inventory,
    Order,
    UserProfile,
    Contact,
    Cosmetic,
    OrderItem,
    Doctor,
)
from django.contrib.auth import update_session_auth_hash, login
from django.conf import settings
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from .forms import CheckoutForm
from django.core.paginator import Paginator



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
    medicines_qs = (
        Medicine.objects.filter(name__icontains=query)
        if query else Medicine.objects.all()
    ).order_by('name')

    paginator = Paginator(medicines_qs, 12)  # 12 medicines per page
    page_number = request.GET.get('page')
    medicines = paginator.get_page(page_number)

    return render(
        request,
        "medicine_list.html",
        {
            "medicines": medicines,
            "MEDIA_URL": settings.MEDIA_URL,
            "query": query,  # pass query to keep search input value if needed
        },
    )

def add_to_cart(request):
    if request.method == "POST":
        item_id = str(
            request.POST.get("medicine_id") or request.POST.get("cosmetic_id")
        )
        quantity = int(request.POST.get("quantity", 1))
        cart = request.session.get("cart", {})

        if item_id in cart:
            cart[item_id] += quantity
        else:
            cart[item_id] = quantity

        request.session["cart"] = cart

        # Redirect back to the page from where the request came
        referer = request.META.get(
            "HTTP_REFERER", "default_url"
        )  # 'default_url' can be a fallback if referer is not available
        return HttpResponseRedirect(referer)


def cart_view(request):
    cart = request.session.get("cart", {})
    cart_items = []
    total_price = 0

    # Handle both Medicine and Cosmetic items in the cart
    for product_id, quantity in cart.items():
        try:
            # Try to get Medicine first
            product = Medicine.objects.get(id=product_id)
        except Medicine.DoesNotExist:
            # If not found, try to get Cosmetic
            try:
                product = Cosmetic.objects.get(id=product_id)
            except Cosmetic.DoesNotExist:
                continue  # Skip this item if not found in either Medicine or Cosmetic

        subtotal = product.price * quantity
        cart_items.append(
            {
                "product": product,
                "quantity": quantity,
                "total": subtotal,
                "price": product.price,
            }
        )
        total_price += subtotal

    show_form = False
    form = CheckoutForm()

    if request.method == "POST":
        if request.POST.get("show_form") == "1":
            show_form = True  # user clicked Proceed
        else:
            form = CheckoutForm(request.POST)
            if form.is_valid():
                name = form.cleaned_data["name"]
                phone = form.cleaned_data["phone"]
                address = form.cleaned_data["address"]

                # Create a single order for all cart items
                order = Order.objects.create(
                    total_price=total_price,
                    customer_name=name,
                    customer_phone=phone,
                    customer_address=address,
                    status="pending",
                )

                # Create an OrderItem for each product in the cart
                for item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        product_name=item["product"].name,  # Store the product name
                        quantity=item["quantity"],  # Set quantity
                        price_per_unit=item["price"],  # Set price per unit
                        total_price=item["total"],  # Set total price for this item
                    )

                # Clear the cart after successful order placement
                request.session["cart"] = {}

                # Send the success message with payment instructions
                payment_number = "+92-3037442533"
                messages.success(
                    request,
                    f"Order placed successfully. Please send payment to Jazzcash: {payment_number} and send a snapshot of your payment on WhatsApp for confirmation.",
                )

                return redirect("view_cart")
    return render(
        request,
        "cart.html",
        {
            "cart_items": cart_items,
            "total_price": total_price,
            "form": form,
            "show_form": show_form,
        },
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

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            phone = form.cleaned_data["phone"]
            address = form.cleaned_data["address"]

            # Process each item into an Order (optional: add name/phone/address if model allows)
            for medicine_id, quantity in cart.items():
                try:
                    medicine = Medicine.objects.get(id=medicine_id)
                    Order.objects.create(
                        medicine=medicine,
                        quantity=quantity,
                        price_per_unit=medicine.price,
                        status="pending",
                    )
                except Medicine.DoesNotExist:
                    continue

            # Clear the cart
            request.session["cart"] = {}
            request.session.modified = True

            # Show message to send payment manually
            return render(
                request,
                "order_success.html",
                {
                    "name": name,
                    "phone": phone,
                    "address": address,
                    "payment_info": "Please send payment to JazzCash 0300-XXXXXXX",
                },
            )

    else:
        form = CheckoutForm()

    return render(request, "checkout.html", {"form": form})


def checkout_success(request):
    return render(request, "checkout_success.html")


# ✅ Inventory display
def inventory_view(request):
    inventory = Inventory.objects.select_related("medicine").all()
    return render(request, "ainventory.html", {"inventory": inventory})


def doctor_list(request):
    doctors = Doctor.objects.all()

    print("Doctors:", doctors)  # Debugging line to check the doctors queryset
    return render(request, "doctor_list.html", {"doctors": doctors})


def all_cosmetics(request):
    query = request.GET.get("q", "")  # Search query from URL
    # Filter cosmetics based on the search query if any
    cosmetics = (
        Cosmetic.objects.filter(name__icontains=query)
        if query
        else Cosmetic.objects.all()
    )

    # Pass the cosmetics data and MEDIA_URL to the template context
    return render(
        request,
        "all_cosmetics.html",
        {
            "cosmetics": cosmetics,
            "MEDIA_URL": settings.MEDIA_URL,  # Add MEDIA_URL to the context
        },
    )
