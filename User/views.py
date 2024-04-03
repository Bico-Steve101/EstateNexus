import json
import logging
import random
import string
from datetime import timedelta

import requests
from io import BytesIO
from itertools import chain
import pandas as pd
from celery.utils.log import get_task_logger

from django.contrib import messages as msg
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.hashers import check_password
from pyfcm import FCMNotification
from django.db import IntegrityError
from django.db.models import Count, Sum, Q
from django.http import HttpResponse, JsonResponse, HttpResponseServerError
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django_daraja.mpesa.core import MpesaClient

from .tasks import send_scheduled_messages
from twilio.rest import Client
from requests.auth import HTTPBasicAuth

from User.forms import PropertyForm, ManagerForm, TenantForm, SignUpForm, PaypalPaymentForm, \
    CreditCardPaymentForm, MPesaPaymentForm, CustomPasswordChangeForm, TestimonialForm, SendMessageForm, \
    ScheduledMessageForm, MessageForm, ReviewForm
from User.models import Property, Manager, Tenant, PaypalPayment, CreditCardPayment, MPesaPayment, ManagerRequest, \
    TenantRequest, User, Testimonial, ScheduledMessage, Message, ChatMessage, Review, Payment


def get_payment_mode(payment):
    if isinstance(payment, MPesaPayment):
        return "M-pesa"
    elif isinstance(payment, CreditCardPayment):
        return "Credit-card"
    elif isinstance(payment, PaypalPayment):
        return "Pay-pal"
    else:
        return "Unknown"


# Create your views here.
def index(request):
    properties = Property.objects.all()
    villa_properties = Property.objects.filter(type='villa')
    home_properties = Property.objects.filter(type='home')
    office_properties = Property.objects.filter(type='office')
    apartment_properties = Property.objects.filter(type='apartment')
    building_properties = Property.objects.filter(type='building')

    property_counts = Property.objects.filter(
        type__in=['home', 'villa', 'office', 'apartment', 'building']
    ).values('type').annotate(count=Count('type'))

    for property in properties:
        words = property.description.split()[:5]
        truncated_description = ' '.join(words)
        property.description = truncated_description

    owner_count = User.objects.filter(role='owner').count()
    manager_count = User.objects.filter(role='manager').count()
    tenant_count = User.objects.filter(role='tenant').count()
    total_properties = Property.objects.count()

    testimonials = Testimonial.objects.all()

    context = {
        'properties': properties,
        'villa_properties': villa_properties,
        'home_properties': home_properties,
        'office_properties': office_properties,
        'apartment_properties': apartment_properties,
        'building_properties': building_properties,
        'property_counts': property_counts,
        'owner_count': owner_count,
        'manager_count': manager_count,
        'tenant_count': tenant_count,
        'total_properties': total_properties,
        'testimonials': testimonials,
    }

    return render(request, 'EstateNexus/estatenexus/index.html', context)


def shop(request):
    properties = Property.objects.all()
    property_counts = Property.objects.filter(
        type__in=['home', 'villa', 'office', 'apartment', 'duplex']
    ).values('type').annotate(count=Count('type'))

    for property in properties:
        words = property.description.split()[:5]
        truncated_description = ' '.join(words)
        property.description = truncated_description
    context = {
        'properties': properties,
        'property_counts': property_counts,
    }
    return render(request, 'EstateNexus/estatenexus/shop.html', context)


def property_details(request, property_id):
    property = get_object_or_404(Property, id=property_id)
    property_counts = Property.objects.filter(
        type__in=['home', 'villa', 'office', 'apartment', 'duplex']
    ).values('type').annotate(count=Count('type')).order_by('type')
    related_properties = Property.objects.filter(type=property.type).exclude(pk=property_id)[:5]

    for related_property in related_properties:
        words = related_property.description.split()[:5]
        truncated_description = ' '.join(words)
        related_property.description = truncated_description

    context = {
        'property': property,
        'property_counts': property_counts,
        'related_properties': related_properties,

    }
    return render(request, 'EstateNexus/estatenexus/property-detail.html', context)


def contact_page(request):
    return render(request, 'EstateNexus/estatenexus/contact.html')


def cart(request):
    return render(request, 'EstateNexus/estatenexus/cart.html')


def checkout(request):
    return render(request, 'EstateNexus/estatenexus/checkout.html')


def add_testimonial(request):
    if request.method == 'POST':
        form = TestimonialForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/')  # Redirect to a page of your choice
    else:
        form = TestimonialForm()

    return render(request, 'EstateNexus/dark/add_testimonial.html', {'form': form})


def testimonial(request):
    testimonials = Testimonial.objects.all()

    context = {
        'testimonials': testimonials,
    }
    return render(request, 'EstateNexus/estatenexus/testimonial.html', context)


def about(request):
    return render(request, 'EstateNexus/estatenexus/about.html')


def error(request):
    return render(request, 'EstateNexus/estatenexus/404.html')


def access_denied(request):
    return render(request, 'EstateNexus/estatenexus/access-denied.html')


def authenticate_user(user_model, email, password):
    try:
        user_instance = user_model.objects.get(email=email)
        if check_password(password, user_instance.user.password):
            return user_instance
    except user_model.DoesNotExist:
        return None


