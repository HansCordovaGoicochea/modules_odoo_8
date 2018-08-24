# -*- coding: utf-8 -*-
import json

import requests
import urllib2
from bs4 import BeautifulSoup
import string
from datetime import datetime

class SUNATRuc(object):

    def __init__(self):
        self.session = requests.session()
        self.url = "http://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/jcrS00Alias"

    def getNumRand(self):
        url = "http://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/captcha?accion=random"
        r1 = self.session.get(url)
        return r1.content

    def getDataRUC(self, ruc):
        numRand = self.getNumRand()
        # print(numRand)
        rpt = {}
        if ruc != "" and numRand is not False:
            values = {
                "accion": "consPorRuc",
                "nroRuc": ruc,
                "numRnd": numRand
            }
            r2 = self.session.post(self.url, data=values)
            soup = BeautifulSoup(r2.text, "lxml")
            # print(soup)
            # RAZON SOCIAL
            input = soup.find("input", {"name": "desRuc"})
            if input:
                input= input['value']
                rpt['Ruc'] = ruc
                rpt['nombre'] = input

                rows = soup.find_all(name='table')[0].find_all('tr')

                datos = []
                for row in rows:
                    # print(row)
                    cols = row.find_all('td')
                    cols = [ele.text.strip() for ele in cols]
                    datos.append([ele for ele in cols if ele])  # Get rid of empty values

                busca = {
                    "nombre_comercial"      : u"Nombre Comercial:",
                    "tipo_contribuyente" 	: u"Tipo Contribuyente:",
                    "fecha_inscripcion" 	: u"Fecha de Inscripción:",
                    "estado_contribuyente" 	: u"Estado del Contribuyente:",
                    "condicion_contribuyente": u"Condición del Contribuyente:",
                    "domicilio_fiscal" 		: u"Dirección del Domicilio Fiscal:",
                    "sistema_emision_comprobante": u"Sistema de Emisión de Comprobante:",
                    "ActividadExterior"		: u"Actividad de Comercio Exterior:",
                    "sistema_contabilidad" 	: u"Sistema de Contabilidad:",
                    "Oficio" 				: u"Profesión u Oficio:",
                    "ActividadEconomica" 	: u"Actividad\(es\) Económica\(s\):",
                    "EmisionElectronica" 	: u"Emisor electrónico desde:",
                    "PLE" 					: u"Afiliado al PLE desde:",
                    "padron" 		: u"Padrones :"
                }
                for key, value in busca.iteritems():
                    for dato in datos:
                        if value in dato[0]:
                            if value in (u'Afiliado al PLE desde:', u'Fecha de Inscripción:', u"Emisor electrónico desde:"):
                                if len(dato[1]) > 4:
                                    fecha = datetime.strptime(dato[1], '%d/%m/%Y')
                                    fecha = fecha.strftime('%Y-%m-%d')
                                    rpt[key] = fecha
                            else:
                                rpt[key] = dato[1]

                d = rpt['domicilio_fiscal'].replace('  ', '')
                de2 = d.split('-')[-2:]
                rpt["address2"] = ' /'.join(de2).strip()

                if rpt["padron"].upper() != 'NINGUNO':
                    rpt["agente_retencion"] = True
                    positiona = rpt["padron"].find('(')
                    positionb = rpt["padron"].find(')')
                    fecha = datetime.strptime(rpt["padron"][positionb + 1:].split(' ')[-1], '%d/%m/%Y')
                    fecha = fecha.strftime('%Y-%m-%d')

                    rpt["agente_retencion_resolucion"] = rpt["padron"][positiona + 1:positionb]
                    rpt["agente_retencion_apartir_del"] = fecha

                rpt['domicilio_fiscal'] = rpt['domicilio_fiscal'].replace('  ', '')
                # print(rpt)
            if len(rpt) > 2:

                legal = self.representanteLegal(ruc) or []
                rpt["representantes_legales"] = legal

                trabs = self.numtrabajadores(ruc) or []
                rpt["cantidad_trabajadores"] = trabs

                return rpt
        return False

    def representanteLegal(self, ruc):
        payload2 = {
            "accion": "getRepLeg",
            "nroRuc": ruc,
            "desRuc": ""
        }

        r3 = self.session.post(self.url, data=payload2)
        # print(r3.text)
        if r3.status_code == 200 and r3:
            objeto = BeautifulSoup(r3.text, "lxml").find_all('div', {'id': 'print'})
            representantes_legales = []
            # print(objeto)
            if len(objeto) > 0:
                objeto = objeto[0].find_all(name='table')[3].find_all('tr')
                for objetito in objeto:
                    # print(objetito)
                    obj = objetito.find_all('td', {'class': 'bg'})
                    if obj:
                        representantes_legales.append({
                            "documento": obj[0].text.strip(),
                            "nro_documento": obj[1].text.strip(),
                            "nombre": obj[2].text.strip(),
                            "cargo": obj[3].text.strip(),
                            "fecha_desde": obj[4].text.strip(),
                        })
            return representantes_legales
        return []

    def numtrabajadores(self, ruc):
        payload3 = {
            "accion": "getCantTrab",
            "nroRuc": ruc,
            "desRuc": ""
        }

        r4 = self.session.post(self.url, data=payload3)
        if r4.status_code == 200 and r4:
            objeto = BeautifulSoup(r4.text, "lxml").find_all('div', {'id': 'print'})
            # print(objeto)
            # [0].find_all(name='table')[3].find_all('tr')
            cantidad_trabajadores = []
            if objeto:
                for objetito in objeto:
                    obj = objetito.find_all('td', {'align': 'center'})
                    # print(obj)
                    if obj:
                        # raise Warning(obj)
                        periodo = obj[0].text.strip().split('-')
                        cantidad_trabajadores.append({
                            "periodo" 		: obj[0].text.strip(),
                            "anio" 				: periodo[0],
                            "mes" 				: periodo[1],
                            "total_trabajadores": obj[1].text.strip(),
                            "pensionista" 		: obj[2].text.strip(),
                            "prestador_servicio": obj[3].text.strip()
                        })
            return cantidad_trabajadores
        return []

    def dnitoruc(self, dni):
        dni = str(dni)
        if dni != "" or len(dni) == 8:
            suma = 0
            hash = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
            suma = 5  # 10[NRO_DNI]X(1 * 5) + (0 * 4)
            for i in range(2, 10):
                # print(dni[i - 2])
                suma += (int(dni[i-2]) * hash[i])  # 3, 2, 7, 6, 5, 4, 3, 2
            entero = int(suma/11)

            digito = 11 - (suma - entero*11)

            if digito == 10:
                digito = 0
            elif digito == 11:
                digito = 1
            return "10"+str(dni)+str(digito)

    def valid(self, valor):  # Script SUNAT
        valor = str(valor.strip())
        if valor:
            if len(valor) == 11:  # RUC
                suma = 0
                x = 6
                for i in range(0, len(valor)-1):
                    if i == 4:
                        x = 8
                    digito = valor[i]
                    x = x -1
                    if i == 0:
                        suma += (int(digito) * x)
                    else:
                        suma += (int(digito) * x)
                resto = suma % 11
                resto = 11 - resto
                if resto >= 10:
                    resto = resto - 10
                if int(resto) == int(valor[len(valor) - 1]):
                    return True
        return False

    def search(self, ruc_dni, inJSON = False):
        if len(str(ruc_dni).strip()) == 8:
            ruc_dni = self.dnitoruc(ruc_dni)
        if len(str(ruc_dni).strip()) == 11 and self.valid(str(ruc_dni).strip()):
            info = self.getDataRUC(ruc_dni)
            if info:
                rtn = {
                    "success": True,
                    "result" : info
                }
            else:
                rtn = {
                    "success": False,
                    "msg": "No se ha encontrado resultados."
                }
            if inJSON:
                return json.dumps(rtn, indent=4, sort_keys=True)
            else:
                return rtn
        rtn = {
            "success": False,
            "msg": "Nro de RUC o DNI no valido."
        }
        if inJSON:
            return json.dumps(rtn, indent=4, sort_keys=True)
        else:
            return rtn

# sunat = SUNATRuc()
# # data = sunat.getDataRUC(20292132591)
# data = sunat.search(20292132591, True)
# print(data)