# -*- coding: utf-8 -*-
import json
import urllib
import urllib2

import requests
from bs4 import BeautifulSoup
import pytz
import re
from urlparse import urljoin
import pycurl
import StringIO

class SUNATRuc(object):

    # def __init__(self):
        # self.session = requests.session()
        # self.referer = self.session.post("http://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/frameCriterioBusqueda.jsp")


    def getNumRand(self):
        url = "http://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/captcha?accion=random"
        numRand = self.CurlPOST(url)
        # numRand = urllib2.urlopen(url).read()
        # print(self.referer.cookies)
        # numRand = requests.post(url, cookies=self.referer.cookies)
        return numRand

    def getDataRUC(self, ruc):
        numRand = self.getNumRand()
        # print(numRand)

        rtn = []
        if ruc != "" and numRand is not False:
            values = {
                "accion": "consPorRuc",
                "nroRuc": ruc,
                "numRnd": numRand
            }
            # print(values)

            url = "http://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/jcrS00Alias"
            data = urllib.urlencode(values)
            user_agent = 'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:53.0) Gecko/20100101 Firefox/53.0'
            headers = {
                'User-Agent': user_agent,
                'Content-Type': 'application/json;charset=UTF-8'
                       }
            # enviar HTTP POST request
            # print(self.referer.content)
            page = self.CurlPOST(url, data, '')
            print(page)

    def CurlPOST(self, url, data=False, cookie=False):

        c = pycurl.Curl()
        b = StringIO.StringIO()
        c.setopt(pycurl.URL, url)

        c.setopt(pycurl.HTTPHEADER, ['Content-Type: application/json'])
        # c.setopt(pycurl.TIMEOUT, 10)
        c.setopt(pycurl.WRITEFUNCTION, b.write)
        if cookie:
            c.setopt(pycurl.COOKIEJAR, cookie)
            c.setopt(pycurl.COOKIEFILE, cookie)
        if data:
            c.setopt(pycurl.POST, 1)
            c.setopt(pycurl.POSTFIELDS, data)

        c.perform()
        html = b.getvalue()
        b.close()
        c.close()
        return html

sunat = SUNATRuc()
sunat.getDataRUC('20453679757')