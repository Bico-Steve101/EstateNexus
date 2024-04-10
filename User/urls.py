from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from User import views

app_name = "User"

urlpatterns = [
                  path('', views.index, name="index"),
                  path('shop/', views.shop, name="shop"),
                  path('property/<str:property_id>/', views.property_details, name='property_details'),
                  path('contact-page/', views.contact_page, name="contact-page"),
                  path('cart/', views.cart, name="cart"),
                  path('checkout/', views.checkout, name="checkout"),
                  path('testimonial/', views.testimonial, name="testimonial"),
                  path('about/', views.about, name="about"),
                  path('error/', views.error, name="error"),
                  path('access-denied/', views.access_denied, name="access-denied"),
                  path('login/', views.user_login, name="login"),
                  path('logout/', views.logout_view, name='logout'),
                  path('sign-up/', views.sign_up, name="signup"),
                  path('password-protected/', views.password_protected, name="password_protected"),
                  path('replace-password/', views.replace_password, name="replace-password"),
                  path('update-password/', views.update_password, name="update-password"),
                  path('user-account/', views.user_account, name="user-account"),
                  path('add_testimonial/', views.add_testimonial, name='add_testimonial'),

                  # dashboard starts here
                  path('dashboard/', views.dashboard, name="dashboard"),
                  path('respond_to_request/<str:request_id>/<str:response>/', views.respond_to_request,
                       name='respond_to_request'),
                  path('respond_to_tenant_request/<str:request_id>/<str:response>/', views.respond_to_tenant_request,
                       name='respond_to_tenant_request'),
                  path('dashboard-sales/', views.dashboard_sales, name="dashboard-sales"),
                  path('property/payments/<str:property_id>/payments/', views.payments, name='payments'),
                  path('managers/', views.managers, name="managers"),
                  path('add-managers/', views.add_managers, name="add-managers"),
                  path('properties/', views.properties, name="properties"),
                  path('property-contact/<str:property_id>/', views.property_contact, name="property-contact"),
                  path('tenant-profile/<int:tenant_id>/', views.tenant_profile, name='tenant-profile'),
                  path('paypal-payment/', views.paypal_payment, name='paypal_payment'),
                  path('credit-card-payment/', views.credit_card_payment, name='credit_card_payment'),
                  path('add_tenant/', views.add_tenant, name="add-tenant"),
                  path('calendar/', views.calendar, name="calendar"),
                  path('getting-started/', views.getting_started, name="getting-started"),
                  path('manager/<str:manager_id>/', views.managers_profile, name='managers-profile'),
                  path('tenant-invoice/', views.invoice, name="invoice"),
                  path('download/', views.download, name='download'),
                  path('property details/<str:property_id>/', views.dashboard_property_detail,
                       name="dashboard-property-details"),
                  path('add-property/', views.add_property, name="add-property"),
                  path('send_message/<int:property_id>/', views.send_message, name='send_message'),
                  path('schedule_message/<int:property_id>/', views.schedule_message, name='schedule_message'),
                  path('mark_all_messages_as_read/', views.mark_all_messages_as_read, name='mark_all_messages_as_read'),

                  path('property/<int:property_id>/edit/', views.edit_property, name='edit_property'),
                  path('property/<int:property_id>/delete/', views.delete_property, name='delete_property'),

                  # mpesa payemnt
                  path('mpesa/payment/', views.mpesa_payment, name='mpesa_payment'),
                  path('mpesa/callback/', views.mpesa_callback, name='mpesa_callback'),
                  # path('mpesa/payment/status/', views.query_stk_push_status, name='mpesa_payment_status'),
                  path('token/', views.getAccessToken, name='token'),

                  path('api/property-data/', views.get_property_data, name='property_data'),

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
