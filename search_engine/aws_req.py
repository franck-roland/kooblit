from hashlib import sha256
import hmac
import base64
import urllib
import sys
import xml.etree.ElementTree as ET
import re
import json
import os

head = """GET
ecs.amazonaws.co.uk
/onca/xml
"""

template = """Service=AWSECommerceService
AWSAccessKeyId=AKIAJC6ZI2BWV4H7XTMQ
Operation=ItemSearch
SearchIndex=Books
Sort=salesrank
Title={0}
ResponseGroup=ItemAttributes%2CImages
Version=2009-01-06
Timestamp=2015-01-01T12%3A00%3A00Z
AssociateTag=kooblit-21"""

def sanitizer(func):
    def do(title,*args):
        l = []
        for i in title:
            if i.isalnum():
                l.append(i)
            else:
                l.append("%")
                l.append(hex(ord(i)).upper()[2:])
        return func(''.join(l),*args)
    return do

def calculate_signature_amazon(k, m):
    h = hmac.new(k, m, sha256)
    d = h.digest()
    b = base64.standard_b64encode(d)
    l = []
    for i in b:
        if i.isalnum():
            l.append(i)
        else:
            l.append("%")
            l.append(hex(ord(i)).upper()[2:])
    return ''.join(l)

def compute_json_one_result(result):
    t = result.find('ItemAttributes').find('Title').text
    r = result.find("LargeImage").find("URL").text
    return [t,r]

@sanitizer
def compute_args(title,k):
    global template
    global head
    m = template.format(title)
    m = m.split("\n")
    m.sort()
    m = '&'.join(m)
#    k = open("AMAZON_KEY.conf").read()[:-1]
    u = urllib.urlopen("http://ecs.amazonaws.co.uk/onca/xml?"+m+"&Signature="+calculate_signature_amazon(k, head+m))
    deb = "http://ecs.amazonaws.co.uk/onca/xml?"+m+"&Signature="+calculate_signature_amazon(k, head+m)
    s = u.read()
    s = re.sub(' xmlns="[^"]+"', '', s, count=1)
    root = ET.fromstring(s)
    result = []
    for t in root.iter('Item'):
        result.append(compute_json_one_result(t))
    return result


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