def user_login(request):
    testimonial = Testimonial.objects.order_by('?').first()
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')  # Use email as username
            password = form.cleaned_data.get('password')

            # Check if the user is a manager
            manager = authenticate_user(Manager, email, password)
            if manager is not None:
                login(request, manager.user)
                return redirect('User:dashboard-property-details', property_id=manager.property.id)

            # Check if the user is a tenant
            tenant = authenticate_user(Tenant, email, password)
            if tenant is not None:
                login(request, tenant.user)
                return redirect('/')

            # Regular user authentication
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('User:index')

            msg.error(request, 'Invalid email or password.')
    else:
        form = AuthenticationForm()
    context = {
        'testimonial': testimonial,
        'form': form
    }
    return render(request, 'EstateNexus/estatenexus/login.html', context)


def logout_view(request):
    logout(request)
    return redirect('User:login')


def password_protected(request):
    return render(request, 'EstateNexus/estatenexus/password-protected.html')


def replace_password(request):
    return render(request, 'EstateNexus/estatenexus/replace-password.html')


def sign_up(request):
    testimonial = Testimonial.objects.order_by('?').first()
    if request.method == 'POST':
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            if user.role == 'owner':
                return redirect('User:add-property')
            elif user.role == 'manager':
                return redirect('User:add-managers')
            elif user.role == 'tenant':
                return redirect('User:add-tenant')
    else:
        form = SignUpForm()
    context = {
        'testimonial': testimonial,
        'form': form
    }
    return render(request, 'EstateNexus/estatenexus/signup.html', context)


def update_password(request):
    testimonial = Testimonial.objects.order_by('?').first()
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            msg.success(request, 'Your password was updated successfully. 😊 You were automatically logged in and '
                                      'can continue your session!.')
            return redirect('User:update-password')
        else:
            msg.error(request, 'There was an error updating your password. Please try again, or contact us if '
                                    'you continue to have problems.!')
    else:
        form = CustomPasswordChangeForm(request.user)
    context = {
        'testimonial': testimonial,
        'form': form
    }
    return render(request, 'EstateNexus/estatenexus/update-password.html', context)


def user_account(request):
    return render(request, 'EstateNexus/estatenexus/user-account.html')


def dashboard(request):
    # Fetch recent activities within the last 5 days
    today = timezone.now()
    five_days_ago = today - timedelta(days=5)
    three_days_ago = today - timedelta(days=3)

    properties = Property.objects.filter(user=request.user)
    managers = Manager.objects.filter(property__in=properties)
    manager_requests = ManagerRequest.objects.filter(property__user=request.user, joined__gte=five_days_ago)
    tenant_requests = TenantRequest.objects.filter(property__user=request.user, joined__gte=five_days_ago)

    # Fetch recent payments for each payment method
    recent_mpesa_payments = MPesaPayment.objects.filter(tenant__property__user=request.user, payment_date__gte=five_days_ago)
    recent_credit_card_payments = CreditCardPayment.objects.filter(tenant__property__user=request.user, payment_date__gte=five_days_ago)
    recent_paypal_payments = PaypalPayment.objects.filter(tenant__property__user=request.user, payment_date__gte=five_days_ago)

    # Combine all recent payments into one queryset
    recent_payments = list(recent_mpesa_payments) + list(recent_credit_card_payments) + list(recent_paypal_payments)

    recent_reviews = Review.objects.filter(property__user=request.user, created_at__gte=three_days_ago)

    context = {
        'properties': properties,
        'managers': managers,
        'manager_requests': manager_requests,
        'tenant_requests': tenant_requests,
        'recent_payments': recent_payments,
        'recent_reviews': recent_reviews,
    }
    return render(request, 'EstateNexus/dark/index.html', context)


def dashboard_sales(request):
    try:
        # Retrieve the properties owned by the user
        user = request.user
        properties = Property.objects.filter(user=user)

        # Initialize empty lists to store payments and payment statuses for all properties
        all_payments = []
        payment_statuses = {}

        # Iterate over each property
        for property_object in properties:
            # Retrieve all payments made to the specific property
            mpesa_payments = MPesaPayment.objects.filter(tenant__property=property_object)
            credit_card_payments = CreditCardPayment.objects.filter(tenant__property=property_object)
            paypal_payments = PaypalPayment.objects.filter(tenant__property=property_object)

            # Combine payments for the current property into a single queryset
            property_payments = list(mpesa_payments) + list(credit_card_payments) + list(paypal_payments)

            # Append payments for the current property to the overall list of payments
            all_payments.extend(property_payments)

            # Calculate total payments for the current month for the current property
            current_month = timezone.now().month
            current_year = timezone.now().year
            monthly_payments = sum(
                payment.amount
                for payment in property_payments
                if payment.payment_date.month == current_month and payment.payment_date.year == current_year
            )

            # Determine payment status for the current property
            if monthly_payments < property_object.price:
                payment_status = "Pending"
            elif monthly_payments == property_object.price:
                payment_status = "Completed"
            else:
                payment_status = "Excess"

            # Store payment status for the current property
            payment_statuses[property_object.id] = payment_status

        # Calculate total payment made by the user for all properties
        total_property_payments = sum(payment.amount for payment in all_payments)

        # Calculate counts for all payments, pending payments, and completed payments
        total_payments_count = len(all_payments)
        pending_payments_count = len([payment for payment in all_payments if payment.amount < property_object.price])
        completed_payments_count = len([payment for payment in all_payments if payment.amount == property_object.price])
        excess_payments_count = total_payments_count - pending_payments_count - completed_payments_count

        # Render the payments page with the payments queryset and other context variables
        return render(request, 'EstateNexus/dark/dashboard-sales.html', {
            'payments': all_payments,
            'properties': properties,
            'payment_statuses': payment_statuses,
            'total_property_payments': total_property_payments,
            'total_payments_count': total_payments_count,
            'pending_payments_count': pending_payments_count,
            'completed_payments_count': completed_payments_count,
            'excess_payments_count': excess_payments_count,
            'get_payment_mode': get_payment_mode,  # Pass the function to the template context
        })

    except Property.DoesNotExist:
        return HttpResponse("Property not found")


