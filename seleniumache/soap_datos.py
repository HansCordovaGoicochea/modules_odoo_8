from suds.client import Client

client = Client(url='http://www.enlacesframework.info/wsfesunat/feosesunat.php?wsdl')
print(client.service.FE_Ruc_Sunat('20453679757'))