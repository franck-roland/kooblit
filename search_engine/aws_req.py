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


def creer_uniques_resultats_jusque_i(title, key, index, json_manager):
    """ Fonction appelée quand le ieme resulat de recherche n'est pas disponible """
    global template
    global head
    assert(index>0)
    url = "http://{0}/onca/xml?"
    result = []
    duplication = []
    for link_url in ("ecs.amazonaws.fr", "ecs.amazonaws.com"):
        max_pages = 0
        for page_nb in xrange(1, 11):
            m = template.format(title, str(page_nb))
            m = m.split("\n")
            m.sort()
            m = '&'.join(m)
            s = check_in_tmp(title, page_nb, link_url)
            if not s:
                u = urllib.urlopen(''.join((url.format(link_url),
                                            m,
                                            "&Signature=",
                                            calculate_signature_amazon(key, head.format(link_url) + m))))
                s = u.read()
                create_tmp(title, page_nb, link_url, s)
            s = re.sub(' xmlns="[^"]+"', '', s, count=1)
            root = ET.fromstring(s)
            if page_nb == 1:
                try:
                    max_pages = int(root.find('Items').find('TotalPages').text)

                except AttributeError:
                    break

            for t in root.iter('Item'):
                tmp = compute_json_one_result(t)
                # Ajouter si l'élément titre+auteur n'est pas deja dans les resultats
                if not (tmp['title'], tmp['author']) in duplication or not json_manager.delete_duplicate:
                    if tmp['book_format'] in (u'Broché', 'Hardcover'):
                        if tmp['language'] in (u'Français', 'Anglais', 'English', 'French'):
                            result.append(tmp)
                            duplication.append((tmp['title'], tmp['author']))
                            if not json_manager.check_json_file_exist(len(result)):
                                json_manager.create_json_result(len(result), tmp)

                if len(result) >= index:
                    return result

            if page_nb == max_pages:
                break

    return result

def recherche_between_i_and_j(title, key, begin, end, exact_match=0, delete_duplicate=True, escape=False):
    assert(begin > 0)
    assert(end >= begin)
    
    json_manager = JsonManager(title, delete_duplicate)

    result = json_manager.check_json_file_exist(end)
    if not result:
        if end >= MAX_SEARCH_ON_A_PAGE:
            if not json_manager.check_json_file_exist(begin + 12):
                results = creer_uniques_resultats_jusque_i(title, key, begin + 12, json_manager)
            else:
                results = [json_manager.check_json_file_exist(i) for i in range(begin,begin + 13)]
        else:
            results = creer_uniques_resultats_jusque_i(title, key, end, json_manager)

    else:
        results = [json_manager.check_json_file_exist(i) for i in range(begin,end+1)]

    results_final = []
    for res in results:
        if sanitize(res['title'], slugify=1) == title or not exact_match:
            if escape: # echaper les caracteres speciaux
                res['title'] = sanitize(res['title'])
            results_final.append(res)
    return results_final

@sanitizer
def compute_args(title, key, exact_match=0, delete_duplicate=True, escape=False, nb_results_max=0):
    if not nb_results_max:
        nb_results_max = MAX_SEARCH_ON_A_PAGE
    return recherche_between_i_and_j(title, key, 1, nb_results_max, exact_match=exact_match, delete_duplicate=delete_duplicate, escape=escape)



def create_book(title, k):
    compute_args(title, k, exact_match=1, delete_duplicate=0)
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
    l = ''.join([link_url, m, "&Signature=", calculate_signature_amazon(k, head + m)])
    l = l.split('?')
    l[1] = l[1].split("&")
    # import pdb;pdb.set_trace()
    for i, v in enumerate(l[1]):
        l[1][i] = v.split("=")
        l[1][i][1] = backward(l[1][i][1])
    return l


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