def managers(request):
    user = request.user
    user_properties = Property.objects.filter(user=user)
    managers = Manager.objects.filter(property__in=user_properties)
    context = {
        'managers': managers,
    }
    return render(request, 'EstateNexus/dark/managers.html', context)


def add_managers(request):
    properties = Property.objects.filter(manager__isnull=True)
    if request.method == 'POST':
        form = ManagerForm(request.POST, request.FILES)
        if form.is_valid():
            property_id = form.cleaned_data['property'].id
            property_instance = Property.objects.get(id=property_id)
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            description = form.cleaned_data['description']
            phone_number = form.cleaned_data['phone_number']
            address = form.cleaned_data['address']
            county = form.cleaned_data['county']
            zip_code = form.cleaned_data['zip_code']
            country = form.cleaned_data['country']
            language = form.cleaned_data['language']
            photo = form.cleaned_data['photo']

            if property_instance.manager:
                msg.error(request, 'This property already has a manager assigned. 😊')
            else:
                manager_request = ManagerRequest(property=property_instance, user=request.user, first_name=first_name,
                                                 last_name=last_name, email=email, description=description,
                                                 phone_number=phone_number,
                                                 address=address, county=county, zip_code=zip_code, country=country,
                                                 language=language,
                                                 photo=photo)
                manager_request.save()

                msg.success(request, 'Manager request sent successfully. 😊')
                return redirect('User:index')
    else:
        form = ManagerForm()
    return render(request, 'EstateNexus/dark/add-manager.html', {'form': form, 'properties': properties})


def respond_to_request(request, request_id, response):
    manager_request = get_object_or_404(ManagerRequest, id=request_id)
    if response == 'accept':
        try:
            new_manager = Manager.objects.create(
                user=manager_request.user,
                first_name=manager_request.first_name,
                last_name=manager_request.last_name,
                email=manager_request.email,
                description=manager_request.description,
                phone_number=manager_request.phone_number,
                address=manager_request.address,
                county=manager_request.county,
                zip_code=manager_request.zip_code,
                country=manager_request.country,
                language=manager_request.language,
                photo=manager_request.photo,
                property=manager_request.property,
                joined=manager_request.joined,
            )
            # Assign the manager to the property
            property_instance = manager_request.property
            property_instance.manager = new_manager
            property_instance.save()
        except IntegrityError:
            msg.error(request, 'An error occurred while creating the Manager object.')
    try:
        manager_request.delete()
    except Exception as e:
        msg.error(request, 'An error occurred while deleting the ManagerRequest object.')
    return redirect('User:dashboard')


def add_tenant(request):
    properties = Property.objects.filter(manager__isnull=False)

    if request.method == 'POST':
        form = TenantForm(request.POST, request.FILES)
        if form.is_valid():
            property_id = form.cleaned_data['property'].id
            property_instance = Property.objects.get(id=property_id)
            email = form.cleaned_data['email']
            no_rooms = form.cleaned_data['no_rooms']
            occupants = form.cleaned_data['occupants']
            sum_insured = form.cleaned_data['sum_insured']
            lease_start_date = form.cleaned_data['lease_start_date']
            lease_end_date = form.cleaned_data['lease_end_date']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            tenant_id = form.cleaned_data['tenant_id']
            photo = form.cleaned_data['photo']
            vehicle_no = form.cleaned_data['vehicle_no']
            id_no = form.cleaned_data['id_no']
            house_number = form.cleaned_data['house_number']

            if property_instance.tenant:
                msg.error(request, 'A tenant with this email already exists for this property.')
            elif not no_rooms:
                msg.error(request, 'The number of rooms must be provided.')
            elif not occupants:
                msg.error(request, 'The number of occupants must be provided.')
            else:
                manager = property_instance.manager

                tenant_request = TenantRequest(
                    property=property_instance,
                    user=request.user,
                    email=email,
                    no_rooms=no_rooms,
                    occupants=occupants,
                    sum_insured=sum_insured,
                    lease_start_date=lease_start_date,
                    lease_end_date=lease_end_date,
                    first_name=first_name,
                    last_name=last_name,
                    phone_number=phone_number,
                    tenant_id=tenant_id,
                    photo=photo,
                    vehicle_no=vehicle_no,
                    id_no=id_no,
                    house_number=house_number
                )
                tenant_request.save()
                msg.success(request, 'Tenant request sent successfully. 😊')
                return redirect('User:index')
    else:
        form = TenantForm()

    return render(request, 'EstateNexus/dark/add-tenant.html', {'form': form, 'properties': properties})


