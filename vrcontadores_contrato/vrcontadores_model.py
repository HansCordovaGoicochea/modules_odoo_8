# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning,except_orm
import datetime
import calendar
import requests
from datetime import date,timedelta


from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time


def get_data_doc_number(tipo_doc, numero_doc, format='json'):
    print ("Datos")

    user, password = 'demorest', 'demo1234'
    url = 'http://py-devs.com/api'
    url = '%s/%s/%s' % (url, tipo_doc, str(numero_doc))
    res = {'error': True, 'message': None, 'data': {}}
    try:
        response = requests.get(url, auth=(user, password))
    except requests.exceptions.ConnectionError, e:
        res['message'] = 'Error en la conexion'
        return res

    if response.status_code == 200:
        res['error'] = False
        res['data'] = response.json()
    else:
        try:
            res['message'] = response.json()['detail']
        except Exception, e:
            res['error'] = True
    return res

def add_pago_cliente(self, monto_pagar, tipo_pago, fecha_pago, fecha_incio, cliente, est):
    print("Add Cliente----------------------------------------")
    if monto_pagar and tipo_pago:
        if (tipo_pago == 'trabajo'):
            delete = "DELETE FROM res_partner_pagos_cliente WHERE cliente=" + str(cliente) + "AND estado = 'deudor'"
            self._cr.execute(delete)
            if fecha_pago:
                vals = \
                    {'fecha': fecha_pago
                        , 'importe': monto_pagar
                        , 'cliente': cliente
                        , 'estado': 'deudor'
                     }
                self.env['res.partner.pagos_cliente'].create(vals)
        elif (tipo_pago == 'convenio'):
            if fecha_incio:
                delete = "DELETE FROM res_partner_pagos_cliente WHERE cliente="+str(cliente) + "AND estado = 'deudor'"
                self._cr.execute(delete)
                vals = \
                    {'fecha': fecha_incio
                        , 'importe': monto_pagar
                        , 'cliente': cliente
                        , 'estado': 'pagado'
                     }
                self.env['res.partner.pagos_cliente'].create(vals)
        elif (tipo_pago == 'diario'):
            if fecha_incio:
                delete = "DELETE FROM res_partner_pagos_cliente WHERE cliente=" + str(cliente) + "AND estado = 'deudor'"
                self._cr.execute(delete)
                today = datetime.datetime.now()
                dateMonthEnd = "%s-%s-%s" % (
                today.year, 12, calendar.monthrange(today.year - 1, today.month - 1)[1])
                d1 = date(int(fecha_incio[0:4]), int(fecha_incio[5:7]), int(fecha_incio[-2:]))
                d2 = date(int(dateMonthEnd[0:4]), int(dateMonthEnd[5:7]), 31)
                diff = d2 - d1
                for i in range(0, (int(str(diff).split(' ', 1)[0]) + 1), 1):
                    dias = timedelta(days=i)
                    fecha = d1 + dias
                    vals = \
                        {'fecha': fecha
                            , 'importe': monto_pagar
                            , 'cliente': cliente
                            , 'estado': 'deudor'
                         }
                    self.env['res.partner.pagos_cliente'].create(vals)

        elif (tipo_pago == 'mensual'):
            print("mensual----------------------------------------")
            if fecha_incio:
                delete = "DELETE FROM res_partner_pagos_cliente WHERE cliente=" + str(cliente) + "AND estado = 'deudor'"
                self._cr.execute(delete)
                # if est == 'pago':
                #
                # elif est == 'act':
                #     delete = "DELETE FROM res_partner_pagos_cliente WHERE cliente=" + str(cliente)+""
                #     delete1 = "DELETE FROM res_partner_honorarios WHERE parent_id=" + str(cliente)+""
                #     self._cr.execute(delete)
                #     self._cr.execute(delete1)

                fecha = (int(fecha_incio[0:4]), int(fecha_incio[5:7]), int(fecha_incio[-2:]))  #fecha inicial
                today = datetime.datetime.now()
                dateMonthEnd = "%s-%s-%s" % (
                    today.year, 12, calendar.monthrange(today.year - 1, today.month - 1)[1])

                while int(fecha[0]) <= int(dateMonthEnd[0:4]):
                    print("WHILE----------------------------------------")
                    a = int(fecha_incio[0:4])
                    print(a)
                    # Determinar si el año es biciesto o no
                    if (a % 4 == 0 and a % 100 != 0 or a % 400 == 0):
                        meses = (31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)  # tupla con cantidad de meses
                    else:
                        meses = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)  # tupla con cantidad de meses
                    for i in range(0, int(13-int(fecha_incio[5:7]))):
                        suma_meses = int(fecha[1]) + i  # suponiendo cant_meses = 12, esto da 15

                        # print (fecha_incio)
                        # print (int(fecha[0]) + suma_meses / 12)

                        # if int(fecha_incio[5:7])+i == 12:
                        #     nueva_fecha = date(int(fecha_incio[0:4]), int(fecha_incio[5:7])+i, meses[(suma_meses % 12) - 1])
                        # else:
                        nueva_fecha = date(int(fecha[0]), int(fecha_incio[5:7]) + i, meses[(suma_meses % 12) - 1])
                        # print (nueva_fecha)
                        vals = \
                            {'fecha': nueva_fecha
                            , 'importe': monto_pagar
                            , 'cliente': cliente
                            , 'estado': 'deudor'
                         }
                        self.env['res.partner.pagos_cliente'].create(vals)
                    fecha = (int(fecha[0])+1, str(01).zfill(2), str(01).zfill(2))
                    fecha_incio = "%s-%s-%s" % (int(fecha[0]), str(01).zfill(2), str(01).zfill(2))
                    i = 1
                    a = a + 1

        elif (tipo_pago == 'semanal'):
            if fecha_incio:
                delete = "DELETE FROM res_partner_pagos_cliente WHERE cliente=" + str(cliente) + "AND estado = 'deudor'"
                self._cr.execute(delete)
                d1 = date(int(fecha_incio[0:4]), int(fecha_incio[5:7]), int(fecha_incio[-2:]))
                for i in range(0, int(52 - int(d1.strftime("%U")))):
                    vals = \
                        {'fecha': d1
                            , 'importe': monto_pagar
                            , 'cliente': cliente
                            , 'estado': 'deudor'
                         }
                    self.env['res.partner.pagos_cliente'].create(vals)
                    d1 = d1 + timedelta(days=7)

        elif (tipo_pago == 'quincenal'):
            if fecha_incio:
                delete = "DELETE FROM res_partner_pagos_cliente WHERE cliente=" + str(cliente) + "AND estado = 'deudor'"
                self._cr.execute(delete)
                # Determinar si el año es biciesto o no
                a = int(fecha_incio[0:4])
                if (a % 4 == 0 and a % 100 != 0 or a % 400 == 0):
                    meses = (31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)  # tupla con cantidad de meses
                else:
                    meses = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)  # tupla con cantidad de meses

                fecha = (
                int(fecha_incio[0:4]), int(fecha_incio[5:7]), int(fecha_incio[-2:]))  # fecha inicial
                for i in range(0, int(13 - int(fecha_incio[5:7]))):
                    suma_meses = fecha[1] + i  # suponiendo cant_meses = 12, esto da 15
                    if int(fecha_incio[5:7])+i == 12:
                        nueva_fecha_a = date(int(fecha_incio[0:4]), int(fecha_incio[5:7]) + i,
                                             15)
                        nueva_fecha_b = date(int(fecha_incio[0:4]), int(fecha_incio[5:7]) + i,
                                             meses[(suma_meses % 12) - 1])
                    else:
                        nueva_fecha_a = date(fecha[0] + suma_meses / 12, int(fecha_incio[5:7]) + i,
                                             15)
                        nueva_fecha_b = date(fecha[0] + suma_meses / 12, int(fecha_incio[5:7]) + i,
                                             meses[(suma_meses % 12) - 1])

                    vals = \
                        {'fecha': nueva_fecha_a
                            , 'importe': monto_pagar
                            , 'cliente': cliente
                            , 'estado': 'deudor'
                         }
                    self.env['res.partner.pagos_cliente'].create(vals)
                    vals = \
                        {'fecha': nueva_fecha_b
                            , 'importe': monto_pagar
                            , 'cliente': cliente
                            , 'estado': 'deudor'
                         }
                    self.env['res.partner.pagos_cliente'].create(vals)


