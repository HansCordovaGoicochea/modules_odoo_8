# -*- coding: utf-8 -*-

from __future__ import print_function
import base64
import logging
from zipfile import ZipFile

import requests
import suds
import suds.client
from suds.wsse import *
import urlparse, urllib, os
import time



def addSecurityHeader(client, username, password):
    security = Security()
    userNameToken = UsernameToken(username, password)
    timeStampToken = Timestamp(validity=600)
    security.tokens.append(userNameToken)
    security.tokens.append(timeStampToken)
    client.set_options(wsse=security)


class getStatusSunat(object):

    def getStatus(self, ticket, zip):
        logging.basicConfig(level=logging.DEBUG)
        # logging.getLogger('suds.client').setLevel(logging.DEBUG)

        username = '20495932797ADMINSC2'
        password = 'CARNAVAL'
        session = requests.session()
        session.auth = (username, password)

        # url = 'http://192.168.1.2:81/sunatWC/sunattest.xml'
        url = "https://e-beta.sunat.gob.pe/ol-ti-itcpfegem-beta/billService?wsdl"
        headers = {'Host': 'www.sunat.gob.pe:443', 'SOAPAction': "urn:sendSummary"}
        cliente = suds.client.Client(url, headers=headers, cache=None)
        addSecurityHeader(cliente, username, password)

        try:
            print (str(ticket))
            get_file_decode = cliente.service.getStatus(str(ticket))
            print(get_file_decode)
            path2 = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'archivos/recepcionado'))
            path2 = path2.replace('\\', '/')
            path2 = r"" + path2
            f = open(r'' + path2 + '/' + 'R-' + zip, 'wb')
            f.write(base64.b64decode(str(get_file_decode[0])))
            f.close()
        except suds.WebFault as detail:
            print('')
            print(detail)

# r = EnvioSunat()
# r.getStatus(ticket='201701051222401',zip='gfffff.zip')
