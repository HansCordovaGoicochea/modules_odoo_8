import suds
import base64
import bitarray
from suds.wsse import *
import base64
import logging
import requests
import logging
logging.basicConfig(level=logging.DEBUG)

url = "https://e-beta.sunat.gob.pe/ol-ti-itcpfegem-beta/billService?wsdl"

def addSecurityHeader(client, username, password):
    security = Security()
    userNameToken = UsernameToken(username, password)
    #timeStampToken = Timestamp(validity=600)
    security.tokens.append(userNameToken)
    #security.tokens.append(timeStampToken)
    client.set_options(wsse=security)

headers = {'Content-Type': 'application/soap+xml; charset="UTF-8"'}
client = suds.client.Client(url, headers=headers, cache=None)
username = '20570867939MODDATOS'
password = 'MODDATOS'
session = requests.session()
session.auth = (username, password)


#client = suds.client.Client(url)
addSecurityHeader(client, username, password)

f = open('20570867939-01-F001-109.ZIP', 'rb')
data_file = f.read()

#with open("20495932797-01-F001-1234.ZIP", "rb") as f:
#    bytes = f.read()
#    encoded = base64.b64encode(str(bytes))

weather = client.service.sendBill("20570867939-01-F001-109.ZIP", base64.b64encode(str(data_file)))

print str(weather)
