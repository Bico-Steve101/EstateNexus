import logging
import secrets
import string

import uuid
from django.contrib.auth.base_user import AbstractBaseUser
# from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


# Create your models here.
class User(AbstractUser):
    ROLE_CHOICES = (
        ('owner', 'Owner'),
        ('manager', 'Manager'),
        ('tenant', 'Tenant'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    name = models.CharField(max_length=100, null=True)
    email = models.EmailField(unique=True, null=True)
    joined = models.DateTimeField(auto_now_add=True)
    avatar = models.ImageField(null=True, upload_to="media/profile",
                               default="avatars/avatar.jpg")
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email


class Property(models.Model):
    OPTIONS = [
        ('rent', 'Rent'),
        ('sale', 'Sale'),
    ]
    TYPES = [
        ('apartment', 'Apartment'),
        ('condominium', 'Condominium'),
        ('townhouse', 'Townhouse'),
        ('land', 'Land'),
        ('commercial_property', 'Commercial Property'),
        ('mobile_home', 'Mobile Home'),
        ('loft', 'Loft'),
        ('cottage', 'Cottage'),
        ('penthouse', 'Penthouse'),
        ('studio', 'Studio'),
        ('villa', 'Villa'),
        ('bungalow', 'Bungalow'),
        ('duplex', 'Duplex'),
        ('house', 'House'),
        ('office', 'Office'),
        ('home', 'Home'),
        # Add other types here...
    ]
    ZONING = [
        ('residential', 'Residential'),
        ('commercial', 'Commercial'),
        ('industrial', 'Industrial'),
        ('mixed_use', 'Mixed Use'),
        ('agricultural', 'Agricultural'),
        ('historical_preservation', 'Historical Preservation'),
        ('open_space', 'Open Space'),
        ('recreational', 'Recreational'),
        ('special_use', 'Special Use'),
        ('variances', 'Variances'),
        ('overlay_zoning', 'Overlay Zoning'),
        ('cluster_zoning', 'Cluster Zoning'),
        ('conservation_zoning', 'Conservation Zoning'),
        ('planned_unit_development', 'Planned Unit Development'),
        ('transition_oriented_development', 'Transition Oriented Development'),
        ('urban_renewal', 'Urban Renewal'),
        ('waterfront_zoning', 'Waterfront Zoning'),
        ('other', 'Other'),
        # Add other zoning types here...
    ]
    CATEGORY = [
        ('residential', 'Residential'),
        ('commercial', 'Commercial'),
        ('industrial', 'Industrial'),
        ('vocational_renting', 'Vocational Renting'),
        ('land', 'Land'),
        ('mixed_use', 'Mixed Use'),
        ('retail', 'Retail'),
        ('office', 'Office'),
        ('warehouse', 'Warehouse'),
        ('hospitality', 'Hospitality'),
        ('special_purpose', 'Special Purpose'),
        ('agricultural', 'Agricultural'),
        ('other', 'Other'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, unique=True)
    option = models.CharField(max_length=10, choices=OPTIONS)
    email = models.EmailField(unique=True)
    description = models.TextField()
    phone_number = models.CharField(max_length=15)
    address = models.CharField(max_length=255)
    county = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    country = models.CharField(max_length=100)
    type = models.CharField(max_length=50, choices=TYPES)
    category = models.CharField(max_length=100, choices=CATEGORY)
    zoning = models.CharField(max_length=50, choices=ZONING)
    size = models.DecimalField(max_digits=10, decimal_places=2)
    special_feature = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=0)
    photo = models.ImageField(upload_to='media/properties/photos', default="avatars/proerty-empty.jpg")
    manager = models.OneToOneField('Manager', on_delete=models.SET_NULL, null=True, related_name='property_manager')
    tenant = models.ForeignKey('Tenant', on_delete=models.SET_NULL, null=True, related_name='rented_property')
    company = models.CharField(max_length=255)
    created = models.DateTimeField(default=timezone.now)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return self.name


class Manager(models.Model):
    COUNTRIES = [
        ('Kenya', 'Kenya'),
        ('Uganda', 'Uganda'),
        ('Tanzania', 'Tanzania'),
        ('Burundi', 'Burundi'),
        ('Comoros', 'Comoros'),
        ('Djobouti', 'Djobouti'),
        ('Eritrea', 'Eritrea'),
        ('Ethiopia', 'Ethiopia'),
        ('Madagascar', 'Madagascar'),
        ('Malawi', 'Malawi'),
        ('Mauritius', 'Mauritius'),
        ('Mozambique', 'Mozambique'),
        ('Rwanda', 'Rwanda'),
        ('Seychelles', 'Seychelles'),
        ('Somalia', 'Somalia'),
        ('South_sudan', 'South Sudan'),
        ('Zambia', 'Zambia'),
        ('Zimbabwe', 'Zimbabwe'),
        # Add other countries here...
    ]
    LANGUAGES = [
        ('Swahili', 'Swahili'),
        ('English', 'English'),
        ('French', 'French'),
        ('German', 'German'),
        ('Portuguese', 'Portuguese'),
        # Add other languages here...
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    description = models.TextField()
    property = models.OneToOneField(Property, on_delete=models.CASCADE, related_name='property_to_manage')
    phone_number = models.CharField(max_length=15)
    address = models.CharField(max_length=255)
    county = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    country = models.CharField(max_length=50, choices=COUNTRIES)
    language = models.CharField(max_length=50, choices=LANGUAGES)
    photo = models.ImageField(upload_to='media/managers', default="avatars/avatar.jpg")
    joined = models.DateTimeField(default=timezone.now)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    tenant = models.ForeignKey('Tenant', on_delete=models.SET_NULL, null=True, related_name='manager_test_chat')

    def __str__(self):
        return self.email


class ManagerRequest(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    description = models.TextField()
    phone_number = models.CharField(max_length=15)
    address = models.CharField(max_length=255)
    county = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    country = models.CharField(max_length=50, choices=Manager.COUNTRIES)
    language = models.CharField(max_length=50, choices=Manager.LANGUAGES)
    photo = models.ImageField(upload_to='media/managers', default="avatars/avatar.jpg")
    joined = models.DateTimeField(default=timezone.now)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)


class Tenant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    manager = models.ForeignKey('Manager', on_delete=models.CASCADE, null=True, related_name='tenants_manger')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='tenants')
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    id_no = models.CharField(max_length=20)
    phone_number = models.CharField(max_length=15)
    house_number = models.CharField(max_length=10)
    no_rooms = models.IntegerField(null=False)
    occupants = models.IntegerField()
    vehicle_no = models.CharField(max_length=15)
    tenant_id = models.CharField(max_length=20)
    sum_insured = models.DecimalField(max_digits=10, decimal_places=2)
    lease_start_date = models.DateField()
    lease_end_date = models.DateField()
    photo = models.ImageField(upload_to='media/tenants', default="avatars/avatar.jpg")
    joined = models.DateTimeField(default=timezone.now)
    balance = models.DecimalField(max_digits=100, decimal_places=2, default=0)
    last_payment_update_month = models.IntegerField(default=0)
    last_payment_update_year = models.IntegerField(default=0)
    total_monthly_payments = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return self.email


class TenantRequest(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    id_no = models.CharField(max_length=20)
    phone_number = models.CharField(max_length=15)
    house_number = models.CharField(max_length=10)
    no_rooms = models.IntegerField()
    occupants = models.IntegerField()
    vehicle_no = models.CharField(max_length=15)
    tenant_id = models.CharField(max_length=20)
    sum_insured = models.DecimalField(max_digits=10, decimal_places=2)
    lease_start_date = models.DateField()
    lease_end_date = models.DateField()
    photo = models.ImageField(upload_to='media/tenants', default="avatars/avatar.jpg")
    joined = models.DateTimeField(default=timezone.now)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)


class Payment(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    payment_id = models.CharField(max_length=100, unique=True, editable=False)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.payment_id:
            self.payment_id = self.generate_payment_id()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_payment_id():
        alphanumeric = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphanumeric) for _ in range(5))


STATUS = ((1, "Pending"), (0, "Complete"))


class MPesaPayment(Payment):
    phone_number = models.CharField(max_length=15)
    status = models.IntegerField(choices=STATUS, default=1)
    checkout_request_id = models.CharField(max_length=100, null=True, blank=True)


class MpesaResponseBody(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    body = models.JSONField()



class CreditCardPayment(Payment):
    COUNTRIES = [
        ('Kenya', 'Kenya'),
        ('Uganda', 'Uganda'),
        ('Tanzania', 'Tanzania'),
        ('Ethiopia', 'Ethiopia'),
        ('United States', 'United States'),
        ('Rwanda', 'Rwanda'),
        ('Somalia', 'Somalia'),
        ('South Sudan', 'South Sudan'),
        ('DR Congo', 'DR Congo'),
    ]
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    card_number = models.CharField(max_length=16)
    expiry_date = models.CharField(max_length=5)  # Format: MM/YY
    cvc = models.CharField(max_length=3)
    country = models.CharField(max_length=50, choices=COUNTRIES)


class PaypalPayment(Payment):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    text = models.TextField()
    image = models.ImageField(upload_to='reviews/images', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text[:50]


logger = logging.getLogger(__name__)


class Message(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='sent_messages')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_property_message = models.BooleanField(default=False)

    def __str__(self):
        return f'Message from {self.tenant.user.username} to Property {self.property.id}'


class ChatMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='property_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_received = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False)
    file = models.FileField(upload_to='messages/files', null=True, blank=True)

    def __str__(self):
        return self.content


class ScheduledMessage(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    message = models.TextField()
    send_at = models.DateTimeField()
    is_sent = models.BooleanField(default=False)

    def __str__(self):
        # Convert the send_at time to the user's timezone
        user_timezone = timezone.get_current_timezone()
        local_send_at = self.send_at.astimezone(user_timezone)
        return f"Scheduled message for {self.tenant.phone_number},{self.tenant.id} at {local_send_at.strftime('%Y-%m-%d %H:%M')} {user_timezone}"

    def save(self, *args, **kwargs):
        if self.send_at and self.send_at <= timezone.now():
            self.is_sent = True
        super().save(*args, **kwargs)


class Testimonial(models.Model):
    client_name = models.CharField(max_length=255)
    profession = models.CharField(max_length=255)
    rating = models.IntegerField()
    testimonial_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    photo = models.ImageField(upload_to='media/testimonials', default="avatars/avatar.jpg")

    def __str__(self):
        return self.client_name
