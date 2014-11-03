# -*- coding: utf-8 -*-

from django.test import TestCase
from django.conf import settings
import urllib
import hashlib
import base64
from django.http import HttpResponseRedirect
from urllib import quote_plus
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

def openssl_sign(data, priv_key):
    # priv_key.sign_init()
    # priv_key.sign_update(data)
    return priv_key.sign(data)

def openssl_sign2(data, priv_key):
    # priv_key.sign_init()
    # priv_key.sign_update(data)
    return priv_key.sign(data)

# Create your tests here.
class PayplugTestCase(TestCase):
    def setUp(self):

        self.params = {
        "ipn_url": "http://1a24e0f2.ngrok.com/ipn",
        "return_url": "http://1a24e0f2.ngrok.com",
        "amount": "999",
        "currency": "EUR",
        "first_name": "alain"

        }
        filename = "config/payplug_rsa_private_key.pem"
        self.rsa_key = RSA.importKey(settings.PAYPLUG_PRIVATE_KEY)
        # self.base_url = settings.PAYPLUG_URL
        self.base_url = "https://www.payplug.fr/p/test/w4OV"

    def test_commande(self):
        url_params = urllib.urlencode(self.params)
        url_params = quote_plus(url_params, '=&')
        print url_params
        url_params = url_params.encode("utf­-8")
        data = base64.b64encode(url_params).decode('utf­-8')
        data = quote_plus(data, '=&')

        # url_params = urllib.urlencode(self.params)
        # url_params = quote_plus(url_params)
        # url_params = url_params.encode("utf­8")

        # data = base64.b64encode(url_params).decode('utf­-8')
        # data = quote_plus(data, "")

        rsa = PKCS1_v1_5.new(self.rsa_key)
        _hash = SHA.new()
        _hash.update(url_params)
        sign = base64.b64encode(rsa.sign(_hash))
        sign = quote_plus(sign.decode('utf­-8'), '=&')

        # signature = self.priv1.sign(hashlib.sha1(url_params).digest(),None)[0]
        url = "".join((self.base_url, "?data=", data, "&sign=", sign))
        print url
        # print hex(signature)[2:][:-1]
        # signature = urllib.quote_plus(hex(signature)[2:][:-1].encode('base64'))
        # print url
        # return HttpResponseRedirect(url)