def respond_to_tenant_request(request, request_id, response):
    tenant_request = get_object_or_404(TenantRequest, id=request_id)
    if response == 'accept':
        try:
            property_instance = tenant_request.property
            new_tenant = Tenant.objects.create(
                user=tenant_request.user,
                first_name=tenant_request.first_name,
                last_name=tenant_request.last_name,
                email=tenant_request.email,
                id_no=tenant_request.id_no,
                phone_number=tenant_request.phone_number,
                house_number=tenant_request.house_number,
                no_rooms=tenant_request.no_rooms,
                occupants=tenant_request.occupants,
                vehicle_no=tenant_request.vehicle_no,
                tenant_id=tenant_request.tenant_id,
                sum_insured=tenant_request.sum_insured,
                lease_start_date=tenant_request.lease_start_date,
                lease_end_date=tenant_request.lease_end_date,
                photo=tenant_request.photo,
                property=property_instance,
                joined=tenant_request.joined,
                manager=property_instance.manager,  # Assign the manager of the property to the tenant
            )
        except IntegrityError:
            msg.error(request, 'An error occurred while creating the Tenant object.')
    try:
        tenant_request.delete()
    except Exception as e:
        msg.error(request, 'An error occurred while deleting the TenantRequest object.')
    return redirect('User:dashboard')


@login_required
def properties(request):
    user = request.user
    user_properties = Property.objects.filter(user=user)
    rent_count = Property.objects.filter(user=user, option='rent').count()
    sale_count = Property.objects.filter(user=user, option='sale').count()
    manager_count = Manager.objects.filter(property__in=user_properties).count()

    # Count the number of tenants for each property
    tenant_counts = {property.id: property.tenants.count() for property in user_properties}

    context = {
        'user_properties': user_properties,
        'manager_count': manager_count,
        'rent_count': rent_count,
        'sale_count': sale_count,
        'tenant_counts': tenant_counts,  # Add tenant_counts to the context
    }
    return render(request, 'EstateNexus/dark/properties.html', context)


def property_contact(request, property_id):
    try:
        # Retrieve the property object
        property = get_object_or_404(Property, id=property_id)

        # Retrieve tenants
        tenants = property.tenants.all()
        num_tenants = tenants.count()

        # Retrieve all payments made to the specific property
        mpesa_payments = MPesaPayment.objects.filter(tenant__property=property)
        credit_card_payments = CreditCardPayment.objects.filter(tenant__property=property)
        paypal_payments = PaypalPayment.objects.filter(tenant__property=property)

        # Combine all payment types into a single queryset
        all_payments = list(mpesa_payments) + list(credit_card_payments) + list(paypal_payments)

        # Calculate total payments for the current month
        current_month = timezone.now().month
        current_year = timezone.now().year
        monthly_payments = sum(
            payment.amount
            for payment in all_payments
            if payment.payment_date.month == current_month and payment.payment_date.year == current_year
        )

        # Calculate total payment made by the tenants for the property
        total_property_payments = sum(payment.amount for payment in all_payments)

        # Determine payment status
        if monthly_payments < property.price:
            payment_status = "Pending"
        elif monthly_payments == property.price:
            payment_status = "Completed"
        else:
            payment_status = "Excess"

        # Retrieve messages related to the property
        messages = ChatMessage.objects.filter(property=property).order_by('timestamp')
        reviews = Review.objects.filter(property=property)

        if request.method == 'POST':
            form = ReviewForm(request.POST, request.FILES)
            if form.is_valid():
                review = form.save(commit=False)
                review.user = request.user
                review.property = property
                review.save()
                return redirect('User:property_contact', property_id=property_id)
        else:
            form = ReviewForm()

        # Render the property contact page with the property, tenants, and payment details
        context = {
            'property': property,
            'reviews': reviews,
            'form': form,
            'tenants': tenants,
            'num_tenants': num_tenants,
            'payments': all_payments,
            'monthly_payments': monthly_payments,
            'total_property_payments': total_property_payments,
            'payment_status': payment_status,
            'get_payment_mode': get_payment_mode,  # Pass the function to the template context
            'messages': messages,  # Add messages to the context
        }

        return render(request, 'EstateNexus/dark/property-contact.html', context)

    except Property.DoesNotExist:
        return HttpResponse("Property not found")


def generate_invoice_id(length=5, use_uppercase=True, use_lowercase=True, use_digits=True):
    """
    Generate a random invoice ID.

    The ID consists of alphanumeric characters. Special characters are excluded for readability and to avoid confusion.

    Args:
    length (int): The length of the invoice ID. Default is 5.
    use_uppercase (bool): Whether to include uppercase letters in the ID. Default is True.
    use_lowercase (bool): Whether to include lowercase letters in the ID. Default is True.
    use_digits (bool): Whether to include digits in the ID. Default is True.

    Returns:
    str: Randomly generated invoice ID.
    """
    characters = ''
    if use_uppercase:
        characters += string.ascii_uppercase
    if use_lowercase:
        characters += string.ascii_lowercase
    if use_digits:
        characters += string.digits

    if not characters:
        raise ValueError("At least one character set must be chosen")

    return ''.join(random.choice(characters) for _ in range(length))


