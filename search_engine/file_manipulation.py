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

class JsonManager(object):
    """docstring for JsonManager"""
    def __init__(self, title, delete_duplicate=False):
        super(JsonManager, self).__init__()
        self.title = title
        self.delete_duplicate = delete_duplicate
        if not self.delete_duplicate:
            self.dir_name = "/results_json/"
        else:
            self.dir_name = "/unique_results_json/"
        root_name = sha1(self.title).hexdigest()
        create_dir_if_not_exists("/tmp/" + root_name)
        self.dir_path = "/tmp/" + root_name + self.dir_name
        create_dir_if_not_exists(self.dir_path)
        self.offset = 0

    def set_offset(self, offset):
        self.offset = offset

    def get_filename(self, index, is_offseted=False):
        if is_offseted:
            index += self.offset
        return "".join(("res_", str(index), '.json'))

    def get_json_file(self, index, is_offseted=False):
        """ Check if a json file corresponding to the answer nber 'index' 
        of the search 'title' exists"""
        ret = {}
        if self.check_json_file_exist(index):
            with open(self.dir_path + self.get_filename(index, is_offseted), 'r') as f:
                    ret = json.load(f)
        return ret
        
    def check_json_file_exist(self, index, is_offseted=False):
        if index <= 0:
            return False

        if os.path.isdir(self.dir_path):
            if int(time.time() - os.stat(self.dir_path).st_ctime) / 86400 > 7:
                shutil.rmtree(self.dir_path)
                return False
            nber_files = len([name for name in os.listdir(self.dir_path) if os.path.isfile(self.dir_path + name)])
            if index <= nber_files:
                return os.path.isfile(self.dir_path + self.get_filename(index, is_offseted))
            else:
                return False


    def create_json_result(self, index, result, is_offseted=False):
        create_dir_if_not_exists(self.dir_path)
        file_name = self.dir_path + self.get_filename(index, is_offseted)
        with open(file_name, 'w') as f:
            f.write(json.dumps(result))
        


def create_dir_if_not_exists(path_name):
    if not os.path.isdir(path_name):
        if os.path.exists(path_name):
            os.remove(path_name)
        os.mkdir(path_name)


class AmazonResultsCache(object):
    """Gestion des création de fichiers Contenant les resultats d'amazon dans le dossier tmp"""
    def __init__(self, title, server_name):
        super(AmazonResultsCache, self).__init__()
        self.title = title
        self.server_name = server_name
        dir_name = sha1(self.title).hexdigest()
        create_dir_if_not_exists("/tmp/" + dir_name)
        self.dir_path = "/tmp/" + dir_name + "/" + self.server_name + "/"


    def get_last_page_recorded(self):
        if os.path.isdir(self.dir_path):
            if int(time.time() - os.stat(self.dir_path).st_ctime) / 86400 > 7:
                shutil.rmtree(self.dir_path)
                return 0
            else:
                return len([name for name in os.listdir(self.dir_path) if os.path.isfile(self.dir_path + name)])
        return 0


    def check_in_tmp(self, page_nb):
        ret = ''
        if os.path.isdir(self.dir_path):
            if int(time.time() - os.stat(self.dir_path).st_ctime) / 86400 > 7:
                shutil.rmtree(self.dir_path)
                return ''
            nber = len([name for name in os.listdir(self.dir_path) if os.path.isfile(self.dir_path + name)])
            if page_nb <= nber and page_nb > 0:
                if os.path.isfile(self.dir_path + "f_" + str(page_nb) + '.xml'):
                    with open(self.dir_path + "f_" + str(page_nb) + '.xml', 'r') as f:
                        ret = f.read()
                        root = ET.fromstring(ret)
                        # Check if there was an error in the buffered page
                        try:
                            root.find("{http://ecs.amazonaws.com/doc/2009-01-06/}Error").text
                            ret = ""
                        except AttributeError:
                            pass
        return ret


    def create_tmp(self, page_nb, result):
        create_dir_if_not_exists(self.dir_path)
        file_name = self.dir_path + "f_" + str(page_nb) + '.xml'
        with open(file_name, 'w') as f:
            f.write(result)
