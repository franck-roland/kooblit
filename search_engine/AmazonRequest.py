# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
import urllib
import re
from json import JSONEncoder

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
BOOK_FORMATS = (u'Broché', 'Hardcover', 'Poche')

class ResponseEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__

class Response(object):
    """docstring for Response"""
    def __init__(self, results, server_index, last_page):
        super(Response, self).__init__()
        self.results = results
        self.last_page = last_page
        self.server_index = server_index
    
    def __len__(self):
        return len(self.results)

    def __iter__(self):
        for attr in self.results:
            yield attr


class AmazonRequest(object):
    """docstring for AmazonRequest"""
    def __init__(self, title, key, book_title="", exact_match=0, delete_duplicate=True, escape=False, nb_results_max=0):
        super(AmazonRequest, self).__init__()
        self.title = sanitize(title)
        self.key = key
        self.exact_match = exact_match
        self.delete_duplicate = delete_duplicate
        self.escape = escape
        self.nb_results_max = nb_results_max
        self.book_title = sanitize(book_title)


    def creer_uniques_resultats_jusque_i(self, index, json_manager, response,
        server_index=0, first_page=1, duplication=None, is_offseted=False):
        """ Fonction appelée quand le ieme resulat de recherche n'est pas disponible """
        global template
        global head
        assert(index > 0)
        assert(server_index < len(servers))
        assert(first_page > 0 and first_page <= 10)

        url = "http://{0}/onca/xml?"
        result = []
        print first_page, server_index
        if duplication == None:
            duplication = []
        for s_index in xrange(server_index,len(servers)):
            link_url = servers[s_index]
            max_pages = 0
            amazon_cache = AmazonResultsCache(self.title, link_url)
            for page_nb in xrange(first_page, 11):
                response.last_page = page_nb
                response.server_index = s_index
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
                        if tmp['book_format'] in BOOK_FORMATS:
                            if tmp['language'] in (u'Français', 'Anglais', 'English', 'French', u''):
                                result.append(tmp)
                                duplication.append((tmp['title'], tmp['author']))
                                if not json_manager.check_json_file_exist(len(result), is_offseted=is_offseted):
                                    json_manager.create_json_result(len(result), tmp, is_offseted=is_offseted)

                    if len(result) >= index:
                        return result

                if page_nb == max_pages:
                    break

        return result


    def recherche_between_i_and_j(self, begin, end, server_index=0, page_nb=1):
        assert(begin > 0)
        assert(end >= begin)
        assert(page_nb > 0 and page_nb <= 10)
        assert(server_index < len(servers))
        response = Response([],server_index, page_nb)

        json_manager = JsonManager(self.title, self.delete_duplicate)
        allready_displayed = [] # All the results allready displayed (from 1 to begin-1)
        for index in xrange(1, begin):
            result = json_manager.get_json_file(index)
            if result:
                allready_displayed.append(result)
                json_manager.set_offset(index)
            else:
                break

        # Check if we have at least allready found begin - 1 results
        if len(allready_displayed) < begin - 1:
            results = self.creer_uniques_resultats_jusque_i(end, json_manager, response)[begin-1:]
        else:
            # Remove all the results allready found
            duplication = [(tmp['title'], tmp['author']) for tmp in allready_displayed]
            results = []

            # Find which results have been allready found
            for index in xrange(begin, end + 1):
                result = json_manager.get_json_file(index)
                if result:
                    results.append(result)
                    json_manager.set_offset(index)
                else:
                    break

            # if we didn't have done all the searches
            if len(results) < end - begin:
                # Remove all the results allready found
                duplication.extend([(tmp['title'], tmp['author']) for tmp in results])
                results_tmp = self.creer_uniques_resultats_jusque_i(end - begin + 1 - len(results),
                                                                    json_manager, response, server_index=server_index,
                                                                    first_page=page_nb, duplication=duplication, is_offseted=True)
                results.extend(results_tmp)

        results_final = []
        if self.book_title:
            title_to_compare = sanitize(self.book_title)
        else:
            title_to_compare = self.title
        for res in results:
            if sanitize(res['title']) == title_to_compare or not self.exact_match:
                if self.escape : # echaper les caracteres speciaux
                    res['title'] = sanitize(res['title'])
                results_final.append(res)
        response.results = results_final
        print response.last_page, response.server_index
        return response


    def compute_args(self, server_index=0, page_nb=1):
        assert(page_nb <= 10)
        assert(server_index < len(servers))
        if not self.nb_results_max:
            self.nb_results_max = MAX_SEARCH_ON_A_PAGE
        return self.recherche_between_i_and_j(1, self.nb_results_max, server_index=server_index, page_nb=page_nb)