class res_partner(models.Model):
    _inherit = "res.partner"

    partner_contrato_ids = fields.One2many('res.cliente.contrato', 'partner_id')

class res_cliente_contrato(models.Model):
    _name = 'res.cliente.contrato'
    _rec_name = 'partner_id'
    # _description = 'New Description'

    partner_id = fields.Many2one('res.partner', string='Cliente', ondelete='cascade')
    monto_pagar = fields.Float('Monto a Pagar', required=True)
    fecha_inicio = fields.Date('Fecha Inicio de Contrato', required=True)
    tipo_pago = fields.Selection(
        [('quincenal', 'Quincenal'), ('mensual', 'Mensual'), ('semanal', 'Semanal'), ('diario', 'Diario'),
         ('trabajo', 'Por Trabajo'),
         ('convenio', 'Convenio'),('cancelado', 'Contrato Cancelado')], 'Tipo de Pago', default='quincenal', required=True)
    fecha_pago = fields.Date('Fecha de Pago')

    @api.multi
    def write(self, vals, context=None):


        if vals.has_key('fecha_inicio'):
            fecha_inicio = vals['fecha_inicio']
        else:
            fecha_inicio = self.fecha_inicio

        if vals.has_key('tipo_pago'):
            tipo_pago = vals['tipo_pago']
        else:
            tipo_pago = self.tipo_pago
        print (fecha_inicio, tipo_pago)
        if fecha_inicio:
            self._cr.execute(
                """SELECT COUNT(id) FROM res_partner_pagos_cliente WHERE estado = %s and fecha >= %s and cliente = %s""",
                ('pagado', fecha_inicio, self.partner_id.id))
            count_ids = self._cr.fetchone()[0]
            print (count_ids)
            if count_ids > 0:
                raise except_orm(_('Error!'), _("Hay Cuotas en fechas posteriores porfavor registre otra fecha!!"))
            else:
                if fecha_inicio or tipo_pago:
                    add_pago_cliente(self, self.monto_pagar, tipo_pago,
                                     self.fecha_pago, fecha_inicio, self.partner_id.id, 'act')

        return super(res_cliente_contrato, self).write(vals)


