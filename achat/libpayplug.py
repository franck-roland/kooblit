
class PayplugTestCase(TestCase):
    def setUp(self):

        self.params = {
        "ipn_url": "http://dev.kooblit.com/ipn",
        "return_url": "http://70b673d6.ngrok.com",
        "amount": "999",
        "currency": "EUR",
        "first_name": "alain",
        "last_name": "bernard",
        "email": "alain.bernard@prout.com"

        }
        self.rsa_key = RSA.importKey(settings.PAYPLUG_PRIVATE_KEY)
        # self.base_url = settings.PAYPLUG_URL
        self.base_url = "https://www.payplug.fr/p/test/w4OV"

import json
import base64
import urllib
import hashlib
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
from urllib import quote_plus
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5



"""
Name        Type    Description
amount *    Integer Transaction amount, in cents (such as 4207 for 42,07€). We advise you to verify that the amount is between the minimum and maximum amounts allowed for your account.
currency *  String  Transaction currency. Only EUR is allowed at the moment.
ipn_url *   String  URL pointing to the ipn.php page, to which PayPlug will send payment and refund notifications. This URL must be accessible from anywhere on the Internet (usually not the case in localhost environments).
return_url  String  URL pointing to your payment confirmation page, to which PayPlug will redirect your customer after the payment.
cancel_url  String  URL pointing to your payment cancelation page, to which PayPlug will redirect your customer if he cancels the payment.
email       String  The customer’s email address.
first_name  String  The customer’s first name.
last_name   String  The customer’s last name.
customer    String  The customer ID in your database.
order       String  The order ID in your database.
custom_data String  Additional data that you want to receive in the IPN.
origin      String  Information about your website version (e.g., ‘My Website 1.2’) for monitoring and troubleshooting.
"""
def redirect_payplug(params):
    rsa_key = RSA.importKey(settings.PAYPLUG_PRIVATE_KEY)
    url_params = urllib.urlencode(params)
    url_params = url_params.encode("utf­-8")
    data = base64.b64encode(url_params).decode('utf­-8')
    data = quote_plus(data, '=&')

    rsa = PKCS1_v1_5.new(rsa_key)
    _hash = SHA.new()
    _hash.update(url_params)
    sign = base64.b64encode(rsa.sign(_hash))
    sign = quote_plus(sign.decode('utf­-8'), '=&')

    url = "".join((settings.PAYPLUG_URL, "?data=", data, "&sign=", sign))
    return HttpResponseRedirect(url)

@csrf_exempt
def ipn(request, *args, **kwargs):
    if request.method == 'POST':
        body = request.META.get('wsgi.input').read()
        data = json.loads(body.decode('utf-8'))
        signature = request.META.get('HTTP_PAYPLUG_SIGNATURE')
        signature = base64.b64decode(signature)
        k = settings.PAYPLUG_PUBLIC_KEY
        rsa_key = RSA.importKey(k)
        rsa = PKCS1_v1_5.new(rsa_key)
        hash = SHA.new()
        hash.update(body)
        if rsa.verify(hash, signature):
            message = "IPN received for {first_name} {last_name} for an amount of {amount} EUR"
            message = message.format(first_name=data["first_name"],
            last_name=data["last_name"], amount=data["amount"])
            send_mail("IPN Received", message, settings.DEFAULT_FROM_EMAIL,["franck.l.roland@gmail.com"])
        else:
            message = "The signature was invalid."
            send_mail("IPN Failed", message, settings.DEFAULT_FROM_EMAIL,
            ["franck.l.roland@gmail.com"])
    return HttpResponse()


