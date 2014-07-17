# -*- coding: utf-8 -*-

from hashlib import sha256
import hmac
import base64
import urllib
import sys
import xml.etree.ElementTree as ET
import re
import json
import os
import re

# from mongoengine import *
# connect('docs_db')

# head = """GET
# ecs.amazonaws.co.uk
# /onca/xml
# """
# head = """GET
# ecs.amazonaws.fr
# /onca/xml
# """
head = """GET
{0}
/onca/xml
"""

template = u"""Service=AWSECommerceService
AWSAccessKeyId=AKIAJC6ZI2BWV4H7XTMQ
Operation=ItemSearch
SearchIndex=Books
Sort=salesrank
Title={0}
Page={1}
ResponseGroup=ItemAttributes%2CImages%2CEditorialReview
Version=2009-01-06
Timestamp=2015-01-01T12%3A00%3A00Z
AssociateTag=kooblit-21"""
# callback=%3F
reserved = set([":", "/", "?", "#", "[", "]", "@", "!", "$", "&", "'", "(", ")", "*" , "+" , "," , ";" , "=", ' '])

def sanitize(s, to_lower=0):
    l = []
    if to_lower:
        s = s.lower()
    for i in s:
        if i not in reserved:
            l.append(i)
        else:
            l.append("%")
            l.append(hex(ord(i)).upper()[2:])
    return ''.join(l)

def sanitizer(func):
    def do(title,*args,**kwargs):
        return func(sanitize(title),*args,**kwargs)
    return do


def backward(m):
    prog = re.compile("(%([0-9a-fA-F]{2}))")
    l =  prog.findall(m)
    for i in l:
        m = m.replace(i[0],chr(int(i[1],16)))
    return m



def calculate_signature_amazon(k, m):
    h = hmac.new(k, m, sha256)
    d = h.digest()
    b = sanitize(base64.standard_b64encode(d))
    return b

def get_text(obj, name):
    try:
        ret = obj.find(name).text
    except AttributeError, e:
        ret = ""
    return ret

def compute_json_one_result(result):

    obj = result.find('ItemAttributes')

    title = get_text(obj, 'Title')
    author = get_text(obj, 'Author')
    isbn = get_text(obj, 'ISBN')

    obj = result.find("LargeImage")

    image = get_text(obj, "URL")
    details = result.find("DetailPageURL").text
    
    try:
        obj = result.find('EditorialReviews').find('EditorialReview')
        summary = get_text(obj, 'Content')
    except AttributeError, e:
        summary = ""

    title = title.lower()
    return [title, author, isbn, image, summary, details]


@sanitizer
def compute_args(title,k, exact_match=0, delete_duplicate=1, escape=0):
    global template
    global head
    url = "http://{0}/onca/xml?"
    result = []
    # for i in xrange(1,11):
    for i in xrange(1,2):
        m = template.format(title, str(i))
        m = m.split("\n")
        m.sort()
        m = '&'.join(m)
    #    k = open("AMAZON_KEY.conf").read()[:-1]
        link_url = "http://ecs.amazonaws.co.uk/onca/xml?"
        link_url = "http://ecs.amazonaws.fr/onca/xml?"
        for link_url in ("ecs.amazonaws.co.uk", "ecs.amazonaws.fr"):
            u = urllib.urlopen(''.join((url.format(link_url), 
                m, 
                "&Signature=", 
                calculate_signature_amazon(k, head.format(link_url)+m))))

            deb = ''.join((url.format(link_url), 
                m, 
                "&Signature=", 
                calculate_signature_amazon(k, head.format(link_url)+m)))
            # import pdb;pdb.set_trace()
            s = u.read()
            s = re.sub(' xmlns="[^"]+"', '', s, count=1)
            root = ET.fromstring(s)
            for t in root.iter('Item'):
                tmp = compute_json_one_result(t)
                if exact_match and sanitize(tmp[0]) == title or not exact_match:
                    # import pdb;pdb.set_trace()
                    if escape:
                        tmp[0] = sanitize(tmp[0])
                    if not tmp[:2] in [i[:2] for i in result] or not delete_duplicate:
                        result.append(tmp)
    return result

def create_book(title, k):
    s = compute_args(title, k, exact_match=1, delete_duplicate=0)
    # import pdb;pdb.set_trace()

@sanitizer
def compute_args2(title, k):
    global template
    global head
    m = template.format(title)
    m = m.split("\n")
    m.sort()
    m = '&'.join(m)
#    k = open("AMAZON_KEY.conf").read()[:-1]
    link_url = "http://webservices.amazon.co.uk/onca/xml?"
    link_url = "http://ecs.amazonaws.fr/onca/xml?"
    l = ''.join([link_url, m, "&Signature=", calculate_signature_amazon(k, head+m)])
    l = l.split('?')
    l[1] = l[1].split("&")
    # import pdb;pdb.set_trace()
    for i,v in enumerate(l[1]):
        l[1][i] = v.split("=")
        l[1][i][1] = backward(l[1][i][1])
    return l

def main(f):
    m = open(f,"rb").read()[:-1]
    m = m.split("\n")
    m.sort()
    m = '&'.join(m)
    k = os.environ["AMAZON_KEY"]
    u = urllib.urlopen("http://ecs.amazonaws.co.uk/onca/xml?"+m+"&Signature="+calculate_signature_amazon(k, head+m))
    s = u.read()
    s = re.sub(' xmlns="[^"]+"', '', s, count=1)
    root = ET.fromstring(s)
    result = ['resultat']
    for t in root.iter('Item'):
        result.append(compute_json_one_result(t))
    print "resultat = "+str(result)





if __name__ == "__main__":
    f = sys.argv[1]
    main(f)
