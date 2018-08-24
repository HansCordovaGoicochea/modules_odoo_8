# -*- coding: utf-8 -*-
import string
import os
import base64
import StringIO
import hashlib
from xml.etree import ElementTree
import subprocess
from M2Crypto import RSA
from OpenSSL import crypto
from lxml import etree
import zipfile
import suds
from suds.wsse import *
import requests
import logging
import zipfile

import urlparse, urllib, os
from lxml.etree import DocumentInvalid

logging.basicConfig(level=logging.DEBUG)

SIGN_REF_TMPL = """<ds:SignedInfo xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2" xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2" xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2" xmlns:ccts="urn:un:unece:uncefact:documentation:2" xmlns:ds="http://www.w3.org/2000/09/xmldsig#" xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2" xmlns:qdt="urn:oasis:names:specification:ubl:schema:xsd:QualifiedDatatypes-2" xmlns:sac="urn:sunat:names:specification:ubl:peru:schema:xsd:SunatAggregateComponents-1" xmlns:udt="urn:un:unece:uncefact:data:specification:UnqualifiedDataTypesSchemaModule:2" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><ds:CanonicalizationMethod Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315"></ds:CanonicalizationMethod><ds:SignatureMethod Algorithm="http://www.w3.org/2000/09/xmldsig#rsa-sha1"></ds:SignatureMethod><ds:Reference URI=""><ds:Transforms><ds:Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature"></ds:Transform></ds:Transforms><ds:DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"></ds:DigestMethod><ds:DigestValue>%(digest_value)s</ds:DigestValue></ds:Reference></ds:SignedInfo>"""

SIGNED_TMPL = """<ds:Signature Id="SignSUNAT" xmlns:ds="http://www.w3.org/2000/09/xmldsig#">%(signed_info)s<ds:SignatureValue>%(signature_value)s</ds:SignatureValue>%(key_info)s</ds:Signature>"""

KEY_INFO_RSA_TMPL = """<ds:KeyInfo><ds:X509Data><ds:X509Certificate>%(certificate)s</ds:X509Certificate></ds:X509Data></ds:KeyInfo>"""


def addSecurityHeader(client, username, password):
    security = Security()
    userNameToken = UsernameToken(username, password)
    security.tokens.append(userNameToken)
    client.set_options(wsse=security)


def canonicalize(xml, c14n_exc=True):
    et = etree.parse(xml)
    output = StringIO.StringIO()
    et.write_c14n(output)
    return output.getvalue()


def sha1_hash_digest(payload):
    return base64.b64encode(hashlib.sha1(payload).digest())


class Probando():
    def rsa_sign(self, xml, ref_uri, private_key, password=None, cert=None, mime_type='text/xml', c14n_exc=False, sign_template=SIGN_REF_TMPL, key_info_template=KEY_INFO_RSA_TMPL):

        ref_xml = canonicalize(xml)

        p12 = crypto.load_pkcs12(open(private_key, 'rb').read(), password)
        pem_string = crypto.dump_privatekey(crypto.FILETYPE_PEM, p12.get_privatekey())
        cer_string = crypto.dump_certificate(crypto.FILETYPE_PEM, p12.get_certificate())
        cer_string = cer_string.replace('-----BEGIN CERTIFICATE-----\n', '').replace('-----END CERTIFICATE-----\n', '')

        signed_info = sign_template % {'ref_uri': ref_uri,
                                       'digest_value': sha1_hash_digest(ref_xml)}

        # signedInfoDigestValue = hashlib.sha1(signed_info).digest().strip()

        pkey = RSA.load_key_string(pem_string)
        signature = pkey.sign(hashlib.sha1(signed_info).digest())
        # firma = signature.encode('base64').strip()
        # latin_1_encoded = firma.encode(encoding="ISO-8859-1").strip()

        return {'ref_xml': ref_xml,
                'ref_uri': ref_uri,
                'signed_info': signed_info,
                'signature_value': base64.b64encode(signature),
                'key_info': self.key_info(pkey, p12.get_certificate(), cer_string, mime_type, key_info_template),
                'digest_value': sha1_hash_digest(ref_xml)
                }

    def key_info(self, pkey, x509, cer_string, mime_type, key_info_template):
        return key_info_template % {'certificate': cer_string}

    def sign_xml(self, fichero_xml):
        path = os.path.abspath(
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'account_invoice/archivos/certificado/a.pfx'))
        key_file = path.replace('\\', '/')
        # key_file = 'D:/a.pfx'
        name = fichero_xml
        vars = self.rsa_sign(xml=fichero_xml, ref_uri="", private_key=key_file, password="SCSANFRACISCO2018", mime_type='text/xml')

        firma = SIGNED_TMPL % vars

        # firma = firma.replace('<ds:Signature Id="SignSUNAT">',
        #                       '<ds:Signature Id="SignSUNAT" xmlns:ds="http://www.w3.org/2000/09/xmldsig#">')
        #
        # firma = firma.replace(
        #     '<ds:SignedInfo xmlns="urn:oasis:names:specification:ubl:schema:xsd:CreditNote-2" xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2" xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2" xmlns:ccts="urn:un:unece:uncefact:documentation:2" xmlns:ds="http://www.w3.org/2000/09/xmldsig#" xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2" xmlns:qdt="urn:oasis:names:specification:ubl:schema:xsd:QualifiedDatatypes-2" xmlns:sac="urn:sunat:names:specification:ubl:peru:schema:xsd:SunatAggregateComponents-1" xmlns:udt="urn:un:unece:uncefact:data:specification:UnqualifiedDataTypesSchemaModule:2" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">',
        #     '<ds:SignedInfo xmlns:ds="http://www.w3.org/2000/09/xmldsig#">')
        #
        # firma = firma.replace(
        #     '<ds:CanonicalizationMethod Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315"></ds:CanonicalizationMethod><ds:SignatureMethod Algorithm="http://www.w3.org/2000/09/xmldsig#rsa-sha1"></ds:SignatureMethod><ds:Reference URI=""><ds:Transforms><ds:Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature"></ds:Transform></ds:Transforms><ds:DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"></ds:DigestMethod>',
        #     '<ds:CanonicalizationMethod Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315"/><ds:SignatureMethod Algorithm="http://www.w3.org/2000/09/xmldsig#rsa-sha1"/><ds:Reference URI=""><ds:Transforms><ds:Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature"/></ds:Transforms><ds:DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"/>')

        firma_xml = etree.fromstring(firma)

        file_path_xmldsig = os.path.join(os.path.dirname(__file__), 'archivos/xmldsig-core-schema.xsd')
        schema_file_xmldsig = open(file_path_xmldsig)
        xmlschema_doc_xmldsig = etree.parse(schema_file_xmldsig)
        xmlschema_xmldsig = etree.XMLSchema(xmlschema_doc_xmldsig)
        try:
            xmlschema_xmldsig.assertValid(firma_xml)
        except DocumentInvalid as e:
            raise Warning('Error de Datos', """El sistema generó la firma electrónica del XML pero la firma electrónica no pasa la validación XSD de xmldsig.
                          \nEl siguiente error contiene el identificador o número de documento en conflicto:\n\n %s""" % str(e))

        file_path_xades = os.path.join(os.path.dirname(__file__), 'archivos/XAdES1.2.2.xsd')
        schema_file_xades = open(file_path_xades)
        xmlschema_doc_xades = etree.parse(schema_file_xades)
        xmlschema_xades = etree.XMLSchema(xmlschema_doc_xades)
        try:
            xmlschema_xades.assertValid(firma_xml)
        except DocumentInvalid as e:
            raise Warning('Error de Datos', """El sistema generó la firma electrónica del XML pero la firma electrónica no pasa la validación XSD del estándar XadES_BES.
                          \nEl siguiente error contiene el identificador o número de documento en conflicto:\n\n %s""" % str(e))

        tree = etree.parse(name)
        factura = tree.getroot()
        factura.append(firma_xml)
        tree = etree.ElementTree(factura)

        xml_firmado = ''

        for line in open(name, 'r'):
            output_line = line
            output_line = string.replace(output_line, '<ext:ExtensionContent></ext:ExtensionContent>',
                                         '<ext:ExtensionContent>' + str(firma) + '</ext:ExtensionContent>')
            xml_firmado += output_line

        print (name)
        f = open(name, 'w')
        f.write(xml_firmado)
        f.close()
        # tree.write(name, pretty_print=True, xml_declaration=True, encoding='utf-8', method="xml")
        return vars['digest_value']


