from django import template

from User.models import MPesaPayment, CreditCardPayment, PaypalPayment

register = template.Library()


@register.filter
def get_payment_mode(payment):
    if isinstance(payment, MPesaPayment):
        return "M-pesa"
    elif isinstance(payment, CreditCardPayment):
        return "Credit-card"
    elif isinstance(payment, PaypalPayment):
        return "Pay-pal"
    else:
        return "Unknown"
