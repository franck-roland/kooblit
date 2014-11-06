# -*- coding: utf-8 -*-

from hashlib import sha256, sha1
import hmac
import base64
import urllib
import sys
import xml.etree.ElementTree as ET
import re
import os
import time
import shutil
import json

from django.core.files import File
from manage_books_synth.models import Theme

from kooblit_lib.utils import book_slug

from .file_manipulation import *

head = """GET
{0}
/onca/xml
"""
"""Sort=relevance"""

template = u"""Service=AWSECommerceService
AWSAccessKeyId=AKIAJC6ZI2BWV4H7XTMQ
Operation=ItemSearch
SearchIndex=Books
Title={0}
ItemPage={1}
ResponseGroup=ItemAttributes%2CImages%2CEditorialReview%2CSimilarities%2CBrowseNodes
Version=2009-01-06
Timestamp=2015-01-01T12%3A00%3A00Z
AssociateTag=kooblit-21"""
# callback=%3F
reserved = set([":", "/", "?", "#", "[", "]", "@", "!", "$", "&", "'", "(", ")", "*", "+", ",", ";", "=", ' '])
can_be = set([' '])

MAX_SEARCH_ON_A_PAGE = 2000
BOOK_FORMATS = (u'Broché', 'Hardcover', 'Poche')
def unsanitize(s, to_lower=0):
    s = s.split("%")
    tmp = [s[0]]
    for i in s[1:]:
        if i:
            if chr(int(i[:2], 16)) in can_be:
                v = chr(int(i[:2], 16))
            else:
                v = ''.join(('%', i[:2]))
            tmp.extend([v, i[2:]])
    s = ''.join(tmp)
    if to_lower:
        s = s.lower()
    return s


def sanitize(s, to_lower=0, slugify=0):
    s = s.replace("'","321645e321ezf")
    if slugify:
        s = book_slug(s)
    s = s.replace("321645e321ezf","'")

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
    def do(title, *args, **kwargs):
        return func(sanitize(title, slugify=1), *args, **kwargs)
    return do


def backward(m):
    prog = re.compile("(%([0-9a-fA-F]{2}))")
    l = prog.findall(m)
    for i in l:
        m = m.replace(i[0], chr(int(i[1], 16)))
    return m


def calculate_signature_amazon(k, m):
    h = hmac.new(k, m, sha256)
    d = h.digest()
    b = sanitize(base64.standard_b64encode(d))
    return b


def get_text(obj, name):
    try:
        ret = obj.find(name).text
    except AttributeError:
        ret = ""
    return ret


def compute_theme(current_node, childs_theme=None):
    """ Fonction permettant de peupler les thèmes de la base de données des livres
        browseNodesRoot = root d'un browseNodes
        childs_theme = thèmes qui se sont accumulés avec le parcours des browseNodes
        retour: le premier sous thème si on aboutit a un node Thème, rien sinon"""

    # selectionner BrowseNode (current_node)
    if current_node is None:
        return
    is_root = current_node.find('IsCategoryRoot')
    theme = get_text(current_node, 'Name')
    amazon_id = long(get_text(current_node, 'BrowseNodeId'))
    if is_root is not None:
        if theme != u'Thèmes' or not childs_theme:
            return
        else:

            try:
                father_theme = Theme.objects.get(theme=theme)
            except Theme.DoesNotExist:
                father_theme = Theme(theme=theme, amazon_id=amazon_id)
                father_theme.save()
            for child in childs_theme:
                try:
                    child_theme = Theme.objects.get(theme=child['theme'])
                except Theme.DoesNotExist:
                    child_theme = Theme(**child)
                    child_theme.save()
                if child_theme not in father_theme.sub_theme:
                    father_theme.sub_theme.append(child_theme)
                    father_theme.save()
                father_theme = child_theme
            return theme
    else:
        if childs_theme is None:
            childs_theme = []
        childs_theme.insert(0, {'theme': theme, 'amazon_id': amazon_id})
        ancestors = current_node.find('Ancestors')
        if ancestors is None:
            return
        else:
            next_node = ancestors.find('BrowseNode')
            if compute_theme(next_node, childs_theme):
                return theme
            else:
                return


def compute_json_one_result(result):

    DetailPageURL = result.find('DetailPageURL').text
    details = result.find("DetailPageURL").text

    browseNodes = result.find('BrowseNodes')
    if browseNodes is not None:
        for node in browseNodes.iter('BrowseNode'):
            theme = compute_theme(node)
            if theme:
                break
    else:
        theme = ''

    obj = result.find('ItemAttributes')
    editeur = get_text(obj, 'Publisher')

    title = get_text(obj, 'Title')
    author = get_text(obj, 'Author')
    isbn = get_text(obj, 'ISBN')
    book_format = get_text(obj, 'Binding')
    try:
        languages = obj.find('Languages').find('Language')
        language = get_text(languages, 'Name')
    except AttributeError:
        language = ""

    obj = result.find("LargeImage")
    image = get_text(obj, "URL")
    obj = result.find("MediumImage")
    medium_image = get_text(obj, "URL")

    try:
        obj = result.find('EditorialReviews').find('EditorialReview')
        # summary = BeautifulSoup(get_text(obj, 'Content')).get_text()
        summary = get_text(obj, 'Content')
    except AttributeError:
        summary = ""

    title = title.lower()

    return {'title': title, 'author': author, 'isbn': isbn, 'image': image, 'medium_image': medium_image,
            'summary': summary, 'details': details, 'DetailPageURL': DetailPageURL, 'book_format': book_format,
            'language': language, 'theme': theme, 'editeur': editeur}



def main(f):
    m = open(f, "rb").read()[:-1]
    m = m.split("\n")
    m.sort()
    m = '&'.join(m)
    k = os.environ["AMAZON_KEY"]
    u = urllib.urlopen("http://ecs.amazonaws.co.uk/onca/xml?" + m + "&Signature=" + calculate_signature_amazon(k, head + m))
    s = u.read()
    s = re.sub(' xmlns="[^"]+"', '', s, count=1)
    root = ET.fromstring(s)
    result = ['resultat']
    for t in root.iter('Item'):
        result.append(compute_json_one_result(t))
    print "resultat = " + str(result)


if __name__ == "__main__":
    f = sys.argv[1]
    main(f)
