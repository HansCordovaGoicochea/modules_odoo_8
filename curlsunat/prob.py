# -*- coding: utf-8 -*-
import json

import requests
import urllib2
from bs4 import BeautifulSoup

rpt = {}

url1 = "http://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/captcha?accion=random"
url2 = "http://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/jcrS00Alias"
ses = requests.Session()  # use this object for all get / post requests #
r1 = ses.get(url1)

payload = {
                "accion": "consPorRuc",
                "nroRuc": 20453679757,
                "numRnd": r1.content
            }
# print(payload)
r2 = ses.post(url2, data=payload)
# print(ses.cookies.get_dict())
# print(r2.text)
soup = BeautifulSoup(r2.text, "lxml")


# print table
# RAZON SOCIAL
input = soup.find("input", {"name": "desRuc"})['value']
rpt['Ruc'] = 20453679757
rpt['RazonSocial'] = input

rows = soup.find_all(name='table')[0].find_all('tr')

datos = []
for row in rows:
    # print(row)
    cols = row.find_all('td')
    # print(cols)
    cols = [ele.text.strip() for ele in cols]
    datos.append([ele for ele in cols if ele])  # Get rid of empty values

# print(datos)
print('-----------------')
busca = {
        "NombreComercial" 		: u"Nombre Comercial:",
        "Tipo" 					: u"Tipo Contribuyente:",
        "Inscripcion" 			: u"Fecha de Inscripción:",
        "Estado" 				: u"Estado del Contribuyente:",
        "CondicionContribuyente": u"Condición del Contribuyente:",
        "Direccion" 			: u"Dirección del Domicilio Fiscal:",
        "SistemaEmision" 		: u"Sistema de Emisión de Comprobante:",
        "ActividadExterior"		: u"Actividad de Comercio Exterior:",
        "SistemaContabilidad" 	: u"Sistema de Contabilidad:",
        "Oficio" 				: u"Profesión u Oficio:",
        "ActividadEconomica" 	: u"Actividad\(es\) Económica\(s\):",
        "EmisionElectronica" 	: u"Emisor electrónico desde:",
        "PLE" 					: u"Afiliado al PLE desde:"
}
# print(busca)
for key, value in busca.iteritems():
    for data in datos:
        if value in data[0]:
            rpt[key] = data[1]

# r = json.dumps(rpt, indent=4)
# r = json.dumps(rpt, indent=4, sort_keys=True)
# print(rpt)
print('-----------')
if len(rpt) > -1:
    legal = []

    payload2 = {
        "accion": "getRepLeg",
        "nroRuc": 20453679757,
        "desRuc": ""
    }

    r3 = ses.post(url2, data=payload2)
    # print(r3.text)
    if r3.status_code == 200 and r3:
        objeto = BeautifulSoup(r3.text, "lxml").find_all('div', {'id': 'print'})[0].find_all(name='table')[3].find_all('tr')

        representantes_legales = []
        for objetito in objeto:
            # print(objetito)
            obj = objetito.find_all('td', {'class': 'bg'})
            if obj:
                representantes_legales.append({
                    "tipodoc": obj[0].text.strip(),
                    "numdoc": obj[1].text.strip(),
                    "nombre": obj[2].text.strip(),
                    "cargo": obj[3].text.strip(),
                    "desde": obj[4].text.strip(),
                })
        rpt["representantes_legales"] = representantes_legales

    trabs = []

    payload3 = {
        "accion": "getCantTrab",
        "nroRuc": 20453679757,
        "desRuc": ""
    }

    r4 = ses.post(url2, data=payload3)
    if r4.status_code == 200 and r4:
        objeto = BeautifulSoup(r4.text, "lxml").find_all('div', {'id': 'print'})[0].find_all(name='table')[3].find_all('tr')
        cantidad_trabajadores = []
        for objetito in objeto:
            obj = objetito.find_all('td', {'align': 'center'})
            # print(obj)
            if obj:
                # raise Warning(obj)
                periodo = obj[0].text.strip().split('-')
                cantidad_trabajadores.append({
                    "periodo" 			: obj[0].text.strip(),
                    "anio" 				: periodo[0],
                    "mes" 				: periodo[1],
                    "total_trabajadores": obj[1].text.strip(),
                    "pensionista" 		: obj[2].text.strip(),
                    "prestador_servicio": obj[3].text.strip()
                })
        rpt["cantidad_trabajadores"] = cantidad_trabajadores

print(json.dumps(rpt, indent=4))