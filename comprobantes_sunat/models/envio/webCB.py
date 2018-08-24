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


class EnvioSunat(object):

    def Envio(self, zip):
        logging.basicConfig(level=logging.DEBUG)
        # logging.getLogger('suds.client').setLevel(logging.DEBUG)
        path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'archivos/envio'))
        path = path.replace('\\', '/')
        path = r"" + path
        # path = 'd:/'

        username = '20495932797ADMINSC2'
        password = 'CARNAVAL'
        session = requests.session()
        session.auth = (username, password)

        # username = '20495932797MODDATOS'
        # password = 'moddatos'
        url = "https://e-beta.sunat.gob.pe/ol-ti-itcpfegem-beta/billService?wsdl"
        # url = "https://www.sunat.gob.pe/ol-ti-itcpgem-sqa/billService?wsdl"
        # url = urlparse.urljoin('file:', urllib.pathname2url(os.path.abspath("openerp/modulosnuevos/comprobantes_sunat/sunattest.wsdl")))  # produccion mejorado
        headers = {'Host': 'www.sunat.gob.pe:443', 'SOAPAction': "urn:sendSummary"}
        cliente = suds.client.Client(url, headers=headers, cache=None)
        addSecurityHeader(cliente, username, password)

        g = open(r'' + path + '/' + zip, 'rb')
        data_file = g.read()
        # f = open(r'' + zip, 'rb')

        try:
            print('>>JUSTO VOY >>>>')
            print('CDR CREADOOOOOOOOOOOOOO')
            get_file = cliente.service.sendSummary(zip, base64.b64encode(str(data_file).strip()))
            g.close()
            print ('>>ticket>>>>', str(get_file))
            # time.sleep(5)
            get_file_decode = cliente.service.getStatus(str(get_file))
            print('>><<decode>', str(get_file_decode))
            path2 = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'archivos/recepcionado'))
            path2 = path2.replace('\\', '/')
            path2 = r"" + path2
            print(path2)
            f = open(r'' + path2 + '/' + 'R-' + zip, 'wb')

            f.write(base64.b64decode(str(get_file_decode[0])))
            f.close()
            return get_file
        except suds.WebFault as detail:
            print('')

    # def consultarCDR(self, rucEmisor, tipoComprobante, serieCom,
    #                  numeroCom):
    #
    #     try:
    #         print('>>JUSTO VOY >>>>')
    #         get_file = cliente.service.getStatusCdr(rucEmisor, tipoComprobante, serieCom, numeroCom)
    #         g.close()
    #         print ('>>ticket>>>>', str(get_file))
    #         get_file_decode = cliente.service.getStatus(str(get_file))
    #         print('>><<decode>', str(get_file_decode))
    #         path2 = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'archivos/recepcionado'))
    #         path2 = path2.replace('\\', '/')
    #         path2 = r"" + path2
    #         print(path2)
    #         f = open(r'' + path2 + '/' + 'R' + zip, 'wb')
    #         # print ('llegeueeeeeeeeee')
    #         f.write(base64.b64decode(str(get_file_decode[0])))
    #         f.close()
    #         return get_file
    #     except suds.WebFault as detail:
    #         print('')

# r = EnvioSunat()
# r.Envio(zip='20495932797-RC-20170309-011.ZIP')
