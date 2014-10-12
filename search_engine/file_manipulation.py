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
    
    def check_json_file_exist(self, index):
        """ Check if a json file corresponding to the answer nber 'index' 
        of the search 'title' exists"""
        root_name = sha1(self.title).hexdigest()
        dir_path = "/tmp/" + root_name + self.dir_name
        ret = ''
        if os.path.isdir(dir_path):
            if int(time.time() - os.stat(dir_path).st_ctime) / 86400 > 7:
                shutil.rmtree(dir_path)
                return ''
            nber_files = len([name for name in os.listdir(dir_path) if os.path.isfile(dir_path + name)])
            if index <= nber_files and index > 0:
                with open(dir_path + "res_" + str(index) + '.json', 'r') as f:
                    ret = json.load(f)

        return ret

    def create_json_result(self, index, result):
        dir_name = sha1(self.title).hexdigest()
        dir_path = "/tmp/" + dir_name + "/"
        create_dir_if_not_exists(dir_path)
        dir_path += self.dir_name
        create_dir_if_not_exists(dir_path)
        file_name = dir_path + "res_" + str(index) + '.json'
        with open(file_name, 'w') as f:
            f.write(json.dumps(result))
        


def create_dir_if_not_exists(path_name):
    if not os.path.isdir(path_name):
        if os.path.exists(path_name):
            os.remove(path_name)
        os.mkdir(path_name)

class AmazonResultsCache(object):
    """Gestion des création de fichiers Contenant les resultats d'amazon dans le dossier tmp"""
    def __init__(self, title, page_nb, server_name):
        super(AmazonResultsCache, self).__init__()
        self.title = title
        self.page_nb = page_nb
        self.server_name = server_name
        

    def check_in_tmp(self):
        dir_name = sha1(self.title).hexdigest()
        dir_path = "/tmp/" + dir_name + "/" + self.server_name + "/"
        ret = ''
        if os.path.isdir(dir_path):
            if int(time.time() - os.stat(dir_path).st_ctime) / 86400 > 7:
                shutil.rmtree(dir_path)
                return ''
            nber = len([name for name in os.listdir(dir_path) if os.path.isfile(dir_path + name)])
            if self.page_nb <= nber and self.page_nb > 0:
                with open(dir_path + "f_" + str(self.page_nb) + '.xml', 'r') as f:
                    ret = f.read()
                    root = ET.fromstring(ret)
                    # Check if there was an error in the buffered page
                    try:
                        root.find("{http://ecs.amazonaws.com/doc/2009-01-06/}Error").text
                        ret = ""
                    except AttributeError:
                        pass
        return ret


    def create_tmp(self, result):
        dir_name = sha1(self.title).hexdigest()
        dir_path = "/tmp/" + dir_name + "/"
        create_dir_if_not_exists(dir_path)
        dir_path += self.server_name + "/"
        create_dir_if_not_exists(dir_path)
        file_name = dir_path + "f_" + str(self.page_nb) + '.xml'
        with open(file_name, 'w') as f:
            f.write(result)
