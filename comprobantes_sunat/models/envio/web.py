# -*- coding: utf-8 -*-

from __future__ import print_function
import base64
import logging
import os
import urllib
import urlparse

import requests
import suds
import suds.client
from suds.client import Client
from suds.wsse import *
# from suds.sax.element import Element.
from suds.bindings import binding
import zipfile
# sys.setrecursionlimit(10000) --malogra el sistema


def addSecurityHeader(client, username, password):
    # wsans = ('wsa', "http://www.w3.org/2005/08/addressing")
    security = Security()
    userNameToken = UsernameToken(username, password)
    timeStampToken = Timestamp(validity=600)
    # timeStampToken = Timestamp(validity=600)
    security.tokens.append(userNameToken)
    security.tokens.append(timeStampToken)
    # print(security.tokens)
    # action = client.service.sendBill.method.soap.action
    client.set_options(wsse=security)
    # client.set_options(wsse=security,soapheaders = Element('Action', ns=wsans).setText(action))


class EnvioSunat(object):

    def Envio(self, zip):
        logging.basicConfig(level=logging.DEBUG)
        # logging.getLogger('suds.client').setLevel(logging.DEBUG)
        # logging.getLogger('suds.transport.http').setLevel(logging.DEBUG)
        # logging.getLogger('suds.wsdl').setLevel(logging.DEBUG)
        path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'archivos/envio'))
        path = path.replace('\\', '/')
        path = r"" + path

        username = '20495932797MODDATOS'
        password = 'moddatos'
        # username = '20495932797ADMINSC2'
        # password = 'CARNAVAL'
        session = requests.session()

        session.auth = (username, password)

        # url = "https://www.sunat.gob.pe/ol-ti-itcpgem-sqa/billService?wsdl"
        url = "https://e-beta.sunat.gob.pe/ol-ti-itcpfegem-beta/billService?wsdl"
        # url = urlparse.urljoin('file:', urllib.pathname2url(os.path.abspath("openerp/modulosnuevos/comprobantes_sunat/sunattest.wsdl")))  # produccion mejorado
        headers = {'Host': 'www.sunat.gob.pe:443', 'SOAPAction': "urn:sendBill"}
        # binding.envns = ('SOAP-ENV', 'http://www.w3.org/2003/05/soap-envelope')
        cliente = suds.client.Client(url, headers=headers,cache=None)
        addSecurityHeader(cliente, username, password)

        # # sent file
        g = open(r'' + path + '/' + zip, 'rb')
        data_file = g.read()

        # print(base64.b64encode(str(data_file)))
        try:
            get_file = cliente.service.sendBill(zip, base64.b64encode(str(data_file)))
            g.close()
            # Save file
            get_file_decode = base64.b64decode(str(get_file).strip())
            rec = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'archivos/recepcionado'))
            rec = rec.replace('\\', '/')
            rec = r"" + rec
            dir_p = r'' + rec + '/' + 'R-' + zip
            f = open(r'' + rec + '/' + 'R-' + zip, 'wb')
            f.write(get_file_decode)

            f.close()
            print ('Recepcionado!!!!!!!!!!!!!')
            dir_rep = dir_p
            zipe = zipfile.ZipFile(dir_rep)
            cortando2 = dir_rep.replace('.zip', '.xml')
            cortando3 = cortando2.replace(rec+'/', '')
            file = zipe.read(cortando3)
            zipe.close()
            # print (file)
            return file

        except suds.WebFault as detail:
            print (detail)
            return detail
#
# r = EnvioSunat()
# r.Envio(zip='20495932797-07-FF60-00000074.zip')
