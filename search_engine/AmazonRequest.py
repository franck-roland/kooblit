# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
import urllib
import re

from .aws_req import compute_json_one_result, sanitize, calculate_signature_amazon
from .file_manipulation import JsonManager, AmazonResultsCache

MAX_SEARCH_ON_A_PAGE = 2000
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

servers = ("ecs.amazonaws.fr", "ecs.amazonaws.com")

class AmazonRequest(object):
    """docstring for AmazonRequest"""
    def __init__(self, title, key, exact_match=0, delete_duplicate=True, escape=False, nb_results_max=0):
        super(AmazonRequest, self).__init__()
        self.title = sanitize(title, slugify=1)
        self.key = key
        self.exact_match = exact_match
        self.delete_duplicate = delete_duplicate
        self.escape = escape
        self.nb_results_max = nb_results_max


    def creer_uniques_resultats_jusque_i(self, index, json_manager, 
        urls=servers, first_page=1):
        """ Fonction appelée quand le ieme resulat de recherche n'est pas disponible """
        global template
        global head
        assert(index>0)
        url = "http://{0}/onca/xml?"
        result = []
        duplication = []
        for link_url in urls:
            max_pages = 0
            amazon_cache = AmazonResultsCache(self.title, link_url)
            for page_nb in xrange(1, 11):

                m = template.format(self.title, str(page_nb))
                m = m.split("\n")
                m.sort()
                m = '&'.join(m)
                
                s = amazon_cache.check_in_tmp(page_nb)
                if not s:
                    u = urllib.urlopen(''.join((url.format(link_url),
                                                m,
                                                "&Signature=",
                                                calculate_signature_amazon(self.key, head.format(link_url) + m))))
                    s = u.read()
                    amazon_cache.create_tmp(page_nb, s)
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


    def recherche_between_i_and_j(self, begin, end):
        assert(begin > 0)
        assert(end >= begin)
        
        json_manager = JsonManager(self.title, self.delete_duplicate)
        results = []
        for index in xrange(begin, end + 1):
            result = json_manager.check_json_file_exist(index)
            if result:
                results.append(result)
            else:
                break

        if not result:
            results = self.creer_uniques_resultats_jusque_i(end, json_manager)[begin-1:]
            print len(results)

        else:
            results = [json_manager.get_json_file(i) for i in range(begin,end+1)]

        results_final = []
        for res in results:
            if sanitize(res['title'], slugify=1) == self.title or not self.exact_match:
                if self.escape: # echaper les caracteres speciaux
                    res['title'] = sanitize(res['title'])
                results_final.append(res)
        return results_final


    def compute_args(self):
        if not self.nb_results_max:
            self.nb_results_max = MAX_SEARCH_ON_A_PAGE
        return self.recherche_between_i_and_j(1, self.nb_results_max)