@login_required
def tenant_profile(request, tenant_id):
    try:
        tenant = get_object_or_404(Tenant, id=tenant_id)
        property_occupied = tenant.property
        mpesa_payments = tenant.mpesapayment_set.all()
        credit_card_payments = tenant.creditcardpayment_set.all()
        paypal_payments = tenant.paypalpayment_set.all()
        all_payments = list(chain(mpesa_payments, credit_card_payments, paypal_payments))

        # Calculate monthly payments
        current_month = timezone.now().month
        current_year = timezone.now().year
        monthly_payments = sum(
            payment.amount
            for payment in all_payments
            if payment.payment_date.month == current_month and payment.payment_date.year == current_year
        )
        # Update tenant's total monthly payments and balance
        tenant.total_monthly_payments = monthly_payments
        tenant.balance = tenant.property.price - tenant.total_monthly_payments
        tenant.save()
        # Calculate total all-time payments
        total_all_time_payments = sum(payment.amount for payment in all_payments)
        # Calculate payment percentages
        mpesa_percentage = (mpesa_payments.aggregate(total=Sum('amount'))[
                                'total'] or 0) / total_all_time_payments * 100 if total_all_time_payments > 0 else 0
        credit_card_percentage = (credit_card_payments.aggregate(total=Sum('amount'))[
                                      'total'] or 0) / total_all_time_payments * 100 if total_all_time_payments > 0 else 0
        paypal_percentage = (paypal_payments.aggregate(total=Sum('amount'))[
                                 'total'] or 0) / total_all_time_payments * 100 if total_all_time_payments > 0 else 0
        # Retrieve messages related to the tenant and the property
        messages = ChatMessage.objects.filter(
            Q(sender=tenant.user, receiver=tenant.property.manager.user) |
            Q(sender=tenant.property.manager.user, receiver=tenant.user)
        ).order_by('timestamp')

        reviews = Review.objects.filter(property=property_occupied)

        if request.method == 'POST':
            form = ReviewForm(request.POST, request.FILES)
            if form.is_valid():
                review = form.save(commit=False)
                review.user = request.user
                review.property = property_occupied
                review.save()
                return redirect('User:tenant_profile', tenant_id=tenant_id)
        else:
            form = ReviewForm()

        context = {
            'tenant': tenant,
            'property_occupied': property_occupied,
            'payments': all_payments,
            'balance': tenant.balance,
            'total_monthly_payments': tenant.total_monthly_payments,
            'total_all_time_payments': total_all_time_payments,
            'property_price': tenant.property.price,
            'mpesa_percentage': mpesa_percentage,
            'credit_card_percentage': credit_card_percentage,
            'paypal_percentage': paypal_percentage,
            'messages': messages,
            'room_name': str(tenant_id),
            'reviews': reviews,
            'form': form,
        }
        return render(request, 'EstateNexus/dark/tenant-profile.html', context)
    except Tenant.DoesNotExist:
        return redirect('User:index')


@require_POST
def mark_all_messages_as_read(request):
    ChatMessage.objects.filter(receiver=request.user, is_read=False).update(is_read=True)
    return JsonResponse({"success": True})


def send_push_notification(to_user, message):
    push_service = FCMNotification(api_key="<your-server-key>")
    registration_id = to_user.fcm_token  # You need to store FCM tokens for each user
    message_title = "New message from " + message.sender.username
    message_body = message.content
    result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title,
                                               message_body=message_body)
    return result


def getAccessToken(request):
    consumer_key = 'sGxb5imn3ePLbcNKeaUiVKpIxNtWQkO8DDH6qEJJpCZGFwGy'
    consumer_secret = 'S55sSNaKNWUS1TsG7DTWxZdgmlULDhAqRSGGCfzp0YGNaoJILwKfGwjRAJLG39ki'
    api_URL = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'

    response = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))

    if response.status_code == 200:
        json_response = response.json()
        access_token = json_response['access_token']
        return HttpResponse(access_token)
    else:
        return HttpResponse('Failed to get access token')


@login_required
def mpesa_payment(request):
    tenant = Tenant.objects.get(user=request.user)
    testimonial = Testimonial.objects.order_by('?').first()
    if request.method == 'POST':
        form = MPesaPaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            if payment.amount < 1:
                msg.error(request, 'Minimum M-pesa payment amount is 10.')
                return render(request, 'EstateNexus/dark/mpesa_payment.html', {'form': form, 'tenant': tenant})

            # Create a MpesaClient instance
            client = MpesaClient()

            # Define the Lipa na M-Pesa Online Payment parameters
            PhoneNumber = form.cleaned_data['phone_number']
            Amount = int(payment.amount)  # Convert the amount to an integer
            AccountReference = str(request.user.id)  # Pass the user's ID as the account reference
            TransactionDesc = 'Payment for invoice 001'
            CallBackURL = 'https://api.darajambili.com/express-payment/mpesa/callback/'

            # Make the Lipa na M-Pesa Online Payment API request
            response = client.stk_push(PhoneNumber, Amount, AccountReference, TransactionDesc, CallBackURL)

            # Check if the request was successful
            if response.status_code == 200 and response.json().get('ResponseCode') == '0':
                msg.info(request, 'STK push sent. Please check your phone to complete the payment.')
                return redirect('User:tenant-profile')
            else:
                msg.error(request, 'M-Pesa payment was unsuccessful. Please try again.')

    else:
        form = MPesaPaymentForm()
    context = {
        'testimonial': testimonial,
        'form': form,
        'tenant': tenant
    }
    return render(request, 'EstateNexus/dark/mpesa_payment.html', context)


