# -*- coding: utf-8 -*-

import urllib
import urllib2
from bs4 import BeautifulSoup
import pytz
import re

def getNumRand():
    url = "http://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/captcha?accion=random"
    numRand = urllib2.urlopen(url).read()
    return numRand

def getDataRUC(ruc):
    numRand = getNumRand()
    # print(numRand)
    rtn = []
    if ruc != "" and numRand is not False:
        data = {
            "nroRuc": ruc,
            "accion": "consPorRuc",
            "numRnd": numRand
        }
        # print(data)
        url = "http://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/jcrS00Alias"
        user_agent = 'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:53.0) Gecko/20100101 Firefox/53.0'
        headers = {
            'User-Agent': user_agent,
            'Content-Type': 'application/json;charset=UTF-8'
        }
        # This urlencodes your data (that's why we need to import urllib at the top)
        data = urllib.urlencode(data)
        # enviar HTTP POST request
        request = urllib2.Request(url, data, headers=headers)
        # print(request)
        # leer la pagina
        page = urllib2.urlopen(request).read()
        print(page)

        # RazonSocial
        # patron = '/<input type="hidden" name="desRuc" value="(.*)">/'
        # output = re.findall(patron, page)
        # print(output)

getDataRUC('20453679757')