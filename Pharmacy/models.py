from django.db import models


class Admin(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=50)

    def __str__(self):
        return self.username


class UserProfile(models.Model):
    id = models.AutoField(primary_key=True)
    user_phone_number = models.BigIntegerField(unique=True)
    user_name = models.CharField(max_length=100)
    user_password = models.CharField(max_length=100)

    def __str__(self):
        return self.user_name


class Medicine(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    details = models.TextField(blank=True, null=True)
    link = models.URLField(max_length=200, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=50.00)
    group = models.CharField(max_length=100, blank=True, null=True)
    brand = models.CharField(max_length=100, blank=True, null=True)
    batch_no = models.CharField(max_length=50, blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True)
    image = models.ImageField(
        upload_to="medicine_images/", blank=True, null=True
    )  # Added image field
    added_by = models.ForeignKey(
        Admin, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Inventory(models.Model):
    id = models.AutoField(primary_key=True)
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    availability = models.BooleanField(default=True)
    updated_by = models.ForeignKey(
        Admin, on_delete=models.SET_NULL, null=True, blank=True
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.medicine.name} - {self.quantity} in stock"


class Cosmetic(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=50.00)
    details = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, null=True)
    brand = models.CharField(max_length=100, blank=True, null=True)
    batch_no = models.CharField(max_length=50, blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True)
    image = models.ImageField(upload_to="cosmetic_images/", blank=True, null=True)
    added_by = models.ForeignKey(
        Admin, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Bill(models.Model):
    id = models.AutoField(primary_key=True)
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)
    address = models.CharField(max_length=200)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Bill #{self.id} - {self.user_profile.user_name}"


# class Order(models.Model):
#     STATUS_CHOICES = [
#         ("pending", "Pending"),
#         ("completed", "Completed"),
#         ("canceled", "Canceled"),
#     ]

#     id = models.AutoField(primary_key=True)
#     # medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
#     product = models.TextField(blank=True, null=True)  # Product Name
#     quantity = models.PositiveIntegerField(blank=True, null=True)  # Quantity
#     price_per_unit = models.DecimalField(
#         max_digits=10, decimal_places=2, blank=True, null=True
#     )
#     total_price = models.DecimalField(
#         max_digits=10, decimal_places=2, blank=True, null=True
#     )
#     status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
#     cancel_reason = models.TextField(blank=True, null=True)
#     customer_name = models.CharField(max_length=100)  # Customer Name
#     customer_phone = models.CharField(max_length=15)  # Customer Phone
#     customer_address = models.TextField()  # Customer Address
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def save(self, *args, **kwargs):
#         if self.quantity is None or self.price_per_unit is None:
#             raise ValueError(
#                 "Quantity and price_per_unit must be set before saving an Order."
#             )

#         self.total_price = self.quantity * self.price_per_unit
#         super().save(*args, **kwargs)


class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("completed", "Completed"),
        ("canceled", "Canceled"),
    ]

    id = models.AutoField(primary_key=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    customer_name = models.CharField(max_length=100)
    customer_phone = models.CharField(max_length=15)
    customer_address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.id} - {self.customer_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.price_per_unit
        super().save(*args, **kwargs)


class Sale(models.Model):
    id = models.AutoField(primary_key=True)
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    total_sale = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"Sale on {self.date}"


class PreBooking(models.Model):
    id = models.AutoField(primary_key=True)
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    booking_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_profile.user_name} booked {self.medicine.name}"


class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"


class Doctor(models.Model):
    name = models.CharField(max_length=100)
    specialty = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    address = models.TextField()
    latitude = models.DecimalField(max_digits=10, decimal_places=6)
    longitude = models.DecimalField(max_digits=10, decimal_places=6)

    def __str__(self):
        return self.name