@csrf_exempt
def mpesa_callback(request):
    if request.method == 'POST':
        # Parse the JSON request body
        data = json.loads(request.body)

        # Extract the transaction details
        transaction_id = data.get('Body', {}).get('stkCallback', {}).get('CheckoutRequestID')
        result_code = data.get('Body', {}).get('stkCallback', {}).get('ResultCode')
        result_desc = data.get('Body', {}).get('stkCallback', {}).get('ResultDesc')
        amount = data.get('Body', {}).get('stkCallback', {}).get('CallbackMetadata', {}).get('Item', [{}])[0].get(
            'Value')
        phone_number = data.get('Body', {}).get('stkCallback', {}).get('CallbackMetadata', {}).get('Item', [{}])[1].get(
            'Value')
        tenant_id = data.get('Body', {}).get('stkCallback', {}).get('CallbackMetadata', {}).get('Item', [{}])[2].get(
            'Value')

        # Check the result code
        if result_code == 0:
            # Payment was successful
            # Create a new MPesaPayment object
            tenant = Tenant.objects.get(id=tenant_id)  # Get the tenant using the ID
            payment = MPesaPayment.objects.create(
                tenant=tenant,
                amount=amount,
                phone_number=phone_number,
                payment_id=transaction_id,
                status='completed'
            )
            return JsonResponse({'ResultCode': 0, 'ResultDesc': 'Success'})
        else:
            # Payment failed
            return JsonResponse({'ResultCode': 1, 'ResultDesc': result_desc})

    return JsonResponse({'message': 'Invalid request method'}, status=400)


@login_required
def paypal_payment(request):
    tenant = Tenant.objects.get(user=request.user)
    testimonial = Testimonial.objects.order_by('?').first()
    if request.method == 'POST':
        form = PaypalPaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            if payment.amount < 10:
                msg.error(request, 'Minimum PayPal payment amount is 10.')
                return render(request, 'EstateNexus/dark/paypal_payment.html', {'form': form, 'tenant': tenant})
            payment.tenant = tenant
            payment.save()
            msg.success(request, 'Paypal payment was successful.')
            return redirect('User:tenant-profile')
        else:
            msg.error(request, 'Paypal payment was unsuccessful. Please try again.')
    else:
        form = PaypalPaymentForm()
    context = {
        'testimonial': testimonial,
        'form': form,
        'tenant': tenant
    }
    return render(request, 'EstateNexus/dark/paypal_payment.html', context)


@login_required
def credit_card_payment(request):
    tenant = Tenant.objects.get(user=request.user)
    testimonial = Testimonial.objects.order_by('?').first()
    if request.method == 'POST':
        form = CreditCardPaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            if payment.amount < 10:
                msg.error(request, 'Minimum Credit-Card payment amount is 10.')
                return render(request, 'EstateNexus/dark/credit_card_payment.html', {'form': form, 'tenant': tenant})
            payment.tenant = tenant
            payment.save()
            msg.success(request, 'Credit card payment was successful.')
            return redirect('User:tenant-profile')
        else:
            msg.error(request, 'Credit card payment was unsuccessful. Please try again.')
    else:
        form = CreditCardPaymentForm()
    context = {
        'testimonial': testimonial,
        'form': form,
        'tenant': tenant
    }
    return render(request, 'EstateNexus/dark/credit_card_payment.html', context)


logger = get_task_logger(__name__)

account_sid = 'AC9e35e109ca7de1d8892cc7e00908c6ea'
auth_token = 'eeb9e3b2a960093dacdc3330bdb046a4'
twilio_phone_number = '+12098878105'


@login_required
def send_message(request, property_id):
    if request.method == 'POST':
        form = SendMessageForm(request.POST)
        if form.is_valid():
            client = Client(account_sid, auth_token)
            tenant_id = form.cleaned_data.get('tenant_id')
            tenant = get_object_or_404(Tenant, id=tenant_id)
            message = form.cleaned_data.get('message')

            # Check if the message is empty
            if not message.strip():
                msg.error(request, 'Message cannot be empty.')
                return redirect('User:payments', property_id=property_id)

            try:
                client.messages.create(
                    body=f'EstateNexus, you have a message from "{tenant.property.name}": {message}',
                    from_=twilio_phone_number,
                    to=tenant.phone_number
                )
                msg.success(request, 'Message sent successfully!')
                logger.info(f'Message sent to tenant {tenant_id}.')
            except Exception as e:
                msg.error(request, f'Failed to send message: {str(e)}')
                logger.error(f'Failed to send message to tenant {tenant_id}: {str(e)}')

    return redirect('User:payments', property_id=property_id)


