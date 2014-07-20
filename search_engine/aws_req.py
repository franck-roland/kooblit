# -*- coding: utf-8 -*-

from hashlib import sha256, sha1
import hmac
import base64
import urllib
import sys
import xml.etree.ElementTree as ET
import re
import json
import os
import re
from django.core.files import File

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
ItemPage={1}
ResponseGroup=ItemAttributes%2CImages%2CEditorialReview
Version=2009-01-06
Timestamp=2015-01-01T12%3A00%3A00Z
AssociateTag=kooblit-21"""
# callback=%3F
reserved = set([":", "/", "?", "#", "[", "]", "@", "!", "$", "&", "'", "(", ")", "*" , "+" , "," , ";" , "=", ' '])
can_be = set([' '])

def unsanitize(s, to_lower=0):
    s = s.split("%")
    tmp = [s[0]]
    for i in s[1:]:
        if i:
            if chr(int(i[:2],16)) in can_be:
                v = chr(int(i[:2],16))
            else:
                v = ''.join(('%',i[:2]))
            tmp.extend([v,i[2:]])
    s = ''.join(tmp)
    if to_lower:
        s = s.lower()
    return s

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


def create_dir_if_not_exists(path_name):
    if not os.path.isdir(path_name):
        if os.path.exists(path_name):
            os.remove(path_name)
        os.mkdir(path_name)

#Check if this request has been done the last 24h and read the corresponding page_nb
def check_in_tmp(title, page_nb, server_name):
    dir_name = sha1(title).hexdigest()
    dir_path = "/tmp/"+dir_name+"/"+server_name+"/"
    ret = ''
    if os.path.isdir(dir_path):
        nber = len([name for name in os.listdir(dir_path) if os.path.isfile(dir_path+name)])
        if page_nb <= nber and page_nb > 0:
            with open(dir_path + "f_" + str(page_nb) + '.xml', 'r') as f:
                _file = File(f)
                ret = _file.read()
    return ret

def create_tmp(title, page_nb, server_name, result):
    dir_name = sha1(title).hexdigest()
    dir_path = "/tmp/"+dir_name+"/"
    ret = ''
    create_dir_if_not_exists(dir_path)
    dir_path += server_name+"/"
    create_dir_if_not_exists(dir_path)
    file_name = dir_path+"f_"+str(page_nb)+'.xml'
    with open(file_name, 'w') as f:
        _file = File(f)
        ret = _file.write(result)

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

    return {'title': title, 'author': author, 'isbn': isbn, 'image': image, 'summary': summary, 'details': details}


@sanitizer
def compute_args(title,k, exact_match=0, delete_duplicate=1, escape=0):
    global template
    global head
    url = "http://{0}/onca/xml?"
    result = []
    # for i in xrange(1,11):
    for link_url in ("ecs.amazonaws.co.uk", "ecs.amazonaws.fr"):
        max_pages = 0
        for page_nb in xrange(1,11):
            m = template.format(title, str(page_nb))
            m = m.split("\n")
            m.sort()
            m = '&'.join(m)

            s = check_in_tmp(title, page_nb, link_url)
            if not s:
                u = urllib.urlopen(''.join((url.format(link_url), 
                    m, 
                    "&Signature=", 
                    calculate_signature_amazon(k, head.format(link_url)+m))))

                # deb = ''.join((url.format(link_url), 
                #     m, 
                #     "&Signature=", 
                #     calculate_signature_amazon(k, head.format(link_url)+m)))
                s = u.read()
                create_tmp(title, page_nb, link_url, s)
            s = re.sub(' xmlns="[^"]+"', '', s, count=1)
            root = ET.fromstring(s)
            if page_nb == 1:
                try:
                    max_pages = int(root.find('Items').find('TotalPages').text)
                
                except AttributeError:
                    break

                except Exception, e:
                    raise

            for t in root.iter('Item'):
                tmp = compute_json_one_result(t)
                if exact_match and sanitize(tmp['title']) == title or not exact_match:
                    # import pdb;pdb.set_trace()
                    if escape:
                        tmp['title'] = sanitize(tmp['title'])
                    if not (tmp['title'], tmp['author']) in ((i['title'], i['author']) for i in result) or not delete_duplicate:
                        result.append(tmp)

            if page_nb == max_pages:
                break

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
