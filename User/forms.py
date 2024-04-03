from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Property, Manager, Tenant, User, MPesaPayment, CreditCardPayment, PaypalPayment, Testimonial, \
    ScheduledMessage, Message, Review
from phonenumber_field.phonenumber import to_python
from phonenumbers.phonenumberutil import is_possible_number
from django.core.exceptions import ValidationError


# from .error_codes import PaymentErrorCode


class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = ['name', 'option', 'email', 'description', 'phone_number', 'address', 'county', 'zip_code', 'country',
                  'type', 'category', 'zoning', 'size', 'special_feature', 'price', 'photo', 'company']
        widgets = {
            'option': forms.Select(attrs={'class': 'select2 form-select'}),
            'type': forms.Select(attrs={'class': 'select2 form-select'}),
            'category': forms.Select(attrs={'class': 'select2 form-select'}),
            'zoning': forms.Select(attrs={'class': 'select2 form-select'}),
        }


class ManagerForm(forms.ModelForm):
    property = forms.ModelChoiceField(queryset=Property.objects.filter(manager__isnull=True))

    class Meta:
        model = Manager
        fields = ['first_name', 'last_name', 'email', 'description', 'phone_number', 'address', 'county', 'zip_code',
                  'country', 'language', 'photo', 'property']
        widgets = {
            'country': forms.Select(choices=Manager.COUNTRIES, attrs={'class': 'select2 form-select'}),
            'language': forms.Select(choices=Manager.LANGUAGES, attrs={'class': 'select2 form-select'}),
        }


class TenantForm(forms.ModelForm):
    property = forms.ModelChoiceField(queryset=Property.objects.all())

    class Meta:
        model = Tenant
        fields = [
            'property', 'first_name', 'last_name', 'email', 'id_no', 'phone_number', 'house_number',
            'no_rooms', 'occupants', 'vehicle_no', 'tenant_id', 'sum_insured', 'lease_start_date', 'lease_end_date',
            'photo'
        ]


class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'type': 'password'}),
                                   label=("Old password"), strip=False)
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'type': 'password'}),
                                    label=("New password"), strip=False)
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'type': 'password'}),
                                    label=("Confirm new password"), strip=False)

    class Meta:
        fields = ['old_password', 'new_password1', 'new_password2']


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required. Enter a valid email address.')
    role = forms.ChoiceField(choices=User.ROLE_CHOICES)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'role')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already in use.')
        return email


class PaymentMethodForm(forms.Form):
    PAYMENT_METHODS = [
        ('mpesa', 'M-Pesa'),
        ('paypal', 'PayPal'),
        ('credit_card', 'Credit Card'),
    ]
    payment_method = forms.ChoiceField(choices=PAYMENT_METHODS)


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content']


class MPesaPaymentForm(forms.ModelForm):
    class Meta:
        model = MPesaPayment
        fields = ['phone_number', 'amount']

    amount = forms.IntegerField()

    def get_phone_number(self):
        return self.cleaned_data['phone_number']


class TestimonialForm(forms.ModelForm):
    class Meta:
        model = Testimonial
        fields = ['client_name', 'profession', 'rating', 'testimonial_text', 'photo']


class CreditCardPaymentForm(forms.ModelForm):
    class Meta:
        model = CreditCardPayment
        fields = ['first_name', 'last_name', 'card_number', 'expiry_date', 'cvc', 'country', 'amount']


class PaypalPaymentForm(forms.ModelForm):
    class Meta:
        model = PaypalPayment
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'amount']


class SendMessageForm(forms.Form):
    tenant_id = forms.IntegerField(widget=forms.HiddenInput)
    message = forms.CharField(label='Message', widget=forms.Textarea)


class ScheduledMessageForm(forms.ModelForm):
    class Meta:
        model = ScheduledMessage
        fields = ['tenant', 'message', 'send_at']
        widgets = {
            'send_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def clean_send_at(self):
        send_at = self.cleaned_data.get('send_at')
        if send_at is None:
            raise ValidationError("The 'send_at' field is required.")
        elif send_at <= timezone.now():
            raise ValidationError("The scheduled time can't be in the past.")
        return send_at


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['text', 'image']