@login_required
def schedule_message(request, property_id):
    if request.method == 'POST':
        date = request.POST.get('send_at_0')
        time = request.POST.get('send_at_1')
        send_at = f'{date} {time}'
        post_data = request.POST.copy()
        post_data['send_at'] = send_at

        form = ScheduledMessageForm(post_data)
        if form.is_valid():
            try:
                scheduled_message = form.save()
                send_scheduled_messages.apply_async()  # Schedule the task
                msg.success(request, 'Scheduled message added successfully!')
            except Exception as e:
                msg.error(request, f'Failed to add scheduled message:{str(e)}')
        else:
            msg.error(request, f'Failed to schedule message: {form.errors}')
        return redirect('User:payments', property_id=property_id)


# @shared_task(bind=True, max_retries=3)
# def send_scheduled_messages(self):
#     client = Client(account_sid, auth_token)
#     messages = ScheduledMessage.objects.filter(send_at__lte=timezone.now(), is_sent=False)
#     for message in messages:
#         try:
#             client.messages.create(
#                 body=f'EstateNexus, you have a message from "{message.tenant.property.name}": {message.message}',
#                 from_=twilio_phone_number,
#                 to=message.tenant.phone_number
#             )
#             message.is_sent = True
#             message.save()
#             self.logger.info(f'Successfully sent message {message.id} to {message.tenant.phone_number}')
#         except Exception as e:
#             self.logger.error(f'Failed to send message {message.id} to {message.tenant.phone_number}: {str(e)}')
#             message.send_at = timezone.now() + timedelta(minutes=5)
#             message.save()
#             try:
#                 self.retry(countdown=60 * 5)  # Retry in 5 minutes
#             except self.MaxRetriesExceededError:
#                 self.logger.error(f'Failed to send message {message.id} after maximum retries')


@login_required
def payments(request, property_id):
    property = get_object_or_404(Property, id=property_id)
    tenants = Tenant.objects.filter(property=property)

    mpesa_payments = MPesaPayment.objects.filter(tenant__in=tenants)
    credit_card_payments = CreditCardPayment.objects.filter(tenant__in=tenants)
    paypal_payments = PaypalPayment.objects.filter(tenant__in=tenants)
    all_payments = list(chain(mpesa_payments, credit_card_payments, paypal_payments))
    current_month = timezone.now().month
    current_year = timezone.now().year
    monthly_payments = sum(
        payment.amount
        for payment in all_payments
        if payment.payment_date.month == current_month and payment.payment_date.year == current_year
    )
    total_tenant_payments = sum(payment.amount for payment in all_payments)

    for tenant in tenants:
        tenant_payments = [payment for payment in all_payments if payment.tenant == tenant]
        tenant_monthly_payments = sum(
            payment.amount
            for payment in tenant_payments
            if payment.payment_date.month == current_month and payment.payment_date.year == current_year
        )
        for payment in tenant_payments:
            if tenant_monthly_payments < property.price:
                payment.status = "Pending"
            elif tenant_monthly_payments > property.price:
                payment.status = "Excess"
            else:
                payment.status = "Completed"

    total_payments_count = len(all_payments)
    pending_payments_count = len([payment for payment in all_payments if payment.status == "Pending"])
    completed_payments_count = len([payment for payment in all_payments if payment.status == "Completed"])
    excess_payments_count = total_payments_count - pending_payments_count - completed_payments_count

    context = {
        'payments': all_payments,
        'property': property,
        'monthly_payments': monthly_payments,
        'total_tenant_payments': total_tenant_payments,
        'total_payments_count': total_payments_count,
        'pending_payments_count': pending_payments_count,
        'completed_payments_count': completed_payments_count,
        'excess_payments_count': excess_payments_count,
    }

    return render(request, 'EstateNexus/dark/payments.html', context)


