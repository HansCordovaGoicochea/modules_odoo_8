# -*- coding: ISO-8859-1 -*-
# from __future__ import unicode_literals

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


SIGN_REF_TMPL = """<ds:SignedInfo xmlns="urn:sunat:names:specification:ubl:peru:schema:xsd:VoidedDocuments-1" xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2" xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2" xmlns:ds="http://www.w3.org/2000/09/xmldsig#" xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2" xmlns:sac="urn:sunat:names:specification:ubl:peru:schema:xsd:SunatAggregateComponents-1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><ds:CanonicalizationMethod Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315"></ds:CanonicalizationMethod><ds:SignatureMethod Algorithm="http://www.w3.org/2000/09/xmldsig#rsa-sha1"></ds:SignatureMethod><ds:Reference URI=""><ds:Transforms><ds:Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature"></ds:Transform></ds:Transforms><ds:DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"></ds:DigestMethod><ds:DigestValue>%(digest_value)s</ds:DigestValue></ds:Reference></ds:SignedInfo>"""


SIGNED_TMPL = """<ds:Signature Id="SignSUNAT">%(signed_info)s<ds:SignatureValue>%(signature_value)s</ds:SignatureValue>%(key_info)s</ds:Signature>"""

KEY_INFO_RSA_TMPL = """<ds:KeyInfo><ds:X509Data><ds:X509Certificate>%(certificate)s</ds:X509Certificate></ds:X509Data></ds:KeyInfo>"""


def canonicalize(xml,c14n_exc=True):
    et = etree.parse(xml)
    output = StringIO.StringIO()
    et.write_c14n(output)
    return output.getvalue()

def sha1_hash_digest(payload):
    return base64.b64encode(hashlib.sha1(payload).digest())

class ProbandoBaja(object):

    def rsa_sign(self, xml, ref_uri,private_key,password=None, cert=None, c14n_exc=True,
                 sign_template=SIGN_REF_TMPL, key_info_template=KEY_INFO_RSA_TMPL):

        ref_xml = canonicalize(xml,c14n_exc)
        # print ref_xml


        p12 = crypto.load_pkcs12(open(private_key, 'rb').read(), password)
        pem_string = crypto.dump_privatekey(crypto.FILETYPE_PEM, p12.get_privatekey())
        cer_string = crypto.dump_certificate(crypto.FILETYPE_PEM, p12.get_certificate())
        cer_string = cer_string.replace('-----BEGIN CERTIFICATE-----\n', '').replace('-----END CERTIFICATE-----\n', '')

        signed_info = sign_template % {'ref_uri': ref_uri,
                                       'digest_value': sha1_hash_digest(ref_xml)}

        signedInfoDigestValue = hashlib.sha1(signed_info).digest().strip()
        # print (base64.b64encode(hashlib.sha1(signed_info).digest().strip()))
        # print sfff._generate_signed_info(ref_xml)
        # print (signedInfoDigestValue)

        pkey = RSA.load_key_string(pem_string)
        signature = pkey.sign(signedInfoDigestValue)
        firma = signature.encode('base64').strip()
        latin_1_encoded = firma.encode(encoding="ISO-8859-1").strip()


        return {'ref_xml': ref_xml, 'ref_uri': ref_uri,
                'signed_info': signed_info,
                'signature_value':latin_1_encoded,
                'key_info': self.key_info(pkey, p12.get_certificate(), cer_string,key_info_template),
                'digest_value': sha1_hash_digest(ref_xml)
                }
        # print base64.b64encode(signature)

    def key_info(self, pkey, x509, cer_string, key_info_template):
        return key_info_template % {'certificate': cer_string}


    def sign_xml(self, fichero_xml):
        path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'archivos/certificado/a.pfx'))
        key_file = path.replace('\\', '/')
        name = fichero_xml
        vars = self.rsa_sign(xml=fichero_xml,ref_uri="", private_key=key_file, password="SCSANFRACISCO2018")

        firma = SIGNED_TMPL % vars
        firma = firma.replace('<ds:Signature Id="SignSUNAT">','<ds:Signature Id="SignSUNAT" xmlns:ds="http://www.w3.org/2000/09/xmldsig#">')

        firma = firma.replace('<ds:SignedInfo xmlns="urn:sunat:names:specification:ubl:peru:schema:xsd:VoidedDocuments-1" xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2" xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2" xmlns:ds="http://www.w3.org/2000/09/xmldsig#" xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2" xmlns:sac="urn:sunat:names:specification:ubl:peru:schema:xsd:SunatAggregateComponents-1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">','<ds:SignedInfo xmlns:ds="http://www.w3.org/2000/09/xmldsig#">')

        firma = firma.replace('<ds:CanonicalizationMethod Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315"></ds:CanonicalizationMethod><ds:SignatureMethod Algorithm="http://www.w3.org/2000/09/xmldsig#rsa-sha1"></ds:SignatureMethod><ds:Reference URI=""><ds:Transforms><ds:Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature"></ds:Transform></ds:Transforms><ds:DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"></ds:DigestMethod>','<ds:CanonicalizationMethod Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315"/><ds:SignatureMethod Algorithm="http://www.w3.org/2000/09/xmldsig#rsa-sha1"/><ds:Reference URI=""><ds:Transforms><ds:Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature"/></ds:Transforms><ds:DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"/>')

        firma_xml = etree.fromstring(firma)

        tree = etree.parse(name)

        factura = tree.getroot()
        factura.append(firma_xml)

        xml_firmado = ''

        for line in open(name, 'r'):
            output_line = line
            output_line = string.replace(output_line, '<ext:ExtensionContent/>',
                                         '<ext:ExtensionContent>'
                                         + str(firma)
                                         + '</ext:ExtensionContent>')

            output_line = string.replace(output_line,'<?xml version="1.0" encoding="ISO-8859-1" standalone="no"?>','<?xml version="1.0" encoding="ISO-8859-1"?>')
            xml_firmado += output_line

        f = open(name, 'w')
        f.write(xml_firmado)
        f.close()


        p5= fichero_xml.find('envio')
        pathrecortado = str(fichero_xml[p5+6::])
        print ('>>>>>>'+pathrecortado)
        path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'archivos/envio'))
        path = path.replace('\\', '/')
        base_dir = r"" + path
        nombrefichero = fichero_xml.replace(".xml","")
        zf = zipfile.ZipFile(nombrefichero+'.zip','w')
        zf.write(os.path.join(base_dir, pathrecortado), arcname=pathrecortado)
        zf.close()
        return vars['digest_value']


# r = ProbandoBaja()
# path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'archivos/envio'))
# path = path.replace('\\', '/')
# base_dir = r"" + path
# r.sign_xml(fichero_xml=base_dir+'/20495932797-RA-20170217-001.xml')