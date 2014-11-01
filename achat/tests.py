# -*- coding: utf-8 -*-

from django.test import TestCase
from django.conf import settings
import urllib
import hashlib
import base64
from django.http import HttpResponseRedirect
from Crypto.PublicKey import RSA
import OpenSSL.crypto as ct 
from M2Crypto import RSA as m2rsa

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
        self.ngrok = "http://1a24e0f2.ngrok.com"
        self.amout = 2
        self.currency = "EUR"
        self.params = {
        "ipn_url": "http://1a24e0f2.ngrok.com",
        "amout": 9,
        "currency": "EUR",

        }
        filename = "config/payplug_rsa_private_key.pem"
        print settings.PAYPLUG_PRIVATE_KEY
        self.priv1 = RSA.importKey(settings.PAYPLUG_PRIVATE_KEY)
        self.priv2 = ct.load_privatekey(ct.FILETYPE_PEM, open(filename,"r").read())
        print ct.PKey.check(self.priv2)
        self.priv3 = m2rsa.load_key(filename)
        self.base_url = settings.PAYPLUG_URL

    def test_commande(self):
        url_params = urllib.urlencode(self.params, True)
        print url_params
        data = urllib.quote_plus(base64.standard_b64encode(url_params))
        # signature = self.priv1.sign(hashlib.sha1(url_params).digest(),None)[0]
        signature = urllib.quote_plus(base64.standard_b64encode(openssl_sign(url_params, self.priv3)))
        url = "".join((self.base_url, "?data=", data, "&signature=", signature))
        print url
        signture = urllib.quote_plus(base64.standard_b64encode(ct.sign(self.priv2,url_params,'sha1')))
        url = "".join((self.base_url, "?data=", data, "&signature=", signature))
        print url
        # print hex(signature)[2:][:-1]
        # signature = urllib.quote_plus(hex(signature)[2:][:-1].encode('base64'))
        # print url
        # return HttpResponseRedirect(url)