@login_required
def invoice(request):
    try:
        tenants = Tenant.objects.filter(user=request.user)
        if tenants.exists():
            tenant = tenants.first()
            property_occupied = tenant.property
            property_manager = property_occupied.manager

        # Get all payment records for the tenant
        mpesa_payments = MPesaPayment.objects.filter(tenant=tenant)
        credit_card_payments = CreditCardPayment.objects.filter(tenant=tenant)
        paypal_payments = PaypalPayment.objects.filter(tenant=tenant)
        all_payments = list(chain(mpesa_payments, credit_card_payments, paypal_payments))

        # Assign a unique invoice ID to the invoice
        invoice_id = generate_invoice_id()

        # Attach the invoice ID to each payment
        for payment in all_payments:
            payment.invoice_id = invoice_id

        # Calculate total payments for the current month
        current_month = timezone.now().month
        current_year = timezone.now().year
        monthly_payments = sum(
            payment.amount
            for payment in all_payments
            if payment.payment_date.month == current_month and payment.payment_date.year == current_year
        )

        # Update tenant's monthly payment records if month has changed
        if tenant.last_payment_update_month != current_month or tenant.last_payment_update_year != current_year:
            tenant.total_monthly_payments = monthly_payments
            tenant.last_payment_update_month = current_month
            tenant.last_payment_update_year = current_year
            tenant.save()

        # Calculate total all-time payments (sum of all payments made by the tenant)
        total_all_time_payments = sum(payment.amount for payment in all_payments)

        # Calculate balance based on monthly rent and total monthly payments
        balance = tenant.property.price - tenant.total_monthly_payments

        # Attach the mode name and balance to each payment
        for payment in all_payments:
            payment.mode = get_payment_mode(payment)
            payment.balance = tenant.property.price - payment.amount

        # Calculate percentages based on total all-time payments
        mpesa_percentage = (mpesa_payments.aggregate(total=Sum('amount'))[
                                'total'] or 0) / total_all_time_payments * 100 if total_all_time_payments > 0 else 0
        credit_card_percentage = (credit_card_payments.aggregate(total=Sum('amount'))[
                                      'total'] or 0) / total_all_time_payments * 100 if total_all_time_payments > 0 else 0
        paypal_percentage = (paypal_payments.aggregate(total=Sum('amount'))[
                                 'total'] or 0) / total_all_time_payments * 100 if total_all_time_payments > 0 else 0

        context = {
            'tenant': tenant,
            'property_occupied': property_occupied,
            'payments': all_payments,
            'invoice_id': invoice_id,
            'balance': balance,
            'total_monthly_payments': tenant.total_monthly_payments,
            'total_all_time_payments': total_all_time_payments,
            'mpesa_percentage': mpesa_percentage,
            'credit_card_percentage': credit_card_percentage,
            'paypal_percentage': paypal_percentage,
            'property_manager': property_manager,
        }
        return render(request, 'EstateNexus/dark/page-invoice.html', context)

    except Tenant.DoesNotExist:
        return redirect('User:index')


def calendar(request):
    return render(request, 'EstateNexus/dark/calendar.html')


def managers_profile(request, manager_id):
    manager = get_object_or_404(Manager, id=manager_id)
    properties = Property.objects.filter(manager=manager)
    context = {
        'manager': manager,
        'properties': properties,
    }
    return render(request, 'EstateNexus/dark/managers-profile.html', context)


def dashboard_property_detail(request, property_id):
    property = get_object_or_404(Property, id=property_id)
    user = request.user
    is_tenant = hasattr(user, 'tenant')
    property_occupied = None

    if is_tenant:
        try:
            tenant = user.tenant
            property_occupied = tenant.property
        except Tenant.DoesNotExist:
            pass

    tenants = property.tenants.all()
    num_tenants = tenants.count()

    is_manager = hasattr(user, 'manager')
    manager = Manager.objects.filter(property=property).first()

    reviews = Review.objects.filter(property=property)

    if request.method == 'POST':
        form = ReviewForm(request.POST, request.FILES)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.property = property
            review.save()
            return redirect('User:dashboard-property-details', property_id=property_id)
    else:
        form = ReviewForm()

    context = {
        'property': property,
        'property_occupied': property_occupied,
        'tenants': tenants,
        'num_tenants': num_tenants,
        'is_tenant': is_tenant,
        'is_manager': is_manager,
        'manager': manager,
        'reviews': reviews,
        'form': form,
    }
    return render(request, 'EstateNexus/dark/property-details.html', context)


def add_property(request):
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            property = form.save(commit=False)
            property.user = request.user
            property.save()
            return redirect('User:index')
    else:
        form = PropertyForm()
    return render(request, 'EstateNexus/dark/add-property.html', {'form': form})


def getting_started(request):
    return render(request, 'EstateNexus/dark/getting-started.html')


@login_required
@csrf_exempt
@require_POST
def download(request):
    selected_rows = json.loads(request.body.decode('utf-8')).get('selected_rows')

    df = pd.DataFrame(selected_rows)

    excel_file = BytesIO()
    xls_writer = pd.ExcelWriter(excel_file, engine='xlsxwriter')
    df.to_excel(xls_writer, index=False)
    xls_writer.save()

    excel_file.seek(0)
    response = HttpResponse(excel_file.read(), content_type='application/vnd.openxmlformats-officedocument'
                                                            '.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=Payments.xlsx'

    return response

# @login_required
# def send_message_to_tenants(request):
#     if request.method == 'POST':
#         form = SendMessageForm(request.POST)
#         if form.is_valid():
#             # Get Twilio credentials
#             account_sid = 'your_account_sid'
#             auth_token = 'your_auth_token'
#             twilio_phone_number = 'your_twilio_phone_number'
#
#             # Initialize Twilio client
#             client = Client(account_sid, auth_token)
#
#             # Get tenant ID from the form data
#             tenant_id = form.cleaned_data.get('tenant_id')
#
#             # Get tenant object
#             tenant = get_object_or_404(Tenant, id=tenant_id)
#
#             # Get message from the form data
#             message = form.cleaned_data.get('message')
#
#             try:
#                 # Send SMS message
#                 client.messages.create(
#                     body=message,
#                     from_=twilio_phone_number,
#                     to=tenant.phone_number
#                 )
#                 messages.success(request, 'Message sent successfully!')
#             except Exception as e:
#                 messages.error(request, f'Failed to send message: {str(e)}')
#
#             # Redirect to success page or any other page
#             return redirect('User:payment_page')
#     else:
#         form = SendMessageForm()  # Create an empty form
#         return render(request, 'send_message.html', {'form': form})