class webService():
    def consumir(self, zip, rzip, name):
        logging.basicConfig(level=logging.DEBUG)
        # url = "https://www.sunat.gob.pe/ol-ti-itcpgem-sqa/billService?wsdl" # homologacion
        url = "https://e-beta.sunat.gob.pe/ol-ti-itcpfegem-beta/billService?wsdl"
        # url = 'https://e-factura.sunat.gob.pe/ol-ti-itcpfegem/billService?wsdl' # produccion con errores
        # url = urlparse.urljoin('file:', urllib.pathname2url(os.path.abspath("openerp/modulosnuevos/account_invoice/sunatbeta.wsdl"))) # produccion mejorado
        # url = 'http://192.168.1.7:81/sunatWC/sunatbeta.xml'  # produccion mejorado
        print (url)
        headers = {'Host': 'www.sunat.gob.pe:443', 'SOAPAction': "urn:sendBill"}
        client = suds.client.Client(url, headers=headers, cache=None)
        # print (client)
        username = '20495932797MODDATOS'
        password = 'moddatos'
        # username = '20495932797ADMINSC2'
        # password = 'CARNAVAL'
        session = requests.session()
        session.auth = (username, password)

        addSecurityHeader(client, username, password)

        f_e = open(zip, 'rb')
        data_file = f_e.read()
        try:
            get_file = client.service.sendBill(name, base64.b64encode(str(data_file)))
            # print (get_file)
            f_e.close()

            get_file_decode = base64.b64decode(str(get_file))
            f_r = open(rzip, 'wb')
            f_r.write(get_file_decode)
            f_r.close()

        except suds.WebFault as detail:
            print('-- Detalle error -->', str(detail))
            # print('')

            # def consultarCDR(self, name):
            #     zip = zipfile.ZipFile(name)
            #     cortando = name.replace('d:/','')
            #     cortando2 = cortando.replace('.zip','.xml')
            #     file = zip.read(cortando2)
            #     g = file.find('<cbc:ResponseCode>')
            #     f = file.find('</cbc:ResponseCode>')
            #     cadena = file[g + 18:f]
            #     if int(cadena) == 0:
            #         ge = file.find('<cbc:Description>')
            #         fe = file.find('</cbc:Description>')
            #         cadena2 = file[ge + 17:fe]
            #         print(cadena2)
            #     else:
            #         print('Errorrrrrrrrrrrrrrrr')
            #     zip.close()

# r = webService()
# r = Probando()
# # r.consumir(zip='20495932797-01-FF11-00000051.zip')
# r.sign_xml(fichero_xml='d:/2.xml')