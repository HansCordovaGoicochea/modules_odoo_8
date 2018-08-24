import suds
from suds.client import Client
from suds.wsse import *
import base64
import logging
import requests
logging.basicConfig(level=logging.INFO)
#logging.getLogger('suds.client').setLevel(logging.DEBUG)

#logging.getLogger('suds.transport').setLevel(logging.DEBUG)
#logging.getLogger('suds.xsd.schema').setLevel(logging.DEBUG)
#logging.getLogger('suds.wsdl').setLevel(logging.DEBUG)

#logging.getLogger('suds.wsdl').setLevel(logging.DEBUG)
#logging.getLogger('suds.wsse').setLevel(logging.DEBUG)
def addSecurityHeader(client, username, password):
    security = Security()
    userNameToken = UsernameToken(username, password)
    #timeStampToken = Timestamp(validity=600)
    security.tokens.append(userNameToken)
    #security.tokens.append(timeStampToken)
    client.set_options(wsse=security)
username = '20495932797MODDATOS'
password = 'MODDATOS'
session = requests.session()
session.auth = (username, password)

url = "https://e-beta.sunat.gob.pe/ol-ti-itcpfegem-beta/billService?wsdl"

client = suds.client.Client(url)
addSecurityHeader(client, username, password)

# Send File
f = open('20495932797-01-F001-1.ZIP', 'rb')
data_file = f.read()

get_file = client.service.sendBill("20495932797-01-F001-1.ZIP", base64.b64encode(str(data_file)))

# Save file
get_file_decode = base64.b64decode(str(get_file[1]))
f = open('R-20495932797-01-F001-1.ZIP', 'w')

f.write(get_file_decode)

f.close()
