# -*- coding: utf-8 -*-
from openerp import models, fields, api, _, SUPERUSER_ID, tools
from openerp.exceptions import Warning, except_orm
import datetime
import calendar
import requests
from datetime import date, timedelta


def get_data_doc_number(tipo_doc, numero_doc, format='json'):
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
    if monto_pagar and tipo_pago:
        if (tipo_pago == 'trabajo'):
            # consulta para eliminar los pagos actuales de acuerdo al contrato, que tiene como estado
            # (deudor) y que se encuentran mayores a la fecha de filtro
            delete = "DELETE FROM res_partner_pagos_cliente WHERE cliente=" + str(
                cliente) + "AND estado = 'deudor' AND fecha > '" + fecha_incio + "'"
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
                # consulta para eliminar los pagos actuales de acuerdo al contrato, el estado
                # (deudor) y que la se encuentran el la fecha mayor a la de filtro
                delete = "DELETE FROM res_partner_pagos_cliente WHERE cliente=" + str(
                    cliente) + "AND estado = 'deudor' AND fecha > '" + fecha_incio + "'"
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
                # consulta para eliminar los pagos actuales de acuerdo al contrato, que tiene como estado
                # (deudor) y que se encuentran mayores a la fecha de filtro
                delete = "DELETE FROM res_partner_pagos_cliente WHERE cliente=" + str(
                    cliente) + "AND estado = 'deudor' AND fecha > '" + fecha_incio + "'"
                self._cr.execute(delete)
                today = datetime.datetime.now()
                dateMonthEnd = "%s-%s-%s" % (
                    today.year, 12, calendar.monthrange(today.year - 1, today.month - 1)[1])
                d1 = date(int(fecha_incio[0:4]), int(fecha_incio[5:7]), int(fecha_incio[-2:]))
                d2 = date(int(dateMonthEnd[0:4]), int(dateMonthEnd[5:7]), 31)
                # diferencia de fechas para sacar el numero de dias
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
            if fecha_incio:
                # consulta para eliminar los pagos actuales de acuerdo al contrato, que tiene como estado
                # (deudor) y que se encuentran mayores a la fecha de filtro
                delete = "DELETE FROM res_partner_pagos_cliente WHERE cliente=" + str(
                    cliente) + "AND estado = 'deudor' AND fecha >= '" + fecha_incio + "'"
                self._cr.execute(delete)
                # ----------        AÑO       -------   MES         ------    DIA ---------
                fecha = (int(fecha_incio[0:4]), int(fecha_incio[5:7]), int(fecha_incio[-2:]))  # fecha inicial
                today = datetime.datetime.now()

                dateMonthEnd = "%s-%s-%s" % (
                    today.year, 12, calendar.monthrange(today.year - 1, 12 if today.month == 1 else today.month - 1)[1])

                while int(fecha[0]) <= int(dateMonthEnd[0:4]):
                    a = int(fecha_incio[0:4])
                    print(a)
                    # Determinar si el año es biciesto o no
                    if (a % 4 == 0 and a % 100 != 0 or a % 400 == 0):
                        meses = (31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)  # tupla con cantidad de meses
                    else:
                        meses = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)  # tupla con cantidad de meses
                    for i in range(0, int(13 - int(fecha_incio[5:7]))):
                        suma_meses = int(fecha[1]) + i  # suponiendo cant_meses = 12, esto da 15

                        nueva_fecha = date(int(fecha[0]), int(fecha_incio[5:7]) + i, meses[(suma_meses % 12) - 1])

                        # buscar los pagos echos en el ultimo dia del mes ingresado
                        pagos = self.pool.get('res.partner.pagos_cliente').search(self.env.cr, self.env.uid,
                                                                                  [('cliente', '=', self.id),
                                                                                   ("fecha", '=', nueva_fecha),
                                                                                   ("estado", '=', 'pagado')])

                        # si en esa fecha existen pagos, se pasara al sigiente mes
                        if pagos:
                            print "-"
                        else:

                            vals = \
                                {'fecha': nueva_fecha
                                    , 'importe': monto_pagar
                                    , 'cliente': cliente
                                    , 'estado': 'deudor'
                                 }
                            self.env['res.partner.pagos_cliente'].create(vals)

                    fecha = (int(fecha[0]) + 1, str(01).zfill(2), str(01).zfill(2))
                    fecha_incio = "%s-%s-%s" % (int(fecha[0]), str(01).zfill(2), str(01).zfill(2))
                    i = 1
                    a = a + 1

        elif (tipo_pago == 'semanal'):
            if fecha_incio:
                # consulta para eliminar los pagos actuales de acuerdo al contrato, que tiene como estado
                # (deudor) y que se encuentran mayores a la fecha de filtro
                delete = "DELETE FROM res_partner_pagos_cliente WHERE cliente=" + str(
                    cliente) + "AND estado = 'deudor' AND fecha > '" + fecha_incio + "'"
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
                # consulta para eliminar los pagos actuales de acuerdo al contrato, que tiene como estado
                # (deudor) y que se encuentran mayores a la fecha de filtro
                delete = "DELETE FROM res_partner_pagos_cliente WHERE cliente=" + str(
                    cliente) + "AND estado = 'deudor' AND fecha > '" + fecha_incio + "'"
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
                    if int(fecha_incio[5:7]) + i == 12:
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

        elif tipo_pago == 'cancelado':
            delete = "DELETE FROM res_partner_pagos_cliente WHERE cliente=" + str(
                cliente) + "AND estado = 'deudor' AND fecha > '" + fecha_incio + "'"
            self._cr.execute(delete)

            fecha = (int(fecha_incio[0:4]), int(fecha_incio[5:7]), int(fecha_incio[-2:]))  # fecha inicial
            today = datetime.datetime.now()
            dateMonthEnd = "%s-%s-%s" % (
                today.year, 12, calendar.monthrange(today.year - 1, today.month - 1)[1])

            while int(fecha[0]) <= int(dateMonthEnd[0:4]):
                a = int(fecha_incio[0:4])
                print(a)
                # Determinar si el año es biciesto o no
                if (a % 4 == 0 and a % 100 != 0 or a % 400 == 0):
                    meses = (31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)  # tupla con cantidad de meses
                else:
                    meses = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)  # tupla con cantidad de meses
                for i in range(0, int(13 - int(fecha_incio[5:7]))):
                    suma_meses = int(fecha[1]) + i  # suponiendo cant_meses = 12, esto da 15

                    nueva_fecha = date(int(fecha[0]), int(fecha_incio[5:7]) + i, meses[(suma_meses % 12) - 1])

                    vals = \
                        {'fecha': nueva_fecha
                            , 'importe': monto_pagar
                            , 'cliente': cliente
                            , 'estado': 'cancelado'
                         }
                    self.env['res.partner.pagos_cliente'].create(vals)

                fecha = (int(fecha[0]) + 1, str(01).zfill(2), str(01).zfill(2))
                fecha_incio = "%s-%s-%s" % (int(fecha[0]), str(01).zfill(2), str(01).zfill(2))
                i = 1
                a = a + 1

            print "TIPO DE PAGO ------> " + tipo_pago


class res_partner(models.Model):
    _inherit = "res.partner"
    _inherits = {'res.partner.cuenta_corriente': 'cuentas_id'}
    workplace = fields.Char('Centro de Trabajo')
    doc_type = fields.Selection(
        string='Tipo de Documento',
        selection=(
            ('dni', 'D.N.I.'),
            ('ruc', 'R.U.C.'),
            ('passport', 'Pasaporte'),
            ('other', 'Otro'),
        ),
        default='dni',
    )
    regimen = fields.Char('Regimen')
    partida_registral = fields.Char('Partida Registral')
    nce = fields.Char('N.C.E', size=12)
    usuario = fields.Char('Usuario')
    clave = fields.Char('Clave')
    monto_pagar = fields.Char('Monto a Pagar', required=True)
    fecha_incio = fields.Date('Fecha Inicio de Contrato', required=True)
    tipo_pago = fields.Selection(
        [('quincenal', 'Quincenal'), ('mensual', 'Mensual'), ('semanal', 'Semanal'), ('diario', 'Diario'),
         ('trabajo', 'Por Trabajo'),
         ('convenio', 'Convenio')], 'Tipo de Pago', default='quincenal', required=True)
    fecha_pago = fields.Date('Fecha de Pago')
    estado = fields.Selection(
        [('deudor', 'Deudor'), ('pagado', 'Pagado')], 'Estado', default='deudor', compute='_compute_estado', store=True)
    doc_number = fields.Char('Número de Documento')
    country_id = fields.Many2one('res.country', default=lambda self: self.env[
        'res.country'].search([('name', '=', 'Perú')]))

    # # sunat
    tipo_contribuyente = fields.Char('Tipo de contribuyente')
    nombre_comercial = fields.Char('Nombre comercial')
    fecha_inscripcion = fields.Date('Fecha de inscripción')
    estado_contribuyente = fields.Selection(
        [('ACTIVO', 'ACTIVO'), ('BAJA TEMPORAL', 'BAJA TEMPORAL'), ('BAJA DEFINITIVA', 'BAJA DEFINITIVA'),
         ('BAJA DE OFICIO', 'BAJA DE OFICIO'), ('SUSPENSION TEMPORAL', 'SUSPENSION TEMPORAL')],
        'Estado del contribuyente')
    condicion_contribuyente = fields.Selection(
        [('HABIDO', 'HABIDO'), ('NO HABIDO', 'NO HABIDO'), ('NO HALLADO', 'NO HALLADO')],
        'Condición del contribuyente')

    agente_retension = fields.Boolean('Agente de Retención')
    agente_retension_apartir_del = fields.Date('A partir del')
    agente_retension_resolucion = fields.Char('Resolución')

    sistema_emision_comprobante = fields.Char('Sistema emisión comprobantes/manual')
    sistema_contabilidad = fields.Char('Sistema contabilidad')

    ultima_actualizacion_sunat = fields.Date(
        'Última actualización')
    representante_legal_ids = fields.One2many(
        'res.partner.representante_legal', inverse_name='parent_id')

    @api.multi
    def sunat_1(self):
        from sunat import sunatSelenium
        url = sunatSelenium()
        url.sunatUno(str(self.doc_number) if self.doc_number else '', str(self.usuario) if self.usuario else '',str(self.clave) if self.clave else '')

    @api.multi
    def sunat_2(self):
        from sunat import sunatSelenium
        url = sunatSelenium()
        url.sunatDos(str(self.doc_number) if self.doc_number else '', str(self.usuario) if self.usuario else '',
                     str(self.clave) if self.clave else '')

    @api.depends('estado')
    def _compute_estado(self):
        for rec in self:
            if rec.tipo_pago == 'convenio':
                self.estado = 'pagado'
                self._cr.execute(""" UPDATE res_partner SET estado=%s WHERE id=%s""",
                                 ('pagado', rec.id))
            else:
                if self.doc_number:
                    today = datetime.datetime.now()
                    hoy = "%s-%s-%s" % (today.year, today.month, today.day)
                    id = self.pool.get('res.partner.pagos_cliente').search(self.env.cr, self.env.uid,
                                                                           [('fecha', '<', str(hoy)),
                                                                            ('estado', '=', 'deudor'),
                                                                            ('cliente', '=', rec.id)])

                    if len(id) > 0:
                        self.estado = 'deudor'

                        self._cr.execute(""" UPDATE res_partner SET estado=%s WHERE id=%s""",
                                         ('deudor', rec.id))
                    else:
                        self.estado = 'pagado'
                        self._cr.execute(""" UPDATE res_partner SET estado=%s WHERE id=%s""",
                                         ('pagado', rec.id))

    # @api.onchange('monto_pagar')
    # def onchange_monto_pagar(self):
    #    add_pago_cliente(self.monto_pagar, self.tipo_pago, self.fecha_pago, self.fecha_incio)

    # @api.onchange('fecha_incio')
    # def onchange_fecha_inicio(self):
    #    self.add_pago_cliente()

    # @api.onchange('fecha_pago')
    # def onchange_fecha_pago(self):
    #    self.add_pago_cliente()

    # @api.onchange('tipo_pago')
    # def onchange_tipo_pago(self):
    #    self.add_pago_cliente()

    # @api.multi
    # def write(self, vals):
    #    self.add_pago_cliente()
    #    res = super(res_partner, self).write(vals)
    #    return res

    @api.multi
    def onchange_type(self, is_company):
        res = super(res_partner, self).onchange_type(is_company)

        if 'value' in res.keys():
            doc_type = is_company and 'ruc' or 'dni'
            res['value'].update({'doc_type': doc_type})

        return res

    @api.onchange('doc_number')
    def onchange_doc_number(self):
        # self.doc_number
        self.button_update_document()

    @api.one
    def button_update_document(self):
        if self.country_id.name == u'Perú':
            if self.doc_type and self.doc_type == 'dni' and \
                    not self.is_company:
                # self.company_type == 'person': odoo9
                if self.doc_number and len(self.doc_number) != 8:
                    raise Warning('El Dni debe tener 8 caracteres')
                else:
                    # record_ids = self.env['res.partner'].search([])
                    # for r in record_ids:
                    #     if self.doc_number and self.doc_number == r.doc_number:
                    #         raise Warning('El numero de documento ya esta registrado')
                    d = get_data_doc_number(
                        'dni', self.doc_number, format='json')
                    if not d['error']:
                        d = d['data']
                        self.name = '%s %s, %s' % (d['ape_paterno'],
                                                   d['ape_materno'],
                                                   d['nombres'])

            elif self.doc_type and self.doc_type == 'ruc' and \
                    self.is_company:
                # self.company_type == 'company':
                if self.doc_number and len(self.doc_number) != 11:
                    raise Warning('El Ruc debe tener 11 caracteres')
                else:
                    # record_ids = self.env['res.partner'].search([])
                    # for r in record_ids:
                    #     if self.doc_number and self.doc_number == r.doc_number:
                    #         raise Warning('El numero de documento ya esta registrado')
                    d = get_data_doc_number(
                        'ruc', self.doc_number, format='json')
                    # colocar esto en lugar de todo lo que estaba
                    if d['error']:
                        raise Warning('El Ruc no se encontró en SUNAT')
                        return True
                    # -------------------
                    d = d['data']
                    print (d)
                    self.name = d['nombre']
                    self.street = d['domicilio_fiscal']
                    if d['departamento'] != '':
                        self.street2 = '/'.join((d['departamento'],
                                                 d['provincia'],
                                                 d['distrito']))
                    else:
                        self.street2 = '/'.join((d['provincia'],
                                                 d['provincia'],
                                                 d['distrito']))
                    if d['departamento'] != '':
                        departamento = self.env['res.country.state'].search([['name', '=', d['departamento']]])
                    else:
                        departamento = self.env['res.country.state'].search([['name', '=', d['provincia']]])
                    provincia = self.env['res.country.state'].search([['name', '=', d['provincia']]])
                    distrito = self.env['res.country.state'].search([['name', '=', d['distrito']]])
                    self.state_id = departamento[0]
                    self.province_id = provincia[0]
                    self.district_id = distrito[0]
                    self.tipo_contribuyente = d['tipo_contribuyente']
                    self.nombre_comercial = d['nombre_comercial']
                    self.fecha_inscripcion = d['fecha_inscripcion']
                    self.estado_contribuyente = d['estado_contribuyente']
                    self.condicion_contribuyente = d['condicion_contribuyente']
                    self.agente_retension = d['agente_retencion']
                    self.agente_retension_apartir_del = d['agente_retencion_apartir_del']
                    self.agente_retension_resolucion = d['agente_retencion_resolucion']
                    self.ultima_actualizacion_sunat = d['ultima_actualizacion']
                    self.sistema_emision_comprobante = d['sistema_emision_comprobante']
                    self.sistema_contabilidad = d['sistema_contabilidad']

                    self.representante_legal_ids.unlink()
                    for t in d['representantes_legales']:
                        values = dict(
                            parent_id=self.id,
                            documento=t['documento'],
                            nro_documento=t['nro_documento'],
                            nombre=t['nombre'],
                            cargo=t['cargo'],
                            fecha_desde=t['fecha_desde'],
                        )
                        self.representante_legal_ids.create(values)

                    if d['estado_contribuyente'] == 'ACTIVO':
                        estado = 'ACTIVO'
                    elif d['estado_contribuyente'] == 'BAJA TEMPORAL':
                        estado = 'BT'
                    elif d['estado_contribuyente'] == 'BAJA DEFINITIVA':
                        estado = 'BD'
                    elif d['estado_contribuyente'] == 'BAJA DE OFICIO':
                        estado = 'BO'
                    elif d['estado_contribuyente'] == 'SUSPENSION TEMPORAL':
                        estado = 'ST'
                    else:
                        estado = ''

                    if d['condicion_contribuyente'] == 'HABIDO':
                        condicion = 'HABIDO'
                    elif d['condicion_contribuyente'] == 'NO HALLADO':
                        condicion = 'NH'
                    elif d['condicion_contribuyente'] == 'NO HABIDO':
                        condicion = 'N'
                    else:
                        condicion = ''

                    self.estado_cliente(estado, condicion)

    def estado_cliente(self, estado, condicion):
        today = datetime.datetime.now()
        id_estado = self.pool.get('res.partner.reporte_estado').search(self.env.cr, self.env.uid,
                                                                       [('parent_id', '=', self.id)])
        r_e = self.pool.get('res.partner.reporte_estado').browse(self.env.cr, self.env.uid, id_estado, context=None)
        if r_e:
            for r in r_e:
                if today.month == 1:
                    r.write({'enero_e': estado, 'enero_c': condicion})
                if today.month == 2:
                    r.write({'febrero_e': estado, 'febrero_c': condicion})
                if today.month == 3:
                    r.write({'marzo_e': estado, 'marzo_c': condicion})
                if today.month == 4:
                    r.write({'abril_e': estado, 'abril_c': condicion})
                if today.month == 5:
                    r.write({'mayo_e': estado, 'mayo_c': condicion})
                if today.month == 6:
                    r.write({'junio_e': estado, 'junio_c': condicion})
                if today.month == 7:
                    r.write({'julio_e': estado, 'julio_c': condicion})
                if today.month == 8:
                    r.write({'agosto_e': estado, 'agosto_c': condicion})
                if today.month == 9:
                    r.write({'setiembre_e': estado, 'setiembre_c': condicion})
                if today.month == 10:
                    r.write({'octubre_e': estado, 'octubre_c': condicion})
                if today.month == 11:
                    r.write({'noviembre_e': estado, 'noviembre_c': condicion})
                if today.month == 12:
                    r.write({'diciembre_e': estado, 'diciembre_c': condicion})
        else:
            if self.id:
                if today.month == 1:
                    vals = \
                        {'enero_e': estado
                            , 'enero_c': condicion
                            , 'parent_id': self.id
                         }
                if today.month == 2:
                    vals = \
                        {'febrero_e': estado
                            , 'febrero_c': condicion
                            , 'parent_id': self.id
                         }
                if today.month == 3:
                    vals = \
                        {'marzo_e': estado
                            , 'marzo_c': condicion
                            , 'parent_id': self.id
                         }
                if today.month == 4:
                    vals = \
                        {'abril_e': estado
                            , 'abril_c': condicion
                            , 'parent_id': self.id
                         }
                if today.month == 5:
                    vals = \
                        {'mayo_e': estado
                            , 'mayo_c': condicion
                            , 'parent_id': self.id
                         }
                if today.month == 6:
                    vals = \
                        {'junio_e': estado
                            , 'junio_c': condicion
                            , 'parent_id': self.id
                         }
                if today.month == 7:
                    vals = \
                        {'julio_e': estado
                            , 'julio_c': condicion
                            , 'parent_id': self.id
                         }
                if today.month == 8:
                    vals = \
                        {'agosto_e': estado
                            , 'agosto_c': condicion
                            , 'parent_id': self.id
                         }
                if today.month == 9:
                    vals = \
                        {'setiembre_e': estado
                            , 'setiembre_c': condicion
                            , 'parent_id': self.id
                         }
                if today.month == 10:
                    vals = \
                        {'octubre_e': estado
                            , 'octubre_c': condicion
                            , 'parent_id': self.id
                         }
                if today.month == 11:
                    vals = \
                        {'noviembre_e': estado
                            , 'noviembre_c': condicion
                            , 'parent_id': self.id
                         }
                if today.month == 12:
                    vals = \
                        {'diciembre_e': estado
                            , 'diciembre_c': condicion
                            , 'parent_id': self.id
                         }
                self.env['res.partner.reporte_estado'].create(vals)

    @api.multi
    def load_pantalla_historico(self):
        id = self.pool.get('ir.ui.view').search(self.env.cr, self.env.uid,
                                                [('model', '=', 'res.partner.historia_clinica'),
                                                 ('type', '=', 'form')])

        existeEspecifica = self.pool.get('res.partner.historia_clinica').search(self.env.cr, self.env.uid,
                                                                                [('parent_id', '=',
                                                                                  self.id)])

        course_form = self.pool.get('ir.ui.view').browse(self.env.cr, self.env.uid, id[0], context=None)

        ctx = dict(
            default_parent_id=self.id,
        )

        if existeEspecifica:
            return {
                'name': 'Historia Clínica Contable',
                'type': 'ir.actions.act_window',
                'res_model': 'res.partner.historia_clinica',
                # 'res_id': existeEspecifica[0],
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'views': [(course_form.id, 'form')],
                'view_id': course_form.id,
                'flags': {'action_buttons': True},
                'context': ctx,
            }
        else:
            return {
                'name': 'Historia Clínica Contable',
                'type': 'ir.actions.act_window',
                'res_model': 'res.partner.historia_clinica',
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'views': [(course_form.id, 'form')],
                'view_id': course_form.id,
                'flags': {'action_buttons': True},
                'context': ctx,
            }

    @api.multi
    def load_pantalla_impuestos_pendientes(self):
        print " - - - -  PANTALLA DE INPUESTOS PENDEIENTES - -- --- "
        today = datetime.datetime.now()
        id = self.pool.get('ir.ui.view').search(self.env.cr, self.env.uid,
                                                [('model', '=', 'res.partner.impuestos_pendientes'),
                                                 ('type', '=', 'form')])

        existe = self.pool.get('res.partner.impuestos_pendientes').search(self.env.cr, self.env.uid,
                                                                          [('parent_id', '=',
                                                                            self.id), ('anio', '=', str(today.year))]) # cambio acaaaaaaaaaaaaa 25/05/2017 , ('anio', '=', str(today.year)

        course_form = self.pool.get('ir.ui.view').browse(self.env.cr, self.env.uid, id[0], context=None)

        today = datetime.datetime.now()

        existeReportePagosAnio = self.pool.get('res.partner.reporte_pagos').search(self.env.cr, self.env.uid,
                                                                                   [('name', '=',
                                                                                     today.year)])

        if existeReportePagosAnio:
            parent = self.pool.get('res.partner.reporte_pagos').browse(self.env.cr, self.env.uid,
                                                                       existeReportePagosAnio,
                                                                       context=None).id
        else:
            vals = \
                {'name': today.year
                 }
            parent = self.pool.get('res.partner.reporte_pagos').create(self.env.cr, self.env.uid, vals,
                                                                       context=None)

        existeReporteImp = self.pool.get('res.partner.reporte_pagos').search(self.env.cr, self.env.uid,
                                                                             [('cliente', '=',
                                                                               self.id), ('parent_id', '=',
                                                                                          parent)])

        if existeReporteImp:
            print "Existe  3"
        else:
            vals = \
                {'cliente': self.id,
                 'parent_id': parent
                 }
            self.pool.get('res.partner.reporte_pagos').create(self.env.cr, self.env.uid, vals, context=None)

        ctx = dict(
            default_parent_id=self.id,
        )

        if existe:
            self.createDetalleImpuestos()
            return {
                'name': 'Impuestos Pendientes',
                'type': 'ir.actions.act_window',
                'res_model': 'res.partner.impuestos_pendientes',
                'res_id': existe[0],
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'views': [(course_form.id, 'form')],
                'view_id': course_form.id,
                'flags': {'action_buttons': True},
                'context': ctx,
            }
        else:
            today = datetime.datetime.now()
            vals = \
                {'parent_id': self.id
                 }
            ctx = dict(
                anio=today.year,
                mes=today.month,
            )
            res_id = self.pool.get('res.partner.impuestos_pendientes').create(self.env.cr, self.env.uid, vals,
                                                                              context=ctx)
            self.createDetalleImpuestos()
            return {
                'name': 'Impuestos Pendientes',
                'type': 'ir.actions.act_window',
                'res_model': 'res.partner.impuestos_pendientes',
                'res_id': res_id,
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'views': [(course_form.id, 'form')],
                'view_id': course_form.id,
                'flags': {'action_buttons': True},
                'context': ctx,
            }

    def createDetalleImpuestos(self):
        today = datetime.datetime.now()
        existe = self.pool.get('res.partner.impuestos_pendientes').search(self.env.cr, self.env.uid,
                                                                          [('parent_id', '=',self.id), ('anio', '=', str(today.year))]) # cambio acaaaaaaaaaaaaa 25/05/2017  , ('anio', '=', str(today.year)
        impuesto = self.pool.get('res.partner.impuestos_pendientes').browse(self.env.cr, self.env.uid, existe,
                                                                            context=None)

        existeDetalle = self.pool.get('res.partner.impuestos_pendientes_detalle').search(self.env.cr, self.env.uid,
                                                                                         [('parent_detalle_id', '=',
                                                                                           impuesto.impuesto_pendiente_detalle_id.id)])

        detalle_impuesto = self.pool.get('res.partner.impuestos_pendientes_detalle').browse(self.env.cr, self.env.uid,
                                                                                            existeDetalle, context=None)

        if detalle_impuesto:
            print "Existe"
        else:
            for i in range(1, 13, 1):
                self.createDetalleImpuesto(i, impuesto.impuesto_pendiente_detalle_id.id)

    def createDetalleImpuesto(self, mes, detalle):
        today = datetime.datetime.now()
        vals = \
            {'mes': str(mes),
             'anio': str(today.year),
             'impuesto': 'IGV',
             'parent_detalle_id': detalle
             }
        self.pool.get('res.partner.impuestos_pendientes_detalle').create(self.env.cr, self.env.uid, vals, context=None)
        vals = \
            {'mes': str(mes),
             'anio': str(today.year),
             'impuesto': 'RENTA',
             'parent_detalle_id': detalle
             }
        self.pool.get('res.partner.impuestos_pendientes_detalle').create(self.env.cr, self.env.uid, vals, context=None)
        vals = \
            {'mes': str(mes),
             'anio': str(today.year),
             'impuesto': 'ESSALUD',
             'parent_detalle_id': detalle
             }
        self.pool.get('res.partner.impuestos_pendientes_detalle').create(self.env.cr, self.env.uid, vals, context=None)
        vals = \
            {'mes': str(mes),
             'anio': str(today.year),
             'impuesto': 'AFP',
             'parent_detalle_id': detalle
             }
        self.pool.get('res.partner.impuestos_pendientes_detalle').create(self.env.cr, self.env.uid, vals, context=None)
        vals = \
            {'mes': str(mes),
             'anio': str(today.year),
             'impuesto': 'ONP',
             'parent_detalle_id': detalle
             }
        self.pool.get('res.partner.impuestos_pendientes_detalle').create(self.env.cr, self.env.uid, vals, context=None)
        vals = \
            {'mes': str(mes),
             'anio': str(today.year),
             'impuesto': 'SIS O SYS',
             'parent_detalle_id': detalle
             }
        self.pool.get('res.partner.impuestos_pendientes_detalle').create(self.env.cr, self.env.uid, vals, context=None)

    @api.multi
    def load_pantalla_declaraciones(self):
        id = self.pool.get('ir.ui.view').search(self.env.cr, self.env.uid,
                                                [('model', '=', 'res.partner.declaraciones'),
                                                 ('type', '=', 'form')])

        existe = self.pool.get('res.partner.declaraciones').search(self.env.cr, self.env.uid,
                                                                   [('parent_id', '=',
                                                                     self.id)])

        course_form = self.pool.get('ir.ui.view').browse(self.env.cr, self.env.uid, id[0], context=None)

        existeReporteHonorario = self.pool.get('res.partner.reporte_declaracion').search(self.env.cr, self.env.uid,
                                                                                         [('parent_id', '=',
                                                                                           self.id)])
        if existeReporteHonorario:
            print "Existe Reporte 4"
        else:
            vals = \
                {'parent_id': self.id
                 }
            self.pool.get('res.partner.reporte_declaracion').create(self.env.cr, self.env.uid, vals, context=None)

        ctx = dict(
            default_parent_id=self.id,
        )

        if existe:
            return {
                'name': 'Declaraciones',
                'type': 'ir.actions.act_window',
                'res_model': 'res.partner.declaraciones',
                'res_id': existe[0],
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'views': [(course_form.id, 'form')],
                'view_id': course_form.id,
                'flags': {'action_buttons': True},
                'context': ctx,
            }
        else:
            return {
                'name': 'Declaraciones',
                'type': 'ir.actions.act_window',
                'res_model': 'res.partner.declaraciones',
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'views': [(course_form.id, 'form')],
                'view_id': course_form.id,
                'flags': {'action_buttons': True},
                'context': ctx,
            }

    # @api.model
    # def create(self, vals):
    #     record_ids = self.env['res.partner'].search([['customer','=',True],['active','=',True]])
    #     print (record_ids)
    #     for r in record_ids:
    #         print (r.doc_number)
    #         if 'doc_number' in vals:
    #             if vals['doc_number'] and vals['doc_number'] == r.doc_number:
    #                 raise Warning('El numero de documento ya esta registrado')
    #             else:
    #                 return super(res_partner, self).create(vals)
    #         else:
    #             return super(res_partner, self).create(vals)

    @api.multi
    def write_fechas(self, vals, context=None):
        if vals.has_key('fecha_incio'):
            fecha_incio = vals['fecha_incio']
        else:
            fecha_incio = self.fecha_incio

        if vals.has_key('tipo_pago'):
            tipo_pago = vals['tipo_pago']
        else:
            tipo_pago = self.tipo_pago
        if fecha_incio:
            self._cr.execute(
                """SELECT COUNT(id) FROM res_partner_pagos_cliente WHERE estado = %s and fecha >= %s and cliente = %s""",
                ('pagado', fecha_incio, self.id))
            count_ids = self._cr.fetchone()[0]
            if count_ids > 0:
                raise except_orm(_('Error!'), _("Hay Cuotas en fechas posteriores porfavor registre otra fecha!!"))
            else:
                if fecha_incio or tipo_pago:
                    add_pago_cliente(self, self.monto_pagar, tipo_pago,
                                     self.fecha_pago, fecha_incio, self.id, 'act')

        return super(res_partner, self).write(vals)

    # eliminar datos de la tabla
    @api.multi
    def unlink(self):

        print ("Id DE PAGO", self.id)

        self._cr.execute(""" DELETE FROM res_partner_reporte_honorarios WHERE parent_id = %s""", [self.id])
        self._cr.execute(""" DELETE FROM res_partner_reporte_pagos WHERE cliente = %s""", [self.id])
        self._cr.execute(""" DELETE FROM res_partner_reporte_estado WHERE parent_id = %s""", [self.id])
        self._cr.execute(""" DELETE FROM res_partner_reporte_documentos WHERE cliente = %s""", [self.id])
        self._cr.execute(""" DELETE FROM res_partner_reporte_declaracion WHERE parent_id = %s""", [self.id])
        self._cr.execute(""" DELETE FROM res_partner_historia_clinica_catalogo_meses WHERE cliente = %s""", [self.id])
        self._cr.execute(""" DELETE FROM res_partner_pagos_cliente WHERE cliente = %s""", [self.id])
        # self._cr.execute(""" DELETE FROM res_partner_declaraciones WHERE parent_id = %s""", [self.id])
        return super(res_partner, self).unlink()

    @api.multi
    def load_pantalla_honorarios(self):
        # print (self.fecha_incio)
        contrato = self.env['res.cliente.contrato'].search([('partner_id', '=', self.id)], limit=1, order="id desc")

        id = self.pool.get('ir.ui.view').search(self.env.cr, self.env.uid,
                                                [('model', '=', 'res.partner.honorarios'),
                                                 ('type', '=', 'form')])

        existe = self.pool.get('res.partner.honorarios').search(self.env.cr, self.env.uid,
                                                                [('parent_id', '=',
                                                                  self.id)])

        course_form = self.pool.get('ir.ui.view').browse(self.env.cr, self.env.uid, id[0], context=None)

        id = self.pool.get('res.partner.pagos_cliente').search(self.env.cr, self.env.uid,
                                                               [('cliente', '=', self.id)])

        if len(id) == 0:
            add_pago_cliente(self, contrato.monto_pagar, contrato.tipo_pago,
                             contrato.fecha_pago, contrato.fecha_inicio, self.id, 'crear')
        else:
            add_pago_cliente(self, contrato.monto_pagar, contrato.tipo_pago,
                             contrato.fecha_pago, contrato.fecha_inicio, self.id, 'update')

        existeReporteHonorario = self.pool.get('res.partner.reporte_honorarios').search(self.env.cr, self.env.uid,
                                                                                        [('parent_id', '=',
                                                                                          self.id)])
        if existeReporteHonorario:
            print "Existe Reporte 1"
        else:
            vals = \
                {'parent_id': self.id
                 }
            self.pool.get('res.partner.reporte_honorarios').create(self.env.cr, self.env.uid, vals, context=None)

        ctx = dict(
            default_parent_id=self.id,
            default_importe_pagado=contrato.monto_pagar,
            default_fecha=contrato.fecha_inicio,
            default_tipo=contrato.tipo_pago,
            default_fecha_pago=contrato.fecha_pago,
        )

        if existe:
            return {
                'name': 'Honorarios',
                'type': 'ir.actions.act_window',
                'res_model': 'res.partner.honorarios',
                'res_id': existe[0],
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'views': [(course_form.id, 'form')],
                'view_id': course_form.id,
                'flags': {'action_buttons': True},
                'context': ctx,
            }
        else:
            vals = \
                {'parent_id': self.id
                 }
            res_id = self.pool.get('res.partner.honorarios').create(self.env.cr, self.env.uid, vals, context=None)
            return {
                'name': 'Honorarios',
                'type': 'ir.actions.act_window',
                'res_model': 'res.partner.honorarios',
                'res_id': res_id,
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'views': [(course_form.id, 'form')],
                'view_id': course_form.id,
                'flags': {'action_buttons': True},
                'context': ctx,
            }

    @api.multi
    def load_pantalla_documentos(self):
        id = self.pool.get('ir.ui.view').search(self.env.cr, self.env.uid,
                                                [('model', '=', 'res.partner.documentos'),
                                                 ('type', '=', 'form')])

        existe = self.pool.get('res.partner.documentos').search(self.env.cr, self.env.uid,
                                                                [('parent_id', '=',
                                                                  self.id)])

        course_form = self.pool.get('ir.ui.view').browse(self.env.cr, self.env.uid, id[0], context=None)

        today = datetime.datetime.now()

        existeReporteHonorarioAnio = self.pool.get('res.partner.reporte_documentos').search(self.env.cr, self.env.uid,
                                                                                            [('name', '=',
                                                                                              today.year)])
        if existeReporteHonorarioAnio:
            parent = self.pool.get('ir.ui.view').browse(self.env.cr, self.env.uid, existeReporteHonorarioAnio,
                                                        context=None).id
        else:
            vals = \
                {'name': today.year
                 }
            parent = self.pool.get('res.partner.reporte_documentos').create(self.env.cr, self.env.uid, vals,
                                                                            context=None)

        existeReporteHonorario = self.pool.get('res.partner.reporte_documentos').search(self.env.cr, self.env.uid,
                                                                                        [('cliente', '=',
                                                                                          self.id), ('parent_id', '=',
                                                                                                     parent)])
        if existeReporteHonorario:
            print "Existe Reporte 2"
        else:
            vals = \
                {'cliente': self.id,
                 'parent_id': parent
                 }
            self.pool.get('res.partner.reporte_documentos').create(self.env.cr, self.env.uid, vals, context=None)

        ctx = dict(
            default_parent_id=self.id,
        )

        if existe:
            return {
                'name': 'Recepción y Adjunto de documentos',
                'type': 'ir.actions.act_window',
                'res_model': 'res.partner.documentos',
                'res_id': existe[0],
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'views': [(course_form.id, 'form')],
                'view_id': course_form.id,
                'flags': {'action_buttons': True},
                'context': ctx,
            }
        else:
            return {
                'name': 'Recepción y Adjunto de documentos',
                'type': 'ir.actions.act_window',
                'res_model': 'res.partner.documentos',
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'views': [(course_form.id, 'form')],
                'view_id': course_form.id,
                'flags': {'action_buttons': True},
                'context': ctx,
            }

    # @api.multi
    # def button_method(self):
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'form name',
    #         'res_model': 'object name',
    #         'res_id': id,
    #         'view_type': 'form',
    #         'view_mode': 'form',
    #         'target': 'new',
    #     }


class res_partner_representante_legal(models.Model):
    _name = 'res.partner.representante_legal'
    _rec_name = 'nombre'

    parent_id = fields.Many2one('res.partner', readonly=True)
    documento = fields.Char('Documento', readonly=True)
    nro_documento = fields.Char('Número', readonly=True)
    nombre = fields.Char('Nombre', readonly=True)
    cargo = fields.Char('Cargo', readonly=True)
    fecha_desde = fields.Date('Cargo desde', readonly=True)


class res_partner_historia_clinica(models.Model):

    def _mes_get_fnc_historia(self):
        today = datetime.datetime.now()
        return str(today.month)

    """MOSTRAR RAGO DE 20 AÑOS"""

    def get_rango_anios_historia(self):
        today = datetime.datetime.now()
        lst = []
        for i in range(5, 0, -1):
            lst.append((str(today.year + i), str(today.year + i)))
        for i in range(0, 16):
            lst.append((str(today.year - i), str(today.year - i)))
        return lst

    """CARGAR AÑO ACTUAL POR DEFECTO"""

    def _anio_get_fnc_historia(self):
        today = datetime.datetime.now()
        return str(today.year)

    _name = 'res.partner.historia_clinica'
    _inherits = {'res.partner.historia_clinica_detalle': 'historia_clinica_detalle_id'}
    _rec_name = 'parent_id'
    parent_id = fields.Many2one('res.partner', readonly=True)

    anio = fields.Selection(get_rango_anios_historia, 'Año de Recepción', default=_anio_get_fnc_historia)
    mes = fields.Selection(
        [('1', 'Enero'), ('2', 'Febrero'), ('3', 'Marzo'), ('4', 'Abril'), ('5', 'Mayo'), ('6', 'Junio'),
         ('7', 'Julio'), ('8', 'Agosto'), ('9', 'Setiembre'), ('10', 'Octubre'), ('11', 'Noviembre'),
         ('12', 'Diciembre')], 'Mes de Recepción', default=_mes_get_fnc_historia)

    parent_catalogo_ids = fields.One2many(comodel_name="res.partner.historia_clinica_catalogo_meses",
                                          inverse_name="parent_catalogo_id", string="Historia por meses",
                                          compute='dep_mes_cata', store=True, readonly=False)

    @api.depends('mes')
    def dep_mes_cata(self):
        # print ('dsfdfdfdfghhhhhhhhh')
        self.mostrarImpuestos()

    @api.onchange('mes')
    def check_change_mes(self):
        self.mostrarImpuestos()

    def mostrarImpuestos(self):

        idImp = self.pool.get('res.partner.historia_clinica').search(self.env.cr, self.env.uid,
                                                                     [('parent_id', '=', self.parent_id.id)])
        imp = self.pool.get('res.partner.historia_clinica').browse(self.env.cr, self.env.uid, idImp, context=None)
        id = self.pool.get('res.partner.historia_clinica_catalogo_meses').search(self.env.cr, self.env.uid,
                                                                                 [('mes', '=', self.mes),
                                                                                  ('anio', '=', self.anio),
                                                                                  ('cliente', '=', self.parent_id.id)])
        impuestos = self.pool.get('res.partner.historia_clinica_catalogo_meses').browse(self.env.cr, self.env.uid, id,
                                                                                        context=None)
        self.parent_catalogo_ids = impuestos


class res_partner_historia_clinica_detalle(models.Model):

    def _mes_get_fnc_historia(self):
        today = datetime.datetime.now()
        if self._context.get('mes'):
            return str(self._context.get('mes'))
        else:
            return str(today.month)

    """MOSTRAR RAGO DE 20 AÑOS"""

    def get_rango_anios_historia(self):
        today = datetime.datetime.now()
        lst = []
        for i in range(5, 0, -1):
            lst.append((str(today.year + i), str(today.year + i)))
        for i in range(0, 16):
            lst.append((str(today.year - i), str(today.year - i)))
        return lst

    """CARGAR AÑO ACTUAL POR DEFECTO"""

    def _anio_get_fnc_historia(self):
        print (self._context)
        today = datetime.datetime.now()
        if self._context.get('anio'):
            return str(self._context.get('anio'))
        else:
            return str(today.year)

    @api.model
    def create(self, vals, context=None):
        new_id = super(res_partner_historia_clinica_detalle, self).create(vals)
        new_object = self.env['res.partner.historia_clinica_detalle'].browse(new_id.id)
        print (self._context)
        if vals.has_key('anio') and vals.has_key('fecha') and vals.has_key('mes') and vals.has_key(
                'historico') and vals.has_key('estado'):
            valores = {
                'anio': vals['anio'],
                'fecha': vals['fecha'],
                'mes': vals['mes'],
                'historico': vals['historico'],
                'estado': vals['estado'],
                'cliente': self._context.get('active_id'),
            }
            print (valores)
            self.env['res.partner.historia_clinica_catalogo_meses'].create(valores)
        return new_id

    _name = 'res.partner.historia_clinica_detalle'
    fecha = fields.Date('Fecha Registro')
    estado = fields.Selection(
        [('pendiente', 'Pendiente'), ('solucionado', 'Solucionado')], 'Estado', default='pendiente')
    historico = fields.Char('Suceso')
    parent_detalle_id = fields.Many2one('res.partner.historia_clinica_detalle', 'Parent')
    historia_clinica_detalle_ids = fields.One2many('res.partner.historia_clinica_detalle', 'parent_detalle_id',
                                                   'Included Services')

    anio = fields.Selection(get_rango_anios_historia, 'Año de Recepción', default=_anio_get_fnc_historia)
    mes = fields.Selection(
        [('1', 'Enero'), ('2', 'Febrero'), ('3', 'Marzo'), ('4', 'Abril'), ('5', 'Mayo'), ('6', 'Junio'),
         ('7', 'Julio'), ('8', 'Agosto'), ('9', 'Setiembre'), ('10', 'Octubre'), ('11', 'Noviembre'),
         ('12', 'Diciembre')], 'Mes de Recepción', default=_mes_get_fnc_historia)


class res_partner_historia_clinica_catalogo_meses(models.Model):
    _name = 'res.partner.historia_clinica_catalogo_meses'
    _rec_name = "cliente"

    fecha = fields.Date('Fecha Registro')
    estado = fields.Selection(
        [('pendiente', 'Pendiente'), ('solucionado', 'Solucionado')], 'Estado')
    historico = fields.Char('Suceso')
    parent_catalogo_id = fields.Many2one('res.partner.historia_clinica', 'Parent')
    anio = fields.Char('Año de Recepción')
    mes = fields.Selection(
        [('1', 'Enero'), ('2', 'Febrero'), ('3', 'Marzo'), ('4', 'Abril'), ('5', 'Mayo'), ('6', 'Junio'),
         ('7', 'Julio'), ('8', 'Agosto'), ('9', 'Setiembre'), ('10', 'Octubre'), ('11', 'Noviembre'),
         ('12', 'Diciembre')], 'Mes de Recepción')
    cliente = fields.Many2one('res.partner')


class res_partner_impuestos_pendientes(models.Model):
    """CARGAR MES ACTUAL POR DEFECTO"""

    def _mes_get_fnc(self):
        today = datetime.datetime.now()
        return str(today.month)

    """MOSTRAR RAGO DE 20 AÑOS"""

    def get_rango_anios(self):
        today = datetime.datetime.now()
        lst = []
        for i in range(5, 0, -1):
            lst.append((str(today.year + i), str(today.year + i)))
        for i in range(0, 16):
            lst.append((str(today.year - i), str(today.year - i)))
        return lst

    """CARGAR AÑO ACTUAL POR DEFECTO"""

    def _anio_get_fnc(self):
        today = datetime.datetime.now()
        return str(today.year)

    def _compute_fecha(self):
        self.mostrarImpuestos()

    _name = 'res.partner.impuestos_pendientes'
    _inherits = {'res.partner.impuestos_pendientes_detalle': 'impuesto_pendiente_detalle_id'}
    _rec_name = 'parent_id'
    parent_id = fields.Many2one('res.partner', readonly=True)
    fecha = fields.Date('Fecha Registro', compute="_compute_fecha")
    mes = fields.Selection(
        [('1', 'Enero'), ('2', 'Febrero'), ('3', 'Marzo'), ('4', 'Abril'), ('5', 'Mayo'), ('6', 'Junio'),
         ('7', 'Julio'), ('8', 'Agosto'), ('9', 'Setiembre'), ('10', 'Octubre'), ('11', 'Noviembre'),
         ('12', 'Diciembre')], 'Mes', default=_mes_get_fnc)
    anio = fields.Selection(get_rango_anios, 'Año', default=_anio_get_fnc)

    @api.onchange('mes', 'anio')
    def check_change_mes(self):
        self.mostrarImpuestos()

    def mostrarImpuestos(self):
        print "- - - - Mostrar Impuestos - - - -"
        idImp = self.pool.get('res.partner.impuestos_pendientes').search(self.env.cr, self.env.uid,
                                                                         [('parent_id', '=',
                                                                           self.parent_id.id), ('anio', '=', self.anio)]) # cambio acaaaaaaaaaaaaa 25/05/2017 , ('anio', '=', self.anio)

        imp = self.pool.get('res.partner.impuestos_pendientes').browse(self.env.cr, self.env.uid, idImp,
                                                                       context=None)

        id = self.pool.get('res.partner.impuestos_pendientes_detalle').search(self.env.cr, self.env.uid,
                                                                              [('mes', '=', self.mes),
                                                                               ('anio', '=', self.anio),
                                                                               ('parent_detalle_id', '=',
                                                                                imp.impuesto_pendiente_detalle_id.id)])

        impuestos = self.pool.get('res.partner.impuestos_pendientes_detalle').browse(self.env.cr, self.env.uid, id,
                                                                                     context=None)
        self.impuesto_pendiente_detalle_ids = impuestos


class res_partner_impuestos_pendientes_detalle(models.Model):
    def _mes_get_fnc(self):
        print "- - - - Mostrar Impuestos funcion - - - -"
        return str(self._context.get('mes'))

    """MOSTRAR RAGO DE 20 AÑOS"""

    def get_rango_anios(self):
        today = datetime.datetime.now()
        lst = []
        for i in range(5, 0, -1):
            lst.append((str(today.year + i), str(today.year + i)))
        for i in range(0, 16):
            lst.append((str(today.year - i), str(today.year - i)))
        return lst

    """CARGAR AÑO ACTUAL POR DEFECTO"""

    def _anio_get_fnc(self):
        return str(self._context.get('anio'))

    _name = 'res.partner.impuestos_pendientes_detalle'
    fecha = fields.Date('Fecha')
    impuesto = fields.Char('Nom. Impuesto')
    deuda = fields.Float('Deuda')
    parent_detalle_id = fields.Many2one('res.partner.impuestos_pendientes_detalle', 'Parent')
    impuesto_pendiente_detalle_ids = fields.One2many('res.partner.impuestos_pendientes_detalle', 'parent_detalle_id',
                                                     'Included Services')
    mes = fields.Selection(
        [('1', 'Enero'), ('2', 'Febrero'), ('3', 'Marzo'), ('4', 'Abril'), ('5', 'Mayo'), ('6', 'Junio'),
         ('7', 'Julio'), ('8', 'Agosto'), ('9', 'Setiembre'), ('10', 'Octubre'), ('11', 'Noviembre'),
         ('12', 'Diciembre')], 'Mes', default=_mes_get_fnc)
    anio = fields.Selection(get_rango_anios, 'Año', default=_anio_get_fnc)

    @api.multi
    def write(self, vals):
        for val in vals['impuesto_pendiente_detalle_ids']:
            if val[2]:
                valores = val[2]
                for item in valores.keys():
                    if item == 'fecha':
                        upd = "UPDATE res_partner_impuestos_pendientes_detalle SET fecha='" + str(
                            valores['fecha']) + "' WHERE id = " + str(val[1])
                        self._cr.execute(upd)
                    elif item == 'deuda':
                        upd = "UPDATE res_partner_impuestos_pendientes_detalle SET deuda=" + str(
                            valores['deuda']) + " WHERE id =" + str(val[1])
                        self._cr.execute(upd)


def get_fecha_limite(self, mes, anio, cliente):
    ruc = self.pool.get('res.partner').browse(self.env.cr, self.env.uid, cliente, context=None)

    id = self.pool.get('res.partner.cronograma_obligaciones').search(self.env.cr, self.env.uid,
                                                                     [('mes', '=', mes), ('anio', '=', anio)])
    for i in id:
        cronograma = self.pool.get('res.partner.cronograma_obligaciones').browse(self.env.cr, self.env.uid, i,
                                                                                 context=None)
        dig = cronograma.digito.split(',')
        for j in dig:
            if j == ruc.doc_number[-1]:
                return cronograma.fecha_vencimiento


class res_partner_declaraciones(models.Model):
    _name = 'res.partner.declaraciones'
    _inherits = {'res.partner.declaraciones_detalle': 'declaraciones_id'}
    _rec_name = 'parent_id'
    parent_id = fields.Many2one('res.partner', readonly=True)


class res_partner_declaraciones_detalle(models.Model):
    """CARGAR MES ACTUAL POR DEFECTO"""

    def _mes_get_fnc(self):
        today = datetime.datetime.now()
        return str(today.month)

    """MOSTRAR RAGO DE 20 AÑOS"""

    def get_rango_anios(self):
        today = datetime.datetime.now()
        lst = []
        for i in range(5, 0, -1):
            lst.append((str(today.year + i), str(today.year + i)))
        for i in range(0, 16):
            lst.append((str(today.year - i), str(today.year - i)))
        return lst

    """CARGAR AÑO ACTUAL POR DEFECTO"""

    def _anio_get_fnc(self):
        today = datetime.datetime.now()
        return str(today.year)

    _name = 'res.partner.declaraciones_detalle'
    mes = fields.Selection(
        [('1', 'Enero'), ('2', 'Febrero'), ('3', 'Marzo'), ('4', 'Abril'), ('5', 'Mayo'), ('6', 'Junio'),
         ('7', 'Julio'), ('8', 'Agosto'), ('9', 'Setiembre'), ('10', 'Octubre'), ('11', 'Noviembre'),
         ('12', 'Diciembre')], 'Mes', default=_mes_get_fnc)
    anio = fields.Selection(get_rango_anios, 'Año', default=_anio_get_fnc)
    fecha_pdt = fields.Date('Fecha Declarada PDT')
    fecha_limite = fields.Date('Fecha Límite')
    fecha_declarada = fields.Date('Fecha Declarada PLAME')
    observaciones = fields.Text('Observaciones')
    parent_detalle_id = fields.Many2one('res.partner.declaraciones_detalle', 'Parent')
    declaraciones_ids = fields.One2many('res.partner.declaraciones_detalle', 'parent_detalle_id', 'Included Services')

    @api.onchange('mes')
    def check_change_mes(self):
        self.fecha_limite = get_fecha_limite(self, self.mes, self.anio, self._context.get('cliente'))

    @api.onchange('anio')
    def check_change_anio(self):
        self.fecha_limite = get_fecha_limite(self, self.mes, self.anio, self._context.get('cliente'))


class res_partner_honorarios(models.Model):
    """CARGAR MES ACTUAL POR DEFECTO"""

    def _mesh_get_fnc(self):
        # self.mostrarCronograma()
        today = datetime.datetime.now()
        return str(today.month)

    """MOSTRAR RANGO DE 20 AÑOS"""

    def get_rango_aniosh(self):
        today = datetime.datetime.now()
        lst = []
        for i in range(5, 0, -1):
            lst.append((str(today.year + i), str(today.year + i)))
        for i in range(0, 16):
            lst.append((str(today.year - i), str(today.year - i)))
        return lst

    """CARGAR AÑO ACTUAL POR DEFECTO"""

    def _anioh_get_fnc(self):
        today = datetime.datetime.now()
        return str(today.year)

    _name = 'res.partner.honorarios'
    # _inherits = {'res.partner.honorarios_detalle': 'honorarios_detalle_id'}
    _rec_name = 'parent_id'
    parent_id = fields.Many2one('res.partner', readonly=True)
    mes = fields.Selection(
        [('1', 'Enero'), ('2', 'Febrero'), ('3', 'Marzo'), ('4', 'Abril'), ('5', 'Mayo'), ('6', 'Junio'),
         ('7', 'Julio'), ('8', 'Agosto'), ('9', 'Setiembre'), ('10', 'Octubre'), ('11', 'Noviembre'),
         ('12', 'Diciembre')], 'Mes Honorarios', default=_mesh_get_fnc)
    anio = fields.Selection(get_rango_aniosh, 'Año Honorarios', default=_anioh_get_fnc)
    importe_tot_pagado = fields.Float('Importe a Pagar', compute='_compute_tot_pagado')
    importe_deuda = fields.Float('Importe Deuda', compute='_compute_duda', store=True)
    importe_pagado = fields.Float('Importe Pagado', compute='_compute_pagado')
    pago_ids = fields.One2many('res.partner.pagos_cliente', 'pago_id', compute='_compute_pagos')

    honorarios_detalle_ids = fields.One2many('res.partner.honorarios_detalle', 'parent_detalle_id', 'Included Services')

    # DATOS DE LOS IMPORTES PAGADOS
    @api.depends('mes', 'anio')
    def _compute_tot_pagado(self):
        a = int(self.anio)
        if (a % 4 == 0 and a % 100 != 0 or a % 400 == 0):
            meses = (31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)  # tupla con cantidad de meses
        else:
            meses = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)  # tupla con cantidad de meses
        nueva_inicio = date(int(self.anio), int(self.mes), 1)
        nueva_fin = date(int(self.anio), int(self.mes), meses[int(self.mes) - 1])
        id = self.pool.get('res.partner.pagos_cliente').search(self.env.cr, self.env.uid,
                                                               [('fecha', '>=', str(nueva_inicio)),
                                                                ('fecha', '<=', str(nueva_fin)),
                                                                ('cliente', '=',
                                                                 self._context.get('default_parent_id'))])
        pagos_c = self.pool.get('res.partner.pagos_cliente').browse(self.env.cr, self.env.uid, id, context=None)

        # TABLA DE LOS IMPORTES PAGADOS
        self.mostrarCronograma()
        monto = 0
        # add_pago_cliente(self, monto_pagar, tipo_pago, fecha_pago, fecha_incio, cliente, est):
        for c in pagos_c:
            if c.importe != float(self._context.get('default_importe_pagado')):
                # add_pago_cliente(self, self._context.get('default_importe_pagado'),
                #                  self._context.get('default_tipo'),
                #                  self._context.get('default_fecha_pago'),
                #                  self._context.get('default_fecha'),
                #                  self._context.get('default_parent_id'),
                #                  'pago')
                # monto = monto + float(self._context.get('default_importe_pagado'))
                monto += c.importe
            else:
                monto += c.importe

        self.importe_tot_pagado = monto

    @api.depends('mes', 'anio')
    def _compute_duda(self):
        if self.importe_tot_pagado - self.importe_pagado >= 0:
            self.importe_deuda = self.importe_tot_pagado - self.importe_pagado
        else:
            today = datetime.datetime.now()
            fecha = date(today.year, today.month, today.day)
            id = self.pool.get('res.partner.honorarios_detalle').search(self.env.cr, self.env.uid,
                                                                        [('mes', '=', self.mes),
                                                                         ('anio', '=', self.anio),
                                                                         ('parent_detalle_id', '=',
                                                                          self.id)])

            pagos_honorarios = self.pool.get('res.partner.honorarios_detalle').browse(self.env.cr, self.env.uid, id,
                                                                                      context=None)
            contador = 1
            for h in pagos_honorarios:
                if contador == len(pagos_honorarios):
                    importe = h.importe_pagado + self.importe_tot_pagado - self.importe_pagado
                    h.write({'importe_pagado': importe})
                contador = contador + 1

            vals = \
                {'fecha_pago': fecha
                    , 'mes': str(int(self.mes) + 1)
                    , 'anio': self.anio
                    , 'importe_pagado': (self.importe_tot_pagado - self.importe_pagado) * -1
                    , 'parent_detalle_id': self.id
                 }
            self.env['res.partner.honorarios_detalle'].create(vals)
            self.importe_deuda = 0

    @api.depends('mes', 'anio')
    def _compute_pagado(self):
        monto = 0
        if self.id:
            id = self.pool.get('res.partner.honorarios_detalle').search(self.env.cr, self.env.uid,
                                                                        [('mes', '=', self.mes),
                                                                         ('anio', '=', self.anio),
                                                                         ('parent_detalle_id', '=',
                                                                          self.id)])
        else:
            hon = self.pool.get('res.partner.honorarios').search(self.env.cr, self.env.uid,
                                                                 [('parent_id', '=',
                                                                   int(self._context.get('default_parent_id')))])[0]

            honorario = self.pool.get('res.partner.honorarios').browse(self.env.cr, self.env.uid, hon,
                                                                       context=None)
            for h in honorario:
                id = self.pool.get('res.partner.honorarios_detalle').search(self.env.cr, self.env.uid,
                                                                            [('mes', '=', self.mes),
                                                                             ('anio', '=', self.anio),
                                                                             ('parent_detalle_id', '=',
                                                                              h.id)])

        pagos_honorarios = self.pool.get('res.partner.honorarios_detalle').browse(self.env.cr, self.env.uid, id,
                                                                                  context=None)
        for h in pagos_honorarios:
            monto = monto + h.importe_pagado
        self.importe_pagado = monto

    @api.onchange('mes', 'anio')
    def check_change_mes(self):
        self.mostrarCronograma()

    @api.depends('parent_id')
    def _compute_pagos(self):
        a = int(self.anio)
        if (a % 4 == 0 and a % 100 != 0 or a % 400 == 0):
            meses = (31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)  # tupla con cantidad de meses
        else:
            meses = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)  # tupla con cantidad de meses
        if self.anio and self.mes:
            nueva_inicio = date(int(self.anio), int(self.mes), 1)
            nueva_fin = date(int(self.anio), int(self.mes), meses[int(self.mes) - 1])
            id = self.pool.get('res.partner.pagos_cliente').search(self.env.cr, self.env.uid,
                                                                   [('fecha', '>=', str(nueva_inicio)),
                                                                    ('fecha', '<=', str(nueva_fin)),
                                                                    ('cliente', '=',
                                                                     self._context.get('default_parent_id'))])

            pagos_c = self.pool.get('res.partner.pagos_cliente').browse(self.env.cr, self.env.uid, id, context=None)
            self.pago_ids = pagos_c

    def mostrarCronograma(self):
        a = int(self.anio)
        if (a % 4 == 0 and a % 100 != 0 or a % 400 == 0):
            meses = (31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)  # tupla con cantidad de meses
        else:
            meses = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)  # tupla con cantidad de meses
        nueva_inicio = date(int(self.anio), int(self.mes), 1)
        nueva_fin = date(int(self.anio), int(self.mes), meses[int(self.mes) - 1])
        id = self.pool.get('res.partner.pagos_cliente').search(self.env.cr, self.env.uid,
                                                               [('fecha', '>=', str(nueva_inicio)),
                                                                ('fecha', '<=', str(nueva_fin)),
                                                                ('cliente', '=',
                                                                 self._context.get('default_parent_id'))])

        pagos_c = self.pool.get('res.partner.pagos_cliente').browse(self.env.cr, self.env.uid, id, context=None)
        self.pago_ids = pagos_c
        monto = 0
        id = self.pool.get('res.partner.honorarios_detalle').search(self.env.cr, self.env.uid,
                                                                    [('mes', '=', self.mes),
                                                                     ('anio', '=', self.anio),
                                                                     ('parent_detalle_id', '=', self.id)])
        pagos_honorarios = self.pool.get('res.partner.honorarios_detalle').browse(self.env.cr, self.env.uid, id,
                                                                                  context=None)
        for h in pagos_honorarios:
            monto = monto + h.importe_pagado

    # update
    @api.multi
    def write(self, vals):
        res = super(res_partner_honorarios, self).write(vals)
        id = self.pool.get('res.partner.honorarios_detalle').search(self.env.cr, self.env.uid,
                                                                    [('mes', '=', self.mes),
                                                                     ('anio', '=', self.anio),
                                                                     ('parent_detalle_id', '=', self.id)])
        pagos_c = self.pool.get('res.partner.honorarios_detalle').browse(self.env.cr, self.env.uid, id, context=None)
        monto = 0
        for c in pagos_c:
            monto = monto + c.importe_pagado
        a = int(self.anio)

        if (a % 4 == 0 and a % 100 != 0 or a % 400 == 0):
            meses = (31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)  # tupla con cantidad de meses
        else:
            meses = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)  # tupla con cantidad de meses
        nueva_inicio = date(int(self.anio), int(self.mes), 1)
        nueva_fin = date(int(self.anio), int(self.mes), meses[int(self.mes) - 1])
        id = self.pool.get('res.partner.pagos_cliente').search(self.env.cr, self.env.uid,
                                                               [('fecha', '>=', str(nueva_inicio)),
                                                                ('fecha', '<=', str(nueva_fin)),
                                                                ('cliente', '=',
                                                                 self._context.get('default_parent_id'))])
        # CRONOGRAMA DE PAGOS
        cronograma = self.pool.get('res.partner.pagos_cliente').browse(self.env.cr, self.env.uid, id, context=None)
        for cro in cronograma:
            if monto >= cro.importe:
                cro.write({'estado': 'pagado'})
                monto = monto - cro.importe
            else:
                cro.write({'estado': 'deudor'})
        return res


class res_partner_honorarios_detalle(models.Model):
    """CARGAR MES ACTUAL POR DEFECTO"""

    def _mes_get_fnc(self):
        print (self._context)
        today = datetime.datetime.now()
        if self._context.get('mes'):
            return str(self._context.get('mes'))
        else:
            return str(today.month)

    """MOSTRAR RANGO DE 20 AÑOS"""

    def get_rango_anios(self):
        today = datetime.datetime.now()
        lst = []
        for i in range(5, 0, -1):
            lst.append((str(today.year + i), str(today.year + i)))
        for i in range(0, 16):
            lst.append((str(today.year - i), str(today.year - i)))
        return lst

    """CARGAR AÑO ACTUAL POR DEFECTO"""

    def _anio_get_fnc(self):
        today = datetime.datetime.now()
        if self._context.get('anio'):
            return str(self._context.get('anio'))
        else:
            return str(today.year)

    _name = 'res.partner.honorarios_detalle'
    fecha_pago = fields.Date('Fecha de Pago')
    mes = fields.Selection(
        [('1', 'Enero'), ('2', 'Febrero'), ('3', 'Marzo'), ('4', 'Abril'), ('5', 'Mayo'), ('6', 'Junio'),
         ('7', 'Julio'), ('8', 'Agosto'), ('9', 'Setiembre'), ('10', 'Octubre'), ('11', 'Noviembre'),
         ('12', 'Diciembre')], 'Mes Honorarios', default=_mes_get_fnc)
    anio = fields.Selection(get_rango_anios, 'Año Honorarios', default=_anio_get_fnc)
    importe_pagado = fields.Float('Importe a Pagar')
    importe_deuda = fields.Float('Importe Deuda')
    parent_detalle_id = fields.Many2one('res.partner.honorarios', 'Parent', ondelete='cascade')

    @api.multi
    def unlink(self):

        print("Cliente Id", self._context.get("active_id"))
        a = int(self.anio)
        if (a % 4 == 0 and a % 100 != 0 or a % 400 == 0):
            meses = (31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)  # tupla con cantidad de meses
        else:
            meses = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)  # tupla con cantidad de meses
        fecha = date(int(self.anio), int(self.mes), meses[int(self.mes) - 1])

        id = self.pool.get('res.partner.pagos_cliente').search(self.env.cr, self.env.uid,
                                                               [('fecha', '=', str(fecha)),
                                                                ('cliente', '=', self._context.get("active_id"))])

        print ("Detalles de Pagos", id)

        cronograma = self.pool.get('res.partner.pagos_cliente').browse(self.env.cr, self.env.uid, id, context=None)
        for cro in cronograma:
            cro.write({'estado': 'deudor'})

        return super(res_partner_honorarios_detalle, self).unlink()


class res_partner_pagos_cliente(models.Model):
    # # pagos cliente
    _name = 'res.partner.pagos_cliente'
    fecha = fields.Date('Fecha')
    importe = fields.Float('Importe')
    cliente = fields.Many2one('res.partner')
    ruc = fields.Char('RUC')
    estado = fields.Selection([('deudor', 'Deudor'), ('pagado', 'Pagado'), ('cancelado', 'Contrato Cancelado')],
                              'Estado', default='deudor')
    pago_id = fields.Many2one('res.partner.honorarios', 'Parent')


class res_partner_documentos(models.Model):
    """CARGAR MES ACTUAL POR DEFECTO"""

    def _mes_get_fnc(self):
        today = datetime.datetime.now()
        return str(today.month)

    """MOSTRAR RAGO DE 20 AÑOS"""

    def get_rango_anios(self):
        today = datetime.datetime.now()
        lst = []
        for i in range(5, 0, -1):
            lst.append((str(today.year + i), str(today.year + i)))
        for i in range(0, 16):
            lst.append((str(today.year - i), str(today.year - i)))
        return lst

    """CARGAR AÑO ACTUAL POR DEFECTO"""

    def _anio_get_fnc(self):
        today = datetime.datetime.now()
        return str(today.year)

    _name = 'res.partner.documentos'
    _inherits = {'res.partner.documentos_quincena': 'documento_quincena_id',
                 'res.partner.documentos_fin_mes': 'documento_fin_mes_id'}
    _rec_name = 'parent_id'
    parent_id = fields.Many2one('res.partner', readonly=True)
    anio = fields.Selection(get_rango_anios, 'Año de Recepción', default=_anio_get_fnc)
    mes = fields.Selection(
        [('1', 'Enero'), ('2', 'Febrero'), ('3', 'Marzo'), ('4', 'Abril'), ('5', 'Mayo'), ('6', 'Junio'),
         ('7', 'Julio'), ('8', 'Agosto'), ('9', 'Setiembre'), ('10', 'Octubre'), ('11', 'Noviembre'),
         ('12', 'Diciembre')], 'Mes de Recepción', default=_mes_get_fnc)
    documentos = fields.Many2many('ir.attachment', 'class_ir_attachments_rel', 'class_id', 'attachment_id',
                                  'Documentos')


class res_partner_documentos_quincena(models.Model):
    """CARGAR MES ACTUAL POR DEFECTO"""

    def _mes_get_fnc(self):
        if self._context.get('mes'):
            return str(self._context.get('mes'))

    """MOSTRAR RAGO DE 20 AÑOS"""

    def get_rango_anios(self):
        today = datetime.datetime.now()
        lst = []
        for i in range(5, 0, -1):
            lst.append((str(today.year + i), str(today.year + i)))
        for i in range(0, 16):
            lst.append((str(today.year - i), str(today.year - i)))
        return lst

    """CARGAR AÑO ACTUAL POR DEFECTO"""

    def _anio_get_fnc(self):
        if self._context.get('anio'):
            return str(self._context.get('anio'))

    """CARGAR FECHA LIMITE POR DEFECTO"""

    def _limite_get_fnc(self):
        if self._context.get('anio') and self._context.get('mes'):
            f_limite = date(int(self._context.get('anio')), int(self._context.get('mes')), 20)
            return f_limite

    # cambio de estado
    @api.onchange('fecha')
    def _onchange_FIELD_fecha(self):
        if self.fecha:
            self.estado = 'Recibido'

    _name = 'res.partner.documentos_quincena'
    fecha = fields.Date('Fecha de Recepción')
    fecha_limite = fields.Date('Fecha Limite', default=_limite_get_fnc)
    anio = fields.Selection(get_rango_anios, 'Año de Recepción', default=_anio_get_fnc)
    mes = fields.Selection(
        [('1', 'Enero'), ('2', 'Febrero'), ('3', 'Marzo'), ('4', 'Abril'), ('5', 'Mayo'), ('6', 'Junio'),
         ('7', 'Julio'), ('8', 'Agosto'), ('9', 'Setiembre'), ('10', 'Octubre'), ('11', 'Noviembre'),
         ('12', 'Diciembre')], 'Mes de Recepción', default=_mes_get_fnc)
    estado = fields.Selection(
        [('Pendiente', 'Pendiente'), ('Recibido', 'Recibido'), ('No tiene documentos', 'No tiene documentos')],
        'Estado', default='Pendiente')
    observaciones = fields.Text('Observaciones')
    parent_detalle_id = fields.Many2one('res.partner.documentos_quincena', 'Parent')
    documento_quincena_ids = fields.One2many('res.partner.documentos_quincena', 'parent_detalle_id',
                                             'Included Services')


class res_partner_documentos_fin_mes(models.Model):
    """CARGAR MES ACTUAL POR DEFECTO"""

    def _mes_get_fnc(self):
        if self._context.get('mes'):
            return str(self._context.get('mes'))

    """MOSTRAR RAGO DE 20 AÑOS"""

    def get_rango_anios(self):
        today = datetime.datetime.now()
        lst = []
        for i in range(5, 0, -1):
            lst.append((str(today.year + i), str(today.year + i)))
        for i in range(0, 16):
            lst.append((str(today.year - i), str(today.year - i)))
        return lst

    """CARGAR AÑO ACTUAL POR DEFECTO"""

    def _anio_get_fnc(self):
        today = datetime.datetime.now()
        if self._context.get('anio'):
            return str(self._context.get('anio'))
        # else:
        #     return str(today.year)

    """CARGAR FECHA LIMITE POR DEFECTO"""

    def _limite_get_fnc(self):
        if self._context.get('anio') and self._context.get('mes'):
            a = int(self._context.get('anio'))
            if (a % 4 == 0 and a % 100 != 0 or a % 400 == 0):
                meses = (31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)  # tupla con cantidad de meses
            else:
                meses = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)  # tupla con cantidad de meses
            f_limite = date(int(self._context.get('anio')), int(self._context.get('mes')),
                            meses[(int(self._context.get('mes')) % 12) - 1])
            return f_limite

    _name = 'res.partner.documentos_fin_mes'
    fecha = fields.Date('Fecha de Recepción')
    fecha_limite = fields.Date('Fecha Limite', default=_limite_get_fnc)
    anio = fields.Selection(get_rango_anios, 'Año de Recepción', default=_anio_get_fnc)
    mes = fields.Selection(
        [('1', 'Enero'), ('2', 'Febrero'), ('3', 'Marzo'), ('4', 'Abril'), ('5', 'Mayo'), ('6', 'Junio'),
         ('7', 'Julio'), ('8', 'Agosto'), ('9', 'Setiembre'), ('10', 'Octubre'), ('11', 'Noviembre'),
         ('12', 'Diciembre')], 'Mes de Recepción', default=_mes_get_fnc)
    estado = fields.Selection(
        [('Pendiente', 'Pendiente'), ('Recibido', 'Recibido'), ('No tiene documentos', 'No tiene documentos')],
        'Estado', default='Pendiente')
    observaciones = fields.Text('Observaciones')
    parent_detalle_id = fields.Many2one('res.partner.documentos_fin_mes', 'Parent')
    documento_fin_mes_ids = fields.One2many('res.partner.documentos_fin_mes', 'parent_detalle_id', 'Included Services')


class res_partner_cronograma_obligaciones(models.Model):
    """CARGAR MES ACTUAL POR DEFECTO"""

    def _mes_get_fnc(self):
        today = datetime.datetime.now()
        return str(today.month)

    """MOSTRAR RAGO DE 20 AÑOS"""

    def get_rango_anios(self):
        today = datetime.datetime.now()
        lst = []
        for i in range(5, 0, -1):
            lst.append((str(today.year + i), str(today.year + i)))
        for i in range(0, 16):
            lst.append((str(today.year - i), str(today.year - i)))
        return lst

    """CARGAR AÑO ACTUAL POR DEFECTO"""

    def _anio_get_fnc(self):
        today = datetime.datetime.now()
        return str(today.year)

    _name = 'res.partner.cronograma_obligaciones'
    mes = fields.Selection(
        [('1', 'Enero'), ('2', 'Febrero'), ('3', 'Marzo'), ('4', 'Abril'), ('5', 'Mayo'), ('6', 'Junio'),
         ('7', 'Julio'), ('8', 'Agosto'), ('9', 'Setiembre'), ('10', 'Octubre'), ('11', 'Noviembre'),
         ('12', 'Diciembre')], 'Mes Honorarios', default=_mes_get_fnc)
    anio = fields.Selection(get_rango_anios, 'Año Honorarios', default=_anio_get_fnc)
    fecha_vencimiento = fields.Date('Fecha de Vencimiento')
    digito = fields.Char('Ultimo Digito Ruc')


class res_partner_cuenta_corriente(models.Model):
    # # cuentas corrientes
    _name = 'res.partner.cuenta_corriente'
    # cuenta = fields.Many2one('account.account.template', 'Cuenta')
    cuenta = fields.Char('Cuenta')
    banco = fields.Char('Banco')
    designado = fields.Char('Designado a')
    usuario = fields.Char('Usuario')
    contrasenia = fields.Char('Contraseña')
    cci = fields.Char('CCI')
    parent_id = fields.Many2one('res.partner.cuenta_corriente', 'Parent')
    cuentas_ids = fields.One2many('res.partner.cuenta_corriente', 'parent_id', 'Included Services')


class res_partner_reporte_honorarios(models.Model):
    # # reporte honorarios
    _name = 'res.partner.reporte_honorarios'
    parent_id = fields.Many2one('res.partner', 'Cliente')
    anio = fields.Char('Anio')
    enero = fields.Selection(
        [('Pronto a vencerse', 'Pronto a vencerse'), ('Pagó', 'Pagó'), ('Deudor', 'Deudor'), ('No aplica', 'No aplica'),
         ('cancelado', 'Cancelado')], 'Enero', compute='_compute_enero')
    febrero = fields.Selection(
        [('Pronto a vencerse', 'Pronto a vencerse'), ('Pagó', 'Pagó'), ('Deudor', 'Deudor'), ('No aplica', 'No aplica'),
         ('cancelado', 'Cancelado')], 'Febrero', compute='_compute_febrero')
    marzo = fields.Selection(
        [('Pronto a vencerse', 'Pronto a vencerse'), ('Pagó', 'Pagó'), ('Deudor', 'Deudor'), ('No aplica', 'No aplica'),
         ('cancelado', 'Cancelado')], 'Marzo', compute='_compute_marzo')
    abril = fields.Selection(
        [('Pronto a vencerse', 'Pronto a vencerse'), ('Pagó', 'Pagó'), ('Deudor', 'Deudor'), ('No aplica', 'No aplica'),
         ('cancelado', 'Cancelado')], 'Abril', compute='_compute_abril')
    mayo = fields.Selection(
        [('Pronto a vencerse', 'Pronto a vencerse'), ('Pagó', 'Pagó'), ('Deudor', 'Deudor'), ('No aplica', 'No aplica'),
         ('cancelado', 'Cancelado')], 'Mayo', compute='_compute_mayo')
    junio = fields.Selection(
        [('Pronto a vencerse', 'Pronto a vencerse'), ('Pagó', 'Pagó'), ('Deudor', 'Deudor'), ('No aplica', 'No aplica'),
         ('cancelado', 'Cancelado')], 'Junio', compute='_compute_junio')
    julio = fields.Selection(
        [('Pronto a vencerse', 'Pronto a vencerse'), ('Pagó', 'Pagó'), ('Deudor', 'Deudor'), ('No aplica', 'No aplica'),
         ('cancelado', 'Cancelado')], 'Julio', compute='_compute_julio')
    agosto = fields.Selection(
        [('Pronto a vencerse', 'Pronto a vencerse'), ('Pagó', 'Pagó'), ('Deudor', 'Deudor'), ('No aplica', 'No aplica'),
         ('cancelado', 'Cancelado')], 'Agosto', compute='_compute_agosto')
    setiembre = fields.Selection(
        [('Pronto a vencerse', 'Pronto a vencerse'), ('Pagó', 'Pagó'), ('Deudor', 'Deudor'), ('No aplica', 'No aplica'),
         ('cancelado', 'Cancelado')], 'Setiembre', compute='_compute_setiembre')
    octubre = fields.Selection(
        [('Pronto a vencerse', 'Pronto a vencerse'), ('Pagó', 'Pagó'), ('Deudor', 'Deudor'), ('No aplica', 'No aplica'),
         ('cancelado', 'Cancelado')], 'Octubre', compute='_compute_octubre')
    noviembre = fields.Selection(
        [('Pronto a vencerse', 'Pronto a vencerse'), ('Pagó', 'Pagó'), ('Deudor', 'Deudor'), ('No aplica', 'No aplica'),
         ('cancelado', 'Cancelado')], 'Noviembre', compute='_compute_noviembre')
    diciembre = fields.Selection(
        [('Pronto a vencerse', 'Pronto a vencerse'), ('Pagó', 'Pagó'), ('Deudor', 'Deudor'), ('No aplica', 'No aplica'),
         ('cancelado', 'Cancelado')], 'Diciembre', compute='_compute_diciembre')
    _rec_name = 'parent_id'

    @api.multi
    def getEstado(self, mes):
        self.parent_id.id

        today = datetime.datetime.now()
        a = today.year
        if (a % 4 == 0 and a % 100 != 0 or a % 400 == 0):
            meses = (31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)  # tupla con cantidad de meses
        else:
            meses = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)  # tupla con cantidad de meses

        nueva_inicio = date(today.year, int(mes), 1)
        nueva_fin = date(today.year, int(mes), meses[int(mes) - 1])
        id = self.pool.get('res.partner.pagos_cliente').search(self.env.cr, self.env.uid,
                                                               [('fecha', '>=', str(nueva_inicio)),
                                                                ('fecha', '<=', str(nueva_fin)),
                                                                ('estado', 'in', ['deudor', 'cancelado']),
                                                                ('cliente', '=', self.parent_id.id)])

        cronograma = self.pool.get('res.partner.pagos_cliente').browse(self.env.cr, self.env.uid, id, context=None)

        cliente = self.pool.get('res.cliente.contrato').search(self.env.cr, self.env.uid,
                                                               [('partner_id', '=', self.parent_id.id)], limit=1,
                                                               order="id")

        contrato = self.pool.get('res.cliente.contrato').browse(self.env.cr, self.env.uid, cliente, context=None)

        slist = contrato.fecha_inicio.split("-") if contrato else [0, 0]  #

        if today.month < int(mes):
            if cronograma:
                for cro in cronograma:
                    if cro.estado == 'cancelado':
                        return 'cancelado'
                return 'Pronto a vencerse'

            else:
                return 'No aplica' if int(slist[1]) > int(mes) else 'Pagó'
        else:
            if cronograma:
                for cro in cronograma:
                    if cro.fecha < str(today) and cro.estado != 'cancelado':
                        return 'Deudor'
                    else:
                        return 'cancelado' if cro.estado == 'cancelado' else 'Pronto a vencerse'
            else:
                return 'No aplica' if int(slist[1]) > int(mes) else 'Pagó'

    @api.multi
    def _compute_enero(self):
        for rec in self:
            rec.enero = rec.getEstado('1')

    @api.multi
    def _compute_febrero(self):
        for rec in self:
            rec.febrero = rec.getEstado('2')

    @api.multi
    def _compute_marzo(self):
        for rec in self:
            rec.marzo = rec.getEstado('3')

    @api.multi
    def _compute_abril(self):
        for rec in self:
            rec.abril = rec.getEstado('4')

    @api.multi
    def _compute_mayo(self):
        for rec in self:
            rec.mayo = rec.getEstado('5')

    @api.multi
    def _compute_junio(self):
        for rec in self:
            rec.junio = rec.getEstado('6')

    @api.multi
    def _compute_julio(self):
        for rec in self:
            rec.julio = rec.getEstado('7')

    @api.multi
    def _compute_agosto(self):
        for rec in self:
            rec.agosto = rec.getEstado('8')

    @api.multi
    def _compute_setiembre(self):
        for rec in self:
            rec.setiembre = rec.getEstado('9')

    @api.multi
    def _compute_octubre(self):
        for rec in self:
            rec.octubre = rec.getEstado('10')

    @api.multi
    def _compute_noviembre(self):
        for rec in self:
            rec.noviembre = rec.getEstado('11')

    @api.multi
    def _compute_diciembre(self):
        for rec in self:
            rec.diciembre = rec.getEstado('12')


class res_partner_reporte_estado(models.Model):
    # # reporte estado
    _name = 'res.partner.reporte_estado'
    parent_id = fields.Many2one('res.partner', 'Cliente')
    anio = fields.Char('Anio')
    enero_e = fields.Char('ENE Estado')
    febrero_e = fields.Char('FEB Estado')
    marzo_e = fields.Char('MAR Estado')
    abril_e = fields.Char('ABR Estado')
    mayo_e = fields.Char('MAY Estado')
    junio_e = fields.Char('JUN Estado')
    julio_e = fields.Char('JUL Estado')
    agosto_e = fields.Char('AGO Estado')
    setiembre_e = fields.Char('SEP Estado')
    octubre_e = fields.Char('OCT Estado')
    noviembre_e = fields.Char('NOV Estado')
    diciembre_e = fields.Char('DIC Estado')
    enero_c = fields.Char('ENE Condición')
    febrero_c = fields.Char('FEB Condición')
    marzo_c = fields.Char('MAR Condición')
    abril_c = fields.Char('ABR Condición')
    mayo_c = fields.Char('MAY Condición')
    junio_c = fields.Char('JUN Condición')
    julio_c = fields.Char('JUL Condición')
    agosto_c = fields.Char('AGO Condición')
    setiembre_c = fields.Char('SEP Condición')
    octubre_c = fields.Char('OCT Condición')
    noviembre_c = fields.Char('NOV Condición')
    diciembre_c = fields.Char('DIC Condición')
    _rec_name = 'parent_id'


class res_partner_reporte_declaracion(models.Model):
    # # reporte declaraciones
    _name = 'res.partner.reporte_declaracion'
    parent_id = fields.Many2one('res.partner', 'Cliente')
    anio = fields.Char('Anio', default=datetime.datetime.now().year)
    enero_pdt = fields.Selection(
        [('Declarado a tiempo', 'Declarado a tiempo'), ('Declarado desfasado', 'Declarado desfasado'),
         ('Pendiente declaración', 'Pendiente declaración')], 'Enero PDT', compute='_compute_enero_pdt')
    febrero_pdt = fields.Selection(
        [('Declarado a tiempo', 'Declarado a tiempo'), ('Declarado desfasado', 'Declarado desfasado'),
         ('Pendiente declaración', 'Pendiente declaración')], 'Febrero PDT', compute='_compute_febrero_pdt')
    marzo_pdt = fields.Selection(
        [('Declarado a tiempo', 'Declarado a tiempo'), ('Declarado desfasado', 'Declarado desfasado'),
         ('Pendiente declaración', 'Pendiente declaración')], 'Marzo PDT', compute='_compute_marzo_pdt')
    abril_pdt = fields.Selection(
        [('Declarado a tiempo', 'Declarado a tiempo'), ('Declarado desfasado', 'Declarado desfasado'),
         ('Pendiente declaración', 'Pendiente declaración')], 'Abril PDT', compute='_compute_abril_pdt')
    mayo_pdt = fields.Selection(
        [('Declarado a tiempo', 'Declarado a tiempo'), ('Declarado desfasado', 'Declarado desfasado'),
         ('Pendiente declaración', 'Pendiente declaración')], 'Mayo PDT', compute='_compute_mayo_pdt')
    junio_pdt = fields.Selection(
        [('Declarado a tiempo', 'Declarado a tiempo'), ('Declarado desfasado', 'Declarado desfasado'),
         ('Pendiente declaración', 'Pendiente declaración')], 'Junio PDT', compute='_compute_junio_pdt')
    julio_pdt = fields.Selection(
        [('Declarado a tiempo', 'Declarado a tiempo'), ('Declarado desfasado', 'Declarado desfasado'),
         ('Pendiente declaración', 'Pendiente declaración')], 'Julio PDT', compute='_compute_julio_pdt')
    agosto_pdt = fields.Selection(
        [('Declarado a tiempo', 'Declarado a tiempo'), ('Declarado desfasado', 'Declarado desfasado'),
         ('Pendiente declaración', 'Pendiente declaración')], 'Agosto PDT', compute='_compute_agosto_pdt')
    setiembre_pdt = fields.Selection(
        [('Declarado a tiempo', 'Declarado a tiempo'), ('Declarado desfasado', 'Declarado desfasado'),
         ('Pendiente declaración', 'Pendiente declaración')], 'Setiembre PDT', compute='_compute_setiembre_pdt')
    octubre_pdt = fields.Selection(
        [('Declarado a tiempo', 'Declarado a tiempo'), ('Declarado desfasado', 'Declarado desfasado'),
         ('Pendiente declaración', 'Pendiente declaración')], 'Octubre PDT', compute='_compute_octubre_pdt')
    noviembre_pdt = fields.Selection(
        [('Declarado a tiempo', 'Declarado a tiempo'), ('Declarado desfasado', 'Declarado desfasado'),
         ('Pendiente declaración', 'Pendiente declaración')], 'Noviembre PDT', compute='_compute_noviembre_pdt')
    diciembre_pdt = fields.Selection(
        [('Declarado a tiempo', 'Declarado a tiempo'), ('Declarado desfasado', 'Declarado desfasado'),
         ('Pendiente declaración', 'Pendiente declaración')], 'Diciembre PDT', compute='_compute_diciembre_pdt')
    enero_plame = fields.Selection(
        [('Declarado a tiempo', 'Declarado a tiempo'), ('Declarado desfasado', 'Declarado desfasado'),
         ('Pendiente declaración', 'Pendiente declaración')], 'Enero PLAME', compute='_compute_enero_plame')
    febrero_plame = fields.Selection(
        [('Declarado a tiempo', 'Declarado a tiempo'), ('Declarado desfasado', 'Declarado desfasado'),
         ('Pendiente declaración', 'Pendiente declaración')], 'Febrero PLAME', compute='_compute_febrero_plame')
    marzo_plame = fields.Selection(
        [('Declarado a tiempo', 'Declarado a tiempo'), ('Declarado desfasado', 'Declarado desfasado'),
         ('Pendiente declaración', 'Pendiente declaración')], 'Marzo PLAME', compute='_compute_marzo_plame')
    abril_plame = fields.Selection(
        [('Declarado a tiempo', 'Declarado a tiempo'), ('Declarado desfasado', 'Declarado desfasado'),
         ('Pendiente declaración', 'Pendiente declaración')], 'Abril PLAME', compute='_compute_abril_plame')
    mayo_plame = fields.Selection(
        [('Declarado a tiempo', 'Declarado a tiempo'), ('Declarado desfasado', 'Declarado desfasado'),
         ('Pendiente declaración', 'Pendiente declaración')], 'Mayo PLAME', compute='_compute_mayo_plame')
    junio_plame = fields.Selection(
        [('Declarado a tiempo', 'Declarado a tiempo'), ('Declarado desfasado', 'Declarado desfasado'),
         ('Pendiente declaración', 'Pendiente declaración')], 'Junio PLAME', compute='_compute_junio_plame')
    julio_plame = fields.Selection(
        [('Declarado a tiempo', 'Declarado a tiempo'), ('Declarado desfasado', 'Declarado desfasado'),
         ('Pendiente declaración', 'Pendiente declaración')], 'Julio PLAME', compute='_compute_julio_plame')
    agosto_plame = fields.Selection(
        [('Declarado a tiempo', 'Declarado a tiempo'), ('Declarado desfasado', 'Declarado desfasado'),
         ('Pendiente declaración', 'Pendiente declaración')], 'Agosto PLAME', compute='_compute_agosto_plame')
    setiembre_plame = fields.Selection(
        [('Declarado a tiempo', 'Declarado a tiempo'), ('Declarado desfasado', 'Declarado desfasado'),
         ('Pendiente declaración', 'Pendiente declaración')], 'Setiembre PLAME', compute='_compute_setiembre_plame')
    octubre_plame = fields.Selection(
        [('Declarado a tiempo', 'Declarado a tiempo'), ('Declarado desfasado', 'Declarado desfasado'),
         ('Pendiente declaración', 'Pendiente declaración')], 'Octubre PLAME', compute='_compute_octubre_plame')
    noviembre_plame = fields.Selection(
        [('Declarado a tiempo', 'Declarado a tiempo'), ('Declarado desfasado', 'Declarado desfasado'),
         ('Pendiente declaración', 'Pendiente declaración')], 'Noviembre PLAME', compute='_compute_noviembre_plame')
    diciembre_plame = fields.Selection(
        [('Declarado a tiempo', 'Declarado a tiempo'), ('Declarado desfasado', 'Declarado desfasado'),
         ('Pendiente declaración', 'Pendiente declaración')], 'Diciembre PLAME', compute='_compute_diciembre_plame')
    _rec_name = 'parent_id'

    @api.multi
    def getPdt(self, mes):
        # raise Warning(self.anio)
        today = datetime.datetime.now()
        idDeclaracion = self.pool.get('res.partner.declaraciones').search(self.env.cr, self.env.uid,
                                                                          [('parent_id', '=', self.parent_id.id)])

        declaracion = self.pool.get('res.partner.declaraciones').browse(self.env.cr, self.env.uid, idDeclaracion,
                                                                        context=None)

        id = self.pool.get('res.partner.declaraciones_detalle').search(self.env.cr, self.env.uid,
                                                                       [('anio', '=', str(today.year)),
                                                                        ('mes', '=', mes),
                                                                        ('parent_detalle_id', '=',
                                                                         declaracion.declaraciones_id.id)])
        detalle = self.pool.get('res.partner.declaraciones_detalle').browse(self.env.cr, self.env.uid, id, context=None)

        if detalle:
            for cro in detalle:
                if cro.fecha_pdt:
                    return 'Declarado a tiempo' if cro.fecha_pdt < cro.fecha_limite else 'Declarado desfasado'
                else:
                    return 'Pendiente declaración'
        else:
            return 'Pendiente declaración'

    @api.multi
    def getPlame(self, mes):
        today = datetime.datetime.now()
        idDeclaracion = self.pool.get('res.partner.declaraciones').search(self.env.cr, self.env.uid,
                                                                          [('parent_id', '=', self.parent_id.id)])

        declaracion = self.pool.get('res.partner.declaraciones').browse(self.env.cr, self.env.uid, idDeclaracion,
                                                                        context=None)

        id = self.pool.get('res.partner.declaraciones_detalle').search(self.env.cr, self.env.uid,
                                                                       [('anio', '=', str(today.year)),
                                                                        ('mes', '=', mes),
                                                                        ('parent_detalle_id', '=',
                                                                         declaracion.declaraciones_id.id)])
        detalle = self.pool.get('res.partner.declaraciones_detalle').browse(self.env.cr, self.env.uid, id, context=None)

        if detalle:
            for cro in detalle:
                if cro.fecha_declarada:
                    return 'Declarado a tiempo' if cro.fecha_declarada <= cro.fecha_limite else 'Declarado desfasado'
                else:
                    return 'Pendiente declaración'
        else:
            return 'Pendiente declaración'

    @api.multi
    def _compute_enero_pdt(self):
        for rec in self:
            rec.enero_pdt = rec.getPdt('1')

    @api.multi
    def _compute_febrero_pdt(self):
        for rec in self:
            rec.febrero_pdt = rec.getPdt('2')

    @api.multi
    def _compute_marzo_pdt(self):
        for rec in self:
            rec.marzo_pdt = rec.getPdt('3')

    @api.multi
    def _compute_abril_pdt(self):
        for rec in self:
            rec.abril_pdt = rec.getPdt('4')

    @api.multi
    def _compute_mayo_pdt(self):
        for rec in self:
            rec.mayo_pdt = rec.getPdt('5')

    @api.multi
    def _compute_junio_pdt(self):
        for rec in self:
            rec.junio_pdt = rec.getPdt('6')

    @api.multi
    def _compute_julio_pdt(self):
        for rec in self:
            rec.julio_pdt = rec.getPdt('7')

    @api.multi
    def _compute_agosto_pdt(self):
        for rec in self:
            rec.agosto_pdt = rec.getPdt('8')

    @api.multi
    def _compute_setiembre_pdt(self):
        for rec in self:
            rec.setiembre_pdt = rec.getPdt('9')

    @api.multi
    def _compute_octubre_pdt(self):
        for rec in self:
            rec.octubre_pdt = rec.getPdt('10')

    @api.multi
    def _compute_noviembre_pdt(self):
        for rec in self:
            rec.noviembre_pdt = rec.getPdt('11')

    @api.multi
    def _compute_diciembre_pdt(self):
        for rec in self:
            rec.diciembre_pdt = rec.getPdt('12')

    @api.multi
    def _compute_enero_plame(self):
        for rec in self:
            rec.enero_plame = rec.getPlame('1')

    @api.multi
    def _compute_febrero_plame(self):
        for rec in self:
            rec.febrero_plame = rec.getPlame('2')

    @api.multi
    def _compute_marzo_plame(self):
        for rec in self:
            rec.marzo_plame = rec.getPlame('3')

    @api.multi
    def _compute_abril_plame(self):
        for rec in self:
            rec.abril_plame = rec.getPlame('4')

    @api.multi
    def _compute_mayo_plame(self):
        for rec in self:
            rec.mayo_plame = rec.getPlame('5')

    @api.multi
    def _compute_junio_plame(self):
        for rec in self:
            rec.junio_plame = rec.getPlame('6')

    @api.multi
    def _compute_julio_plame(self):
        for rec in self:
            rec.julio_plame = rec.getPlame('7')

    @api.multi
    def _compute_agosto_plame(self):
        for rec in self:
            rec.agosto_plame = rec.getPlame('8')

    @api.multi
    def _compute_setiembre_plame(self):
        for rec in self:
            rec.setiembre_plame = rec.getPlame('9')

    @api.multi
    def _compute_octubre_plame(self):
        for rec in self:
            rec.octubre_plame = rec.getPlame('10')

    @api.multi
    def _compute_noviembre_plame(self):
        for rec in self:
            rec.noviembre_plame = rec.getPlame('11')

    @api.multi
    def _compute_diciembre_plame(self):
        for rec in self:
            rec.diciembre_plame = rec.getPlame('12')


class res_partner_reporte_pagos(models.Model):
    # # reporte declaraciones

    _name = 'res.partner.reporte_pagos'
    cliente = fields.Many2one('res.partner', 'Cliente')
    name = fields.Char('Anio')
    parent_id = fields.Many2one('res.partner.reporte_pagos', 'Parent Category', select=True, ondelete='cascade')
    child_id = fields.One2many('res.partner.reporte_pagos', 'parent_id', string='Child Categories')
    enero_igv = fields.Char('Enero IGV', compute='_compute_enero_igv')
    febrero_igv = fields.Char('Febrero IGV', compute='_compute_febrero_igv')
    marzo_igv = fields.Char('Marzo IGV', compute='_compute_marzo_igv')
    abril_igv = fields.Char('Abril IGV', compute='_compute_abril_igv')
    mayo_igv = fields.Char('Mayo IGV', compute='_compute_mayo_igv')
    junio_igv = fields.Char('Junio IGV', compute='_compute_junio_igv')
    julio_igv = fields.Char('Julio IGV', compute='_compute_julio_igv')
    agosto_igv = fields.Char('Agosto IGV', compute='_compute_agosto_igv')
    setiembre_igv = fields.Char('Setiembre IGV', compute='_compute_setiembre_igv')
    octubre_igv = fields.Char('Octubre IGV', compute='_compute_octubre_igv')
    noviembre_igv = fields.Char('Noviembre IGV', compute='_compute_noviembre_igv')
    diciembre_igv = fields.Char('Diciembre IGV', compute='_compute_diciembre_igv')
    enero_renta = fields.Char('Enero RENTA', compute='_compute_enero_renta')
    febrero_renta = fields.Char('Febrero RENTA', compute='_compute_febrero_renta')
    marzo_renta = fields.Char('Marzo RENTA', compute='_compute_marzo_renta')
    abril_renta = fields.Char('Abril RENTA', compute='_compute_abril_renta')
    mayo_renta = fields.Char('Mayo RENTA', compute='_compute_mayo_renta')
    junio_renta = fields.Char('Junio RENTA', compute='_compute_junio_renta')
    julio_renta = fields.Char('Julio RENTA', compute='_compute_julio_renta')
    agosto_renta = fields.Char('Agosto RENTA', compute='_compute_agosto_renta')
    setiembre_renta = fields.Char('Setiembre RENTA', compute='_compute_setiembre_renta')
    octubre_renta = fields.Char('Octubre RENTA', compute='_compute_octubre_renta')
    noviembre_renta = fields.Char('Noviembre RENTA', compute='_compute_noviembre_renta')
    diciembre_renta = fields.Char('Diciembre RENTA', compute='_compute_diciembre_renta')
    enero_essalud = fields.Char(
        'Enero ESSALUD', compute='_compute_enero_essalud')
    febrero_essalud = fields.Char(
        'Febrero ESSALUD', compute='_compute_febrero_essalud')
    marzo_essalud = fields.Char(
        'Marzo ESSALUD', compute='_compute_marzo_essalud')
    abril_essalud = fields.Char(
        'Abril ESSALUD', compute='_compute_abril_essalud')
    mayo_essalud = fields.Char(
        'Mayo ESSALUD', compute='_compute_mayo_essalud')
    junio_essalud = fields.Char(
        'Junio ESSALUD', compute='_compute_junio_essalud')
    julio_essalud = fields.Char(
        'Julio ESSALUD', compute='_compute_julio_essalud')
    agosto_essalud = fields.Char(
        'Agosto ESSALUD', compute='_compute_agosto_essalud')
    setiembre_essalud = fields.Char(
        'Setiembre ESSALUD', compute='_compute_setiembre_essalud')
    octubre_essalud = fields.Char(
        'Octubre ESSALUD', compute='_compute_octubre_essalud')
    noviembre_essalud = fields.Char(
        'Noviembre ESSALUD', compute='_compute_noviembre_essalud')
    diciembre_essalud = fields.Char(
        'Diciembre ESSALUD', compute='_compute_diciembre_essalud')
    enero_afp = fields.Char(
        'Enero AFP', compute='_compute_enero_afp')
    febrero_afp = fields.Char(
        'Febrero AFP', compute='_compute_febrero_afp')
    marzo_afp = fields.Char(
        'Marzo AFP', compute='_compute_marzo_afp')
    abril_afp = fields.Char(
        'Abril AFP', compute='_compute_abril_afp')
    mayo_afp = fields.Char(
        'Mayo AFP', compute='_compute_mayo_afp')
    junio_afp = fields.Char(
        'Junio AFP', compute='_compute_junio_afp')
    julio_afp = fields.Char(
        'Julio AFP', compute='_compute_julio_afp')
    agosto_afp = fields.Char(
        'Agosto AFP', compute='_compute_agosto_afp')
    setiembre_afp = fields.Char(
        'Setiembre AFP', compute='_compute_setiembre_afp')
    octubre_afp = fields.Char(
        'Octubre AFP', compute='_compute_octubre_afp')
    noviembre_afp = fields.Char(
        'Noviembre AFP', compute='_compute_noviembre_afp')
    diciembre_afp = fields.Char(
        'Diciembre AFP', compute='_compute_diciembre_afp')
    enero_onp = fields.Char(
        'Enero ONP', compute='_compute_enero_onp')
    febrero_onp = fields.Char(
        'Febrero ONP', compute='_compute_febrero_onp')
    marzo_onp = fields.Char(
        'Marzo ONP', compute='_compute_marzo_onp')
    abril_onp = fields.Char(
        'Abril ONP', compute='_compute_abril_onp')
    mayo_onp = fields.Char(
        'Mayo ONP', compute='_compute_mayo_onp')
    junio_onp = fields.Char(
        'Junio ONP', compute='_compute_junio_onp')
    julio_onp = fields.Char(
        'Julio ONP', compute='_compute_julio_onp')
    agosto_onp = fields.Char(
        'Agosto ONP', compute='_compute_agosto_onp')
    setiembre_onp = fields.Char(
        'Setiembre ONP', compute='_compute_setiembre_onp')
    octubre_onp = fields.Char(
        'Octubre ONP', compute='_compute_octubre_onp')
    noviembre_onp = fields.Char(
        'Noviembre ONP', compute='_compute_noviembre_onp')
    diciembre_onp = fields.Char(
        'Diciembre ONP', compute='_compute_diciembre_onp')

    enero_sys = fields.Char(
        'Enero SYS', compute='_compute_enero_sys')
    febrero_sys = fields.Char(
        'Febrero SYS', compute='_compute_febrero_sys')
    marzo_sys = fields.Char(
        'Marzo SYS', compute='_compute_marzo_sys')
    abril_sys = fields.Char(
        'Abril SYS', compute='_compute_abril_sys')
    mayo_sys = fields.Char(
        'Mayo SYS', compute='_compute_mayo_sys')
    junio_sys = fields.Char(
        'Junio SYS', compute='_compute_junio_sys')
    julio_sys = fields.Char(
        'Julio SYS', compute='_compute_julio_sys')
    agosto_sys = fields.Char(
        'Agosto SYS', compute='_compute_agosto_sys')
    setiembre_sys = fields.Char(
        'Setiembre SYS', compute='_compute_setiembre_sys')
    octubre_sys = fields.Char(
        'Octubre SYS', compute='_compute_octubre_sys')
    noviembre_sys = fields.Char(
        'Noviembre SYS', compute='_compute_noviembre_sys')
    diciembre_sys = fields.Char(
        'Diciembre SYS', compute='_compute_diciembre_sys')

    @api.multi
    def getImp(self, mes, imp):

        today = datetime.datetime.now()
        a = today.year
        if (a % 4 == 0 and a % 100 != 0 or a % 400 == 0):
            meses = (31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)  # tupla con cantidad de meses
        else:
            meses = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)  # tupla con cantidad de meses

        fecha = date(today.year, int(mes), meses[int(mes) - 1])
        id = self.pool.get('res.partner.pagos_cliente').search(self.env.cr, self.env.uid,
                                                               [('fecha', '=', str(fecha)),
                                                                ('estado', '=', 'cancelado'),
                                                                ('cliente', '=', self.parent_id.id)])

        idImp = self.pool.get('res.partner.impuestos_pendientes').search(self.env.cr, self.env.uid,
                                                                         [('parent_id', '=', self.cliente.id)])

        impuesto = self.pool.get('res.partner.impuestos_pendientes').browse(self.env.cr, self.env.uid, idImp,
                                                                            context=None)
        # cambiar al  año actual(dinamico
        # anio = datetime.now()
        id = self.pool.get('res.partner.impuestos_pendientes_detalle').search(self.env.cr, self.env.uid,
                                                                              [('anio', '=',
                                                                                "'" + str(today.year) + "'"),
                                                                               ('mes', '=', mes),
                                                                               ('impuesto', '=', imp),
                                                                               ('parent_detalle_id', '=',
                                                                                impuesto.impuesto_pendiente_detalle_id.id)])
        detalle = self.pool.get('res.partner.impuestos_pendientes_detalle').browse(self.env.cr, self.env.uid, id,
                                                                                   context=None)

        if detalle:
            for cro in detalle:
                valor = str(cro.deuda) + "00" if cro.deuda > 0 else '00'
                return 'Deuda: ' + format(float(valor), '.2f') if cro.deuda > 0 else 'No Deuda'
        else:
            return 'No Deuda'

    @api.multi
    def _compute_enero_igv(self):
        for rec in self:
            rec.enero_igv = rec.getImp('1', 'IGV')

    @api.multi
    def _compute_febrero_igv(self):
        for rec in self:
            rec.febrero_igv = rec.getImp('2', 'IGV')

    @api.multi
    def _compute_marzo_igv(self):
        for rec in self:
            rec.marzo_igv = rec.getImp('3', 'IGV')

    @api.multi
    def _compute_abril_igv(self):
        for rec in self:
            rec.abril_igv = rec.getImp('4', 'IGV')

    @api.multi
    def _compute_mayo_igv(self):
        for rec in self:
            rec.mayo_igv = rec.getImp('5', 'IGV')

    @api.multi
    def _compute_junio_igv(self):
        for rec in self:
            rec.junio_igv = rec.getImp('6', 'IGV')

    @api.multi
    def _compute_julio_igv(self):
        for rec in self:
            rec.julio_igv = rec.getImp('7', 'IGV')

    @api.multi
    def _compute_agosto_igv(self):
        for rec in self:
            rec.agosto_igv = rec.getImp('8', 'IGV')

    @api.multi
    def _compute_setiembre_igv(self):
        for rec in self:
            rec.setiembre_igv = rec.getImp('9', 'IGV')

    @api.multi
    def _compute_octubre_igv(self):
        for rec in self:
            rec.octubre_igv = rec.getImp('10', 'IGV')

    @api.multi
    def _compute_noviembre_igv(self):
        for rec in self:
            rec.noviembre_igv = rec.getImp('11', 'IGV')

    @api.multi
    def _compute_diciembre_igv(self):
        for rec in self:
            rec.diciembre_igv = rec.getImp('12', 'IGV')

    @api.multi
    def _compute_enero_renta(self):
        for rec in self:
            rec.enero_renta = rec.getImp('1', 'RENTA')

    @api.multi
    def _compute_febrero_renta(self):
        for rec in self:
            rec.febrero_renta = rec.getImp('2', 'RENTA')

    @api.multi
    def _compute_marzo_renta(self):
        for rec in self:
            rec.marzo_renta = rec.getImp('3', 'RENTA')

    @api.multi
    def _compute_abril_renta(self):
        for rec in self:
            rec.abril_renta = rec.getImp('4', 'RENTA')

    @api.multi
    def _compute_mayo_renta(self):
        for rec in self:
            rec.mayo_renta = rec.getImp('5', 'RENTA')

    @api.multi
    def _compute_junio_renta(self):
        for rec in self:
            rec.junio_renta = rec.getImp('6', 'RENTA')

    @api.multi
    def _compute_julio_renta(self):
        for rec in self:
            rec.julio_renta = rec.getImp('7', 'RENTA')

    @api.multi
    def _compute_agosto_renta(self):
        for rec in self:
            rec.agosto_renta = rec.getImp('8', 'RENTA')

    @api.multi
    def _compute_setiembre_renta(self):
        for rec in self:
            rec.setiembre_renta = rec.getImp('9', 'RENTA')

    @api.multi
    def _compute_octubre_renta(self):
        for rec in self:
            rec.octubre_renta = rec.getImp('10', 'RENTA')

    @api.multi
    def _compute_noviembre_renta(self):
        for rec in self:
            rec.noviembre_renta = rec.getImp('11', 'RENTA')

    @api.multi
    def _compute_diciembre_renta(self):
        for rec in self:
            rec.diciembre_renta = rec.getImp('12', 'RENTA')

    @api.multi
    def _compute_enero_essalud(self):
        for rec in self:
            rec.enero_essalud = rec.getImp('1', 'ESSALUD')

    @api.multi
    def _compute_febrero_essalud(self):
        for rec in self:
            rec.febrero_essalud = rec.getImp('2', 'ESSALUD')

    @api.multi
    def _compute_marzo_essalud(self):
        for rec in self:
            rec.marzo_essalud = rec.getImp('3', 'ESSALUD')

    @api.multi
    def _compute_abril_essalud(self):
        for rec in self:
            rec.abril_essalud = rec.getImp('4', 'ESSALUD')

    @api.multi
    def _compute_mayo_essalud(self):
        for rec in self:
            rec.mayo_essalud = rec.getImp('5', 'ESSALUD')

    @api.multi
    def _compute_junio_essalud(self):
        for rec in self:
            rec.junio_essalud = rec.getImp('6', 'ESSALUD')

    @api.multi
    def _compute_julio_essalud(self):
        for rec in self:
            rec.julio_essalud = rec.getImp('7', 'ESSALUD')

    @api.multi
    def _compute_agosto_essalud(self):
        for rec in self:
            rec.agosto_essalud = rec.getImp('8', 'ESSALUD')

    @api.multi
    def _compute_setiembre_essalud(self):
        for rec in self:
            rec.setiembre_essalud = rec.getImp('9', 'ESSALUD')

    @api.multi
    def _compute_octubre_essalud(self):
        for rec in self:
            rec.octubre_essalud = rec.getImp('10', 'ESSALUD')

    @api.multi
    def _compute_noviembre_essalud(self):
        for rec in self:
            rec.noviembre_essalud = rec.getImp('11', 'ESSALUD')

    @api.multi
    def _compute_diciembre_essalud(self):
        for rec in self:
            rec.diciembre_essalud = rec.getImp('12', 'ESSALUD')

    @api.multi
    def _compute_enero_afp(self):
        for rec in self:
            rec.enero_afp = rec.getImp('1', 'AFP')

    @api.multi
    def _compute_febrero_afp(self):
        for rec in self:
            rec.febrero_afp = rec.getImp('2', 'AFP')

    @api.multi
    def _compute_marzo_afp(self):
        for rec in self:
            rec.marzo_afp = rec.getImp('3', 'AFP')

    @api.multi
    def _compute_abril_afp(self):
        for rec in self:
            rec.abril_afp = rec.getImp('4', 'AFP')

    @api.multi
    def _compute_mayo_afp(self):
        for rec in self:
            rec.mayo_afp = rec.getImp('5', 'AFP')

    @api.multi
    def _compute_junio_afp(self):
        for rec in self:
            rec.junio_afp = rec.getImp('6', 'AFP')

    @api.multi
    def _compute_julio_afp(self):
        for rec in self:
            rec.julio_afp = rec.getImp('7', 'AFP')

    @api.multi
    def _compute_agosto_afp(self):
        for rec in self:
            rec.agosto_afp = rec.getImp('8', 'AFP')

    @api.multi
    def _compute_setiembre_afp(self):
        for rec in self:
            rec.setiembre_afp = rec.getImp('9', 'AFP')

    @api.multi
    def _compute_octubre_afp(self):
        for rec in self:
            rec.octubre_afp = rec.getImp('10', 'AFP')

    @api.multi
    def _compute_noviembre_afp(self):
        for rec in self:
            rec.noviembre_afp = rec.getImp('11', 'AFP')

    @api.multi
    def _compute_diciembre_afp(self):
        for rec in self:
            rec.diciembre_afp = rec.getImp('12', 'AFP')

    @api.multi
    def _compute_enero_onp(self):
        for rec in self:
            rec.enero_onp = rec.getImp('1', 'ONP')

    @api.multi
    def _compute_febrero_onp(self):
        for rec in self:
            rec.febrero_onp = rec.getImp('2', 'ONP')

    @api.multi
    def _compute_marzo_onp(self):
        for rec in self:
            rec.marzo_onp = rec.getImp('3', 'ONP')

    @api.multi
    def _compute_abril_onp(self):
        for rec in self:
            rec.abril_onp = rec.getImp('4', 'ONP')

    @api.multi
    def _compute_mayo_onp(self):
        for rec in self:
            rec.mayo_onp = rec.getImp('5', 'ONP')

    @api.multi
    def _compute_junio_onp(self):
        for rec in self:
            rec.junio_onp = rec.getImp('6', 'ONP')

    @api.multi
    def _compute_julio_onp(self):
        for rec in self:
            rec.julio_onp = rec.getImp('7', 'ONP')

    @api.multi
    def _compute_agosto_onp(self):
        for rec in self:
            rec.agosto_onp = rec.getImp('8', 'ONP')

    @api.multi
    def _compute_setiembre_onp(self):
        for rec in self:
            rec.setiembre_onp = rec.getImp('9', 'ONP')

    @api.multi
    def _compute_octubre_onp(self):
        for rec in self:
            rec.octubre_onp = rec.getImp('10', 'ONP')

    @api.multi
    def _compute_noviembre_onp(self):
        for rec in self:
            rec.noviembre_onp = rec.getImp('11', 'ONP')

    @api.multi
    def _compute_diciembre_onp(self):
        for rec in self:
            rec.diciembre_onp = rec.getImp('12', 'ONP')

    @api.multi
    def _compute_enero_sys(self):
        for rec in self:
            rec.enero_sys = rec.getImp('1', 'SIS O SYS')

    @api.multi
    def _compute_febrero_sys(self):
        for rec in self:
            rec.febrero_sys = rec.getImp('2', 'SIS O SYS')

    @api.multi
    def _compute_marzo_sys(self):
        for rec in self:
            rec.marzo_sys = rec.getImp('3', 'SIS O SYS')

    @api.multi
    def _compute_abril_sys(self):
        for rec in self:
            rec.abril_sys = rec.getImp('4', 'SIS O SYS')

    @api.multi
    def _compute_mayo_sys(self):
        for rec in self:
            rec.mayo_sys = rec.getImp('5', 'SIS O SYS')

    @api.multi
    def _compute_junio_sys(self):
        for rec in self:
            rec.junio_sys = rec.getImp('6', 'SIS O SYS')

    @api.multi
    def _compute_julio_sys(self):
        for rec in self:
            rec.julio_sys = rec.getImp('7', 'SIS O SYS')

    @api.multi
    def _compute_agosto_sys(self):
        for rec in self:
            rec.agosto_sys = rec.getImp('8', 'SIS O SYS')

    @api.multi
    def _compute_setiembre_sys(self):
        for rec in self:
            rec.setiembre_sys = rec.getImp('9', 'SIS O SYS')

    @api.multi
    def _compute_octubre_sys(self):
        for rec in self:
            rec.octubre_sys = rec.getImp('10', 'SIS O SYS')

    @api.multi
    def _compute_noviembre_sys(self):
        for rec in self:
            rec.noviembre_sys = rec.getImp('11', 'SIS O SYS')

    @api.multi
    def _compute_diciembre_sys(self):
        for rec in self:
            rec.diciembre_sys = rec.getImp('12', 'SIS O SYS')


class res_partner_reporte_documentos(models.Model):
    # # reporte declaraciones
    _name = 'res.partner.reporte_documentos'
    cliente = fields.Many2one('res.partner', 'Cliente')
    name = fields.Char('Anio')
    parent_id = fields.Many2one('res.partner.reporte_documentos', 'Parent Category', select=True, ondelete='cascade')
    child_id = fields.One2many('res.partner.reporte_documentos', 'parent_id', string='Child Categories')
    enero_quincena = fields.Selection(
        [('Pendiente', 'Pendiente'), ('Recibido', 'Recibido'), ('No tiene documentos', 'No tiene documentos')],
        'Enero Doc Quincena', compute='_compute_enero_quincena')
    febrero_quincena = fields.Selection(
        [('Pendiente', 'Pendiente'), ('Recibido', 'Recibido'), ('No tiene documentos', 'No tiene documentos')],
        'Febrero Doc Quincena', compute='_compute_febrero_quincena')
    marzo_quincena = fields.Selection(
        [('Pendiente', 'Pendiente'), ('Recibido', 'Recibido'), ('No tiene documentos', 'No tiene documentos')],
        'Marzo Doc Quincena', compute='_compute_marzo_quincena')
    abril_quincena = fields.Selection(
        [('Pendiente', 'Pendiente'), ('Recibido', 'Recibido'), ('No tiene documentos', 'No tiene documentos')],
        'Abril Doc Quincena', compute='_compute_abril_quincena')
    mayo_quincena = fields.Selection(
        [('Pendiente', 'Pendiente'), ('Recibido', 'Recibido'), ('No tiene documentos', 'No tiene documentos')],
        'Mayo Doc Quincena', compute='_compute_mayo_quincena')
    junio_quincena = fields.Selection(
        [('Pendiente', 'Pendiente'), ('Recibido', 'Recibido'), ('No tiene documentos', 'No tiene documentos')],
        'Junio Doc Quincena', compute='_compute_junio_quincena')
    julio_quincena = fields.Selection(
        [('Pendiente', 'Pendiente'), ('Recibido', 'Recibido'), ('No tiene documentos', 'No tiene documentos')],
        'Julio Doc Quincena', compute='_compute_julio_quincena')
    agosto_quincena = fields.Selection(
        [('Pendiente', 'Pendiente'), ('Recibido', 'Recibido'), ('No tiene documentos', 'No tiene documentos')],
        'Agosto Doc Quincena', compute='_compute_agosto_quincena')
    setiembre_quincena = fields.Selection(
        [('Pendiente', 'Pendiente'), ('Recibido', 'Recibido'), ('No tiene documentos', 'No tiene documentos')],
        'Setiembre Doc Quincena', compute='_compute_setiembre_quincena')
    octubre_quincena = fields.Selection(
        [('Pendiente', 'Pendiente'), ('Recibido', 'Recibido'), ('No tiene documentos', 'No tiene documentos')],
        'Octubre Doc Quincena', compute='_compute_octubre_quincena')
    noviembre_quincena = fields.Selection(
        [('Pendiente', 'Pendiente'), ('Recibido', 'Recibido'), ('No tiene documentos', 'No tiene documentos')],
        'Noviembre Doc Quincena', compute='_compute_noviembre_quincena')
    diciembre_quincena = fields.Selection(
        [('Pendiente', 'Pendiente'), ('Recibido', 'Recibido'), ('No tiene documentos', 'No tiene documentos')],
        'Diciembre Doc Quincena', compute='_compute_diciembre_quincena')
    enero_fin = fields.Selection(
        [('Pendiente', 'Pendiente'), ('Recibido', 'Recibido'), ('No tiene documentos', 'No tiene documentos')],
        'Enero Doc Fin Mes', compute='_compute_enero_fin')
    febrero_fin = fields.Selection(
        [('Pendiente', 'Pendiente'), ('Recibido', 'Recibido'), ('No tiene documentos', 'No tiene documentos')],
        'Febrero Doc Fin Mes', compute='_compute_febrero_fin')
    marzo_fin = fields.Selection(
        [('Pendiente', 'Pendiente'), ('Recibido', 'Recibido'), ('No tiene documentos', 'No tiene documentos')],
        'Marzo Doc Fin Mes', compute='_compute_marzo_fin')
    abril_fin = fields.Selection(
        [('Pendiente', 'Pendiente'), ('Recibido', 'Recibido'), ('No tiene documentos', 'No tiene documentos')],
        'Abril Doc Fin Mes', compute='_compute_abril_fin')
    mayo_fin = fields.Selection(
        [('Pendiente', 'Pendiente'), ('Recibido', 'Recibido'), ('No tiene documentos', 'No tiene documentos')],
        'Mayo Doc Fin Mes', compute='_compute_mayo_fin')
    junio_fin = fields.Selection(
        [('Pendiente', 'Pendiente'), ('Recibido', 'Recibido'), ('No tiene documentos', 'No tiene documentos')],
        'Junio Doc Fin Mes', compute='_compute_junio_fin')
    julio_fin = fields.Selection(
        [('Pendiente', 'Pendiente'), ('Recibido', 'Recibido'), ('No tiene documentos', 'No tiene documentos')],
        'Julio Doc Fin Mes', compute='_compute_julio_fin')
    agosto_fin = fields.Selection(
        [('Pendiente', 'Pendiente'), ('Recibido', 'Recibido'), ('No tiene documentos', 'No tiene documentos')],
        'Agosto Doc Fin Mes', compute='_compute_agosto_fin')
    setiembre_fin = fields.Selection(
        [('Pendiente', 'Pendiente'), ('Recibido', 'Recibido'), ('No tiene documentos', 'No tiene documentos')],
        'Setiembre Doc Fin Mes', compute='_compute_setiembre_fin')
    octubre_fin = fields.Selection(
        [('Pendiente', 'Pendiente'), ('Recibido', 'Recibido'), ('No tiene documentos', 'No tiene documentos')],
        'Octubre Doc Fin Mes', compute='_compute_octubre_fin')
    noviembre_fin = fields.Selection(
        [('Pendiente', 'Pendiente'), ('Recibido', 'Recibido'), ('No tiene documentos', 'No tiene documentos')],
        'Noviembre Doc Fin Mes', compute='_compute_noviembre_fin')
    diciembre_fin = fields.Selection(
        [('Pendiente', 'Pendiente'), ('Recibido', 'Recibido'), ('No tiene documentos', 'No tiene documentos')],
        'Diciembre Doc Fin Mes', compute='_compute_diciembre_fin')

    @api.multi
    def getQuincena(self, mes):
        idDocumento = self.pool.get('res.partner.documentos').search(self.env.cr, self.env.uid,
                                                                     [('parent_id', '=', self.cliente.id)])

        documento = self.pool.get('res.partner.documentos').browse(self.env.cr, self.env.uid, idDocumento, context=None)

        id = self.pool.get('res.partner.documentos_quincena').search(self.env.cr, self.env.uid,
                                                                     [('anio', '=', self.parent_id.name),
                                                                      ('mes', '=', mes),
                                                                      ('parent_detalle_id', '=',
                                                                       documento.documento_quincena_id.id)])
        detalle = self.pool.get('res.partner.documentos_quincena').browse(self.env.cr, self.env.uid, id, context=None)
        if detalle:
            for cro in detalle:
                return 'Pendiente' if cro.estado == 'Pendiente' else 'Recibido'
        else:
            return 'No tiene documentos'

    @api.multi
    def getFin(self, mes):
        idDocumento = self.pool.get('res.partner.documentos').search(self.env.cr, self.env.uid,
                                                                     [('parent_id', '=', self.cliente.id)])

        documento = self.pool.get('res.partner.documentos').browse(self.env.cr, self.env.uid, idDocumento,
                                                                   context=None)

        id = self.pool.get('res.partner.documentos_fin_mes').search(self.env.cr, self.env.uid,
                                                                    [('anio', '=', self.parent_id.name),
                                                                     ('mes', '=', mes),
                                                                     ('parent_detalle_id', '=',
                                                                      documento.documento_fin_mes_id.id)])
        detalle = self.pool.get('res.partner.documentos_fin_mes').browse(self.env.cr, self.env.uid, id, context=None)

        if detalle:
            for cro in detalle:
                return 'Pendiente' if cro.estado == 'Pendiente' else 'Recibido'
        else:
            return 'No tiene documentos'

    @api.multi
    def _compute_enero_quincena(self):
        for rec in self:
            rec.enero_quincena = rec.getQuincena('1')

    @api.multi
    def _compute_febrero_quincena(self):
        for rec in self:
            rec.febrero_quincena = rec.getQuincena('2')

    @api.multi
    def _compute_marzo_quincena(self):
        for rec in self:
            rec.marzo_quincena = rec.getQuincena('3')

    @api.multi
    def _compute_abril_quincena(self):
        for rec in self:
            rec.abril_quincena = rec.getQuincena('4')

    @api.multi
    def _compute_mayo_quincena(self):
        for rec in self:
            rec.mayo_quincena = rec.getQuincena('5')

    @api.multi
    def _compute_junio_quincena(self):
        for rec in self:
            rec.junio_quincena = rec.getQuincena('6')

    @api.multi
    def _compute_julio_quincena(self):
        for rec in self:
            rec.julio_quincena = rec.getQuincena('7')

    @api.multi
    def _compute_agosto_quincena(self):
        for rec in self:
            rec.agosto_quincena = rec.getQuincena('8')

    @api.multi
    def _compute_setiembre_quincena(self):
        for rec in self:
            rec.setiembre_quincena = rec.getQuincena('9')

    @api.multi
    def _compute_octubre_quincena(self):
        for rec in self:
            rec.octubre_quincena = rec.getQuincena('10')

    @api.multi
    def _compute_noviembre_quincena(self):
        for rec in self:
            rec.noviembre_quincena = rec.getQuincena('11')

    @api.multi
    def _compute_diciembre_quincena(self):
        for rec in self:
            rec.diciembre_quincena = rec.getQuincena('12')

    @api.multi
    def _compute_enero_fin(self):
        for rec in self:
            rec.enero_fin = rec.getFin('1')

    @api.multi
    def _compute_febrero_fin(self):
        for rec in self:
            rec.febrero_fin = rec.getFin('2')

    @api.multi
    def _compute_marzo_fin(self):
        for rec in self:
            rec.marzo_fin = rec.getFin('3')

    @api.multi
    def _compute_abril_fin(self):
        for rec in self:
            rec.abril_fin = rec.getFin('4')

    @api.multi
    def _compute_mayo_fin(self):
        for rec in self:
            rec.mayo_fin = rec.getFin('5')

    @api.multi
    def _compute_junio_fin(self):
        for rec in self:
            rec.junio_fin = rec.getFin('6')

    @api.multi
    def _compute_julio_fin(self):
        for rec in self:
            rec.julio_fin = rec.getFin('7')

    @api.multi
    def _compute_agosto_fin(self):
        for rec in self:
            rec.agosto_fin = rec.getFin('8')

    @api.multi
    def _compute_setiembre_fin(self):
        for rec in self:
            rec.setiembre_fin = rec.getFin('9')

    @api.multi
    def _compute_octubre_fin(self):
        for rec in self:
            rec.octubre_fin = rec.getFin('10')

    @api.multi
    def _compute_noviembre_fin(self):
        for rec in self:
            rec.noviembre_fin = rec.getFin('11')

    @api.multi
    def _compute_diciembre_fin(self):
        for rec in self:
            rec.diciembre_fin = rec.getFin('12')


#####################
class res_partner_reporte_honorarios_anio(models.Model):
    # # reporte honorarios
    _name = 'res.partner.reporte.honorarios.anio'
    _auto = False

    cliente = fields.Many2one('res.partner', 'Cliente')
    anio = fields.Integer('Año')
    enero = fields.Selection(
        [('Pronto a vencerse', 'Pronto a vencerse'), ('Pagó', 'Pagó'), ('Deudor', 'Deudor'), ('No aplica', 'No aplica'),
         ('cancelado', 'Cancelado')], 'Enero', compute='_compute_enero')
    febrero = fields.Selection(
        [('Pronto a vencerse', 'Pronto a vencerse'), ('Pagó', 'Pagó'), ('Deudor', 'Deudor'), ('No aplica', 'No aplica'),
         ('cancelado', 'Cancelado')], 'Febrero', compute='_compute_febrero')
    marzo = fields.Selection(
        [('Pronto a vencerse', 'Pronto a vencerse'), ('Pagó', 'Pagó'), ('Deudor', 'Deudor'), ('No aplica', 'No aplica'),
         ('cancelado', 'Cancelado')], 'Marzo', compute='_compute_marzo')
    abril = fields.Selection(
        [('Pronto a vencerse', 'Pronto a vencerse'), ('Pagó', 'Pagó'), ('Deudor', 'Deudor'), ('No aplica', 'No aplica'),
         ('cancelado', 'Cancelado')], 'Abril', compute='_compute_abril')
    mayo = fields.Selection(
        [('Pronto a vencerse', 'Pronto a vencerse'), ('Pagó', 'Pagó'), ('Deudor', 'Deudor'), ('No aplica', 'No aplica'),
         ('cancelado', 'Cancelado')], 'Mayo', compute='_compute_mayo')
    junio = fields.Selection(
        [('Pronto a vencerse', 'Pronto a vencerse'), ('Pagó', 'Pagó'), ('Deudor', 'Deudor'), ('No aplica', 'No aplica'),
         ('cancelado', 'Cancelado')], 'Junio', compute='_compute_junio')
    julio = fields.Selection(
        [('Pronto a vencerse', 'Pronto a vencerse'), ('Pagó', 'Pagó'), ('Deudor', 'Deudor'), ('No aplica', 'No aplica'),
         ('cancelado', 'Cancelado')], 'Julio', compute='_compute_julio')
    agosto = fields.Selection(
        [('Pronto a vencerse', 'Pronto a vencerse'), ('Pagó', 'Pagó'), ('Deudor', 'Deudor'), ('No aplica', 'No aplica'),
         ('cancelado', 'Cancelado')], 'Agosto', compute='_compute_agosto')
    setiembre = fields.Selection(
        [('Pronto a vencerse', 'Pronto a vencerse'), ('Pagó', 'Pagó'), ('Deudor', 'Deudor'), ('No aplica', 'No aplica'),
         ('cancelado', 'Cancelado')], 'Setiembre', compute='_compute_setiembre')
    octubre = fields.Selection(
        [('Pronto a vencerse', 'Pronto a vencerse'), ('Pagó', 'Pagó'), ('Deudor', 'Deudor'), ('No aplica', 'No aplica'),
         ('cancelado', 'Cancelado')], 'Octubre', compute='_compute_octubre')
    noviembre = fields.Selection(
        [('Pronto a vencerse', 'Pronto a vencerse'), ('Pagó', 'Pagó'), ('Deudor', 'Deudor'), ('No aplica', 'No aplica'),
         ('cancelado', 'Cancelado')], 'Noviembre', compute='_compute_noviembre')
    diciembre = fields.Selection(
        [('Pronto a vencerse', 'Pronto a vencerse'), ('Pagó', 'Pagó'), ('Deudor', 'Deudor'), ('No aplica', 'No aplica'),
         ('cancelado', 'Cancelado')], 'Diciembre', compute='_compute_diciembre')

    def init(self, cr):
        print ('entrandooooooooooooooo')
        tools.drop_view_if_exists(cr, 'res_partner_reporte_honorarios_anio')
        cr.execute("""
                   create or replace view res_partner_reporte_honorarios_anio as (
                   select row_number() OVER () AS id, 
                    cliente,
  extract(YEAR FROM fecha) as anio,
  '' AS enero,
  '' AS febrero,
  '' AS marzo,
  '' AS abril,
  '' AS mayo,
  '' AS junio,
  '' AS julio,
  '' AS agosto,
  '' AS septiembre,
  '' AS octubre,
  '' AS noviembre,
  '' AS diciembre
   FROM res_partner_honorarios ph JOIN
  res_partner_pagos_cliente pc on ph.parent_id = pc.cliente
  JOIN res_partner rp ON pc.cliente = rp.id
GROUP BY cliente,extract(YEAR FROM fecha) order by cliente)
                   """)

    @api.multi
    def getEstado(self, mes):
        # self.parent_id.id
        # print(self.anio)
        today = datetime.datetime.now()
        a = self.anio
        if (a % 4 == 0 and a % 100 != 0 or a % 400 == 0):
            meses = (31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)  # tupla con cantidad de meses
        else:
            meses = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)  # tupla con cantidad de meses

        nueva_inicio = date(self.anio, int(mes), 1)
        nueva_fin = date(self.anio, int(mes), meses[int(mes) - 1])
        id = self.pool.get('res.partner.pagos_cliente').search(self.env.cr, self.env.uid,
                                                               [('fecha', '>=', str(nueva_inicio)),
                                                                ('fecha', '<=', str(nueva_fin)),
                                                                ('estado', 'in', ['deudor', 'cancelado']),
                                                                ('cliente', '=', self.cliente.id)])

        cronograma = self.pool.get('res.partner.pagos_cliente').browse(self.env.cr, self.env.uid, id, context=None)

        cliente = self.pool.get('res.cliente.contrato').search(self.env.cr, self.env.uid,
                                                               [('partner_id', '=', self.cliente.id)], limit=1,
                                                               order="id")

        contrato = self.pool.get('res.cliente.contrato').browse(self.env.cr, self.env.uid, cliente, context=None)

        slist = contrato.fecha_inicio.split("-") if contrato else [0, 0]  #

        if today.month < int(mes):
            if cronograma:
                for cro in cronograma:
                    if cro.estado == 'cancelado':
                        return 'cancelado'
                return 'Pronto a vencerse'

            else:
                return 'No aplica' if int(slist[1]) > int(mes) else 'Pagó'
        else:
            if cronograma:
                for cro in cronograma:
                    if cro.fecha < str(today) and cro.estado != 'cancelado':
                        return 'Deudor'
                    else:
                        return 'cancelado' if cro.estado == 'cancelado' else 'Pronto a vencerse'
            else:
                return 'No aplica' if int(slist[1]) > int(mes) else 'Pagó'

    @api.multi
    def _compute_enero(self):
        for rec in self:
            rec.enero = rec.getEstado('1')

    @api.multi
    def _compute_febrero(self):
        for rec in self:
            rec.febrero = rec.getEstado('2')

    @api.multi
    def _compute_marzo(self):
        for rec in self:
            rec.marzo = rec.getEstado('3')

    @api.multi
    def _compute_abril(self):
        for rec in self:
            rec.abril = rec.getEstado('4')

    @api.multi
    def _compute_mayo(self):
        for rec in self:
            rec.mayo = rec.getEstado('5')

    @api.multi
    def _compute_junio(self):
        for rec in self:
            rec.junio = rec.getEstado('6')

    @api.multi
    def _compute_julio(self):
        for rec in self:
            rec.julio = rec.getEstado('7')

    @api.multi
    def _compute_agosto(self):
        for rec in self:
            rec.agosto = rec.getEstado('8')

    @api.multi
    def _compute_setiembre(self):
        for rec in self:
            rec.setiembre = rec.getEstado('9')

    @api.multi
    def _compute_octubre(self):
        for rec in self:
            rec.octubre = rec.getEstado('10')

    @api.multi
    def _compute_noviembre(self):
        for rec in self:
            rec.noviembre = rec.getEstado('11')

    @api.multi
    def _compute_diciembre(self):
        for rec in self:
            rec.diciembre = rec.getEstado('12')


class res_partner_reporte_declaracion_anio(models.Model):
    # # reporte declaraciones
    _name = 'res.partner.reporte.declaracion.anio'
    _auto = False

    parent_id = fields.Many2one('res.partner', 'Cliente')
    anio = fields.Char('Año')
    enero_pdt = fields.Selection(
        [('Declarado a tiempo', 'Declarado a tiempo'), ('Declarado desfasado', 'Declarado desfasado'),
         ('Pendiente declaración', 'Pendiente declaración')], 'Enero PDT', compute='_compute_enero_pdt')
    febrero_pdt = fields.Selection(
        [('Declarado a tiempo', 'Declarado a tiempo'), ('Declarado desfasado', 'Declarado desfasado'),
         ('Pendiente declaración', 'Pendiente declaración')], 'Febrero PDT', compute='_compute_febrero_pdt')
    marzo_pdt = fields.Selection(
        [('Declarado a tiempo', 'Declarado a tiempo'), ('Declarado desfasado', 'Declarado desfasado'),
         ('Pendiente declaración', 'Pendiente declaración')], 'Marzo PDT', compute='_compute_marzo_pdt')
    abril_pdt = fields.Selection(
        [('Declarado a tiempo', 'Declarado a tiempo'), ('Declarado desfasado', 'Declarado desfasado'),
         ('Pendiente declaración', 'Pendiente declaración')], 'Abril PDT', compute='_compute_abril_pdt')
    mayo_pdt = fields.Selection(
        [('Declarado a tiempo', 'Declarado a tiempo'), ('Declarado desfasado', 'Declarado desfasado'),
         ('Pendiente declaración', 'Pendiente declaración')], 'Mayo PDT', compute='_compute_mayo_pdt')
    junio_pdt = fields.Selection(
        [('Declarado a tiempo', 'Declarado a tiempo'), ('Declarado desfasado', 'Declarado desfasado'),
         ('Pendiente declaración', 'Pendiente declaración')], 'Junio PDT', compute='_compute_junio_pdt')
    julio_pdt = fields.Selection(
        [('Declarado a tiempo', 'Declarado a tiempo'), ('Declarado desfasado', 'Declarado desfasado'),
         ('Pendiente declaración', 'Pendiente declaración')], 'Julio PDT', compute='_compute_julio_pdt')
    agosto_pdt = fields.Selection(
        [('Declarado a tiempo', 'Declarado a tiempo'), ('Declarado desfasado', 'Declarado desfasado'),
         ('Pendiente declaración', 'Pendiente declaración')], 'Agosto PDT', compute='_compute_agosto_pdt')
    setiembre_pdt = fields.Selection(
        [('Declarado a tiempo', 'Declarado a tiempo'), ('Declarado desfasado', 'Declarado desfasado'),
         ('Pendiente declaración', 'Pendiente declaración')], 'Setiembre PDT', compute='_compute_setiembre_pdt')
    octubre_pdt = fields.Selection(
        [('Declarado a tiempo', 'Declarado a tiempo'), ('Declarado desfasado', 'Declarado desfasado'),
         ('Pendiente declaración', 'Pendiente declaración')], 'Octubre PDT', compute='_compute_octubre_pdt')
    noviembre_pdt = fields.Selection(
        [('Declarado a tiempo', 'Declarado a tiempo'), ('Declarado desfasado', 'Declarado desfasado'),
         ('Pendiente declaración', 'Pendiente declaración')], 'Noviembre PDT', compute='_compute_noviembre_pdt')
    diciembre_pdt = fields.Selection(
        [('Declarado a tiempo', 'Declarado a tiempo'), ('Declarado desfasado', 'Declarado desfasado'),
         ('Pendiente declaración', 'Pendiente declaración')], 'Diciembre PDT', compute='_compute_diciembre_pdt')
    enero_plame = fields.Selection(
        [('Declarado a tiempo', 'Declarado a tiempo'), ('Declarado desfasado', 'Declarado desfasado'),
         ('Pendiente declaración', 'Pendiente declaración')], 'Enero PLAME', compute='_compute_enero_plame')
    febrero_plame = fields.Selection(
        [('Declarado a tiempo', 'Declarado a tiempo'), ('Declarado desfasado', 'Declarado desfasado'),
         ('Pendiente declaración', 'Pendiente declaración')], 'Febrero PLAME', compute='_compute_febrero_plame')
    marzo_plame = fields.Selection(
        [('Declarado a tiempo', 'Declarado a tiempo'), ('Declarado desfasado', 'Declarado desfasado'),
         ('Pendiente declaración', 'Pendiente declaración')], 'Marzo PLAME', compute='_compute_marzo_plame')
    abril_plame = fields.Selection(
        [('Declarado a tiempo', 'Declarado a tiempo'), ('Declarado desfasado', 'Declarado desfasado'),
         ('Pendiente declaración', 'Pendiente declaración')], 'Abril PLAME', compute='_compute_abril_plame')
    mayo_plame = fields.Selection(
        [('Declarado a tiempo', 'Declarado a tiempo'), ('Declarado desfasado', 'Declarado desfasado'),
         ('Pendiente declaración', 'Pendiente declaración')], 'Mayo PLAME', compute='_compute_mayo_plame')
    junio_plame = fields.Selection(
        [('Declarado a tiempo', 'Declarado a tiempo'), ('Declarado desfasado', 'Declarado desfasado'),
         ('Pendiente declaración', 'Pendiente declaración')], 'Junio PLAME', compute='_compute_junio_plame')
    julio_plame = fields.Selection(
        [('Declarado a tiempo', 'Declarado a tiempo'), ('Declarado desfasado', 'Declarado desfasado'),
         ('Pendiente declaración', 'Pendiente declaración')], 'Julio PLAME', compute='_compute_julio_plame')
    agosto_plame = fields.Selection(
        [('Declarado a tiempo', 'Declarado a tiempo'), ('Declarado desfasado', 'Declarado desfasado'),
         ('Pendiente declaración', 'Pendiente declaración')], 'Agosto PLAME', compute='_compute_agosto_plame')
    setiembre_plame = fields.Selection(
        [('Declarado a tiempo', 'Declarado a tiempo'), ('Declarado desfasado', 'Declarado desfasado'),
         ('Pendiente declaración', 'Pendiente declaración')], 'Setiembre PLAME', compute='_compute_setiembre_plame')
    octubre_plame = fields.Selection(
        [('Declarado a tiempo', 'Declarado a tiempo'), ('Declarado desfasado', 'Declarado desfasado'),
         ('Pendiente declaración', 'Pendiente declaración')], 'Octubre PLAME', compute='_compute_octubre_plame')
    noviembre_plame = fields.Selection(
        [('Declarado a tiempo', 'Declarado a tiempo'), ('Declarado desfasado', 'Declarado desfasado'),
         ('Pendiente declaración', 'Pendiente declaración')], 'Noviembre PLAME', compute='_compute_noviembre_plame')
    diciembre_plame = fields.Selection(
        [('Declarado a tiempo', 'Declarado a tiempo'), ('Declarado desfasado', 'Declarado desfasado'),
         ('Pendiente declaración', 'Pendiente declaración')], 'Diciembre PLAME', compute='_compute_diciembre_plame')
    _rec_name = 'parent_id'

    def init(self, cr):
        print ('entrandooooooooooooooo')
        tools.drop_view_if_exists(cr, 'res_partner_reporte_declaracion_anio')
        cr.execute("""
                       create or replace view res_partner_reporte_declaracion_anio as (
                       select row_number() OVER () AS id, 
                         ph.parent_id,
  anio,
  '' AS enero_pdt,
  '' AS febrero_pdt,
  '' AS marzo_pdt,
  '' AS abril_pdt,
  '' AS mayo_pdt,
  '' AS junio_pdt,
  '' AS julio_pdt,
  '' AS agosto_pdt,
  '' AS septiembre_pdt,
  '' AS octubre_pdt,
  '' AS noviembre_pdt,
  '' AS diciembre_pdt,
  '' AS enero_plame,
  '' AS febrero_plame,
  '' AS marzo_plame,
  '' AS abril_plame,
  '' AS mayo_plame,
  '' AS junio_plame,
  '' AS julio_plame,
  '' AS agosto_plame,
  '' AS septiembre_plame,
  '' AS octubre_plame,
  '' AS noviembre_plame,
  '' AS diciembre_plame
   FROM res_partner_declaraciones ph JOIN
  res_partner_declaraciones_detalle pc on ph.declaraciones_id = pc.parent_detalle_id
GROUP BY parent_id, anio
 order by parent_id ) """)

    @api.multi
    def getPdt(self, mes):
        # raise Warning(self.anio)
        today = datetime.datetime.now()
        idDeclaracion = self.pool.get('res.partner.declaraciones').search(self.env.cr, self.env.uid,
                                                                          [('parent_id', '=', self.parent_id.id)])
        # print('idDeclaracion -> ', str(idDeclaracion))
        declaracion = self.pool.get('res.partner.declaraciones').browse(self.env.cr, self.env.uid, idDeclaracion,
                                                                        context=None)
        # print('declaracion -> ', str(declaracion))
        # print('self.anio -> ', str(self.anio))
        # print('mes -> ', str(mes))
        # print('mes -> ', str(declaracion.declaraciones_id.id))
        id = self.pool.get('res.partner.declaraciones_detalle').search(self.env.cr, self.env.uid,
                                                                       [('anio', '=', str(self.anio)),
                                                                        ('mes', '=', mes),
                                                                        ('parent_detalle_id', '=',
                                                                         declaracion.declaraciones_id.id)])

        # print('id -> ', str(id))
        detalle = self.pool.get('res.partner.declaraciones_detalle').browse(self.env.cr, self.env.uid, id, context=None)

        if detalle:
            for cro in detalle:
                if cro.fecha_pdt:
                    return 'Declarado a tiempo' if cro.fecha_pdt < cro.fecha_limite else 'Declarado desfasado'
                else:
                    return 'Pendiente declaración'
        else:
            return 'Pendiente declaración'

    @api.multi
    def getPlame(self, mes):
        today = datetime.datetime.now()
        idDeclaracion = self.pool.get('res.partner.declaraciones').search(self.env.cr, self.env.uid,
                                                                          [('parent_id', '=', self.parent_id.id)])

        declaracion = self.pool.get('res.partner.declaraciones').browse(self.env.cr, self.env.uid, idDeclaracion,
                                                                        context=None)

        id = self.pool.get('res.partner.declaraciones_detalle').search(self.env.cr, self.env.uid,
                                                                       [('anio', '=', str(self.anio)),
                                                                        ('mes', '=', mes),
                                                                        ('parent_detalle_id', '=',
                                                                         declaracion.declaraciones_id.id)])
        detalle = self.pool.get('res.partner.declaraciones_detalle').browse(self.env.cr, self.env.uid, id, context=None)

        if detalle:
            for cro in detalle:
                if cro.fecha_declarada:
                    return 'Declarado a tiempo' if cro.fecha_declarada <= cro.fecha_limite else 'Declarado desfasado'
                else:
                    return 'Pendiente declaración'
        else:
            return 'Pendiente declaración'

    @api.multi
    def _compute_enero_pdt(self):
        for rec in self:
            rec.enero_pdt = rec.getPdt('1')

    @api.multi
    def _compute_febrero_pdt(self):
        for rec in self:
            rec.febrero_pdt = rec.getPdt('2')

    @api.multi
    def _compute_marzo_pdt(self):
        for rec in self:
            rec.marzo_pdt = rec.getPdt('3')

    @api.multi
    def _compute_abril_pdt(self):
        for rec in self:
            rec.abril_pdt = rec.getPdt('4')

    @api.multi
    def _compute_mayo_pdt(self):
        for rec in self:
            rec.mayo_pdt = rec.getPdt('5')

    @api.multi
    def _compute_junio_pdt(self):
        for rec in self:
            rec.junio_pdt = rec.getPdt('6')

    @api.multi
    def _compute_julio_pdt(self):
        for rec in self:
            rec.julio_pdt = rec.getPdt('7')

    @api.multi
    def _compute_agosto_pdt(self):
        for rec in self:
            rec.agosto_pdt = rec.getPdt('8')

    @api.multi
    def _compute_setiembre_pdt(self):
        for rec in self:
            rec.setiembre_pdt = rec.getPdt('9')

    @api.multi
    def _compute_octubre_pdt(self):
        for rec in self:
            rec.octubre_pdt = rec.getPdt('10')

    @api.multi
    def _compute_noviembre_pdt(self):
        for rec in self:
            rec.noviembre_pdt = rec.getPdt('11')

    @api.multi
    def _compute_diciembre_pdt(self):
        for rec in self:
            rec.diciembre_pdt = rec.getPdt('12')

    @api.multi
    def _compute_enero_plame(self):
        for rec in self:
            rec.enero_plame = rec.getPlame('1')

    @api.multi
    def _compute_febrero_plame(self):
        for rec in self:
            rec.febrero_plame = rec.getPlame('2')

    @api.multi
    def _compute_marzo_plame(self):
        for rec in self:
            rec.marzo_plame = rec.getPlame('3')

    @api.multi
    def _compute_abril_plame(self):
        for rec in self:
            rec.abril_plame = rec.getPlame('4')

    @api.multi
    def _compute_mayo_plame(self):
        for rec in self:
            rec.mayo_plame = rec.getPlame('5')

    @api.multi
    def _compute_junio_plame(self):
        for rec in self:
            rec.junio_plame = rec.getPlame('6')

    @api.multi
    def _compute_julio_plame(self):
        for rec in self:
            rec.julio_plame = rec.getPlame('7')

    @api.multi
    def _compute_agosto_plame(self):
        for rec in self:
            rec.agosto_plame = rec.getPlame('8')

    @api.multi
    def _compute_setiembre_plame(self):
        for rec in self:
            rec.setiembre_plame = rec.getPlame('9')

    @api.multi
    def _compute_octubre_plame(self):
        for rec in self:
            rec.octubre_plame = rec.getPlame('10')

    @api.multi
    def _compute_noviembre_plame(self):
        for rec in self:
            rec.noviembre_plame = rec.getPlame('11')

    @api.multi
    def _compute_diciembre_plame(self):
        for rec in self:
            rec.diciembre_plame = rec.getPlame('12')


class res_partner_reporte_documentos_anio(models.Model):
    # # reporte declaraciones
    _name = 'res.partner.reporte.documentos.anio'
    _auto = False

    parent_id = fields.Many2one('res.partner', 'Cliente')
    anio = fields.Char('Año')
    enero_quincena = fields.Selection(
        [('Pendiente', 'Pendiente'), ('Recibido', 'Recibido'), ('No tiene documentos', 'No tiene documentos')],
        'Enero Doc Quincena', compute='_compute_enero_quincena')
    febrero_quincena = fields.Selection(
        [('Pendiente', 'Pendiente'), ('Recibido', 'Recibido'), ('No tiene documentos', 'No tiene documentos')],
        'Febrero Doc Quincena', compute='_compute_febrero_quincena')
    marzo_quincena = fields.Selection(
        [('Pendiente', 'Pendiente'), ('Recibido', 'Recibido'), ('No tiene documentos', 'No tiene documentos')],
        'Marzo Doc Quincena', compute='_compute_marzo_quincena')
    abril_quincena = fields.Selection(
        [('Pendiente', 'Pendiente'), ('Recibido', 'Recibido'), ('No tiene documentos', 'No tiene documentos')],
        'Abril Doc Quincena', compute='_compute_abril_quincena')
    mayo_quincena = fields.Selection(
        [('Pendiente', 'Pendiente'), ('Recibido', 'Recibido'), ('No tiene documentos', 'No tiene documentos')],
        'Mayo Doc Quincena', compute='_compute_mayo_quincena')
    junio_quincena = fields.Selection(
        [('Pendiente', 'Pendiente'), ('Recibido', 'Recibido'), ('No tiene documentos', 'No tiene documentos')],
        'Junio Doc Quincena', compute='_compute_junio_quincena')
    julio_quincena = fields.Selection(
        [('Pendiente', 'Pendiente'), ('Recibido', 'Recibido'), ('No tiene documentos', 'No tiene documentos')],
        'Julio Doc Quincena', compute='_compute_julio_quincena')
    agosto_quincena = fields.Selection(
        [('Pendiente', 'Pendiente'), ('Recibido', 'Recibido'), ('No tiene documentos', 'No tiene documentos')],
        'Agosto Doc Quincena', compute='_compute_agosto_quincena')
    setiembre_quincena = fields.Selection(
        [('Pendiente', 'Pendiente'), ('Recibido', 'Recibido'), ('No tiene documentos', 'No tiene documentos')],
        'Setiembre Doc Quincena', compute='_compute_setiembre_quincena')
    octubre_quincena = fields.Selection(
        [('Pendiente', 'Pendiente'), ('Recibido', 'Recibido'), ('No tiene documentos', 'No tiene documentos')],
        'Octubre Doc Quincena', compute='_compute_octubre_quincena')
    noviembre_quincena = fields.Selection(
        [('Pendiente', 'Pendiente'), ('Recibido', 'Recibido'), ('No tiene documentos', 'No tiene documentos')],
        'Noviembre Doc Quincena', compute='_compute_noviembre_quincena')
    diciembre_quincena = fields.Selection(
        [('Pendiente', 'Pendiente'), ('Recibido', 'Recibido'), ('No tiene documentos', 'No tiene documentos')],
        'Diciembre Doc Quincena', compute='_compute_diciembre_quincena')
    enero_fin = fields.Selection(
        [('Pendiente', 'Pendiente'), ('Recibido', 'Recibido'), ('No tiene documentos', 'No tiene documentos')],
        'Enero Doc Fin Mes', compute='_compute_enero_fin')
    febrero_fin = fields.Selection(
        [('Pendiente', 'Pendiente'), ('Recibido', 'Recibido'), ('No tiene documentos', 'No tiene documentos')],
        'Febrero Doc Fin Mes', compute='_compute_febrero_fin')
    marzo_fin = fields.Selection(
        [('Pendiente', 'Pendiente'), ('Recibido', 'Recibido'), ('No tiene documentos', 'No tiene documentos')],
        'Marzo Doc Fin Mes', compute='_compute_marzo_fin')
    abril_fin = fields.Selection(
        [('Pendiente', 'Pendiente'), ('Recibido', 'Recibido'), ('No tiene documentos', 'No tiene documentos')],
        'Abril Doc Fin Mes', compute='_compute_abril_fin')
    mayo_fin = fields.Selection(
        [('Pendiente', 'Pendiente'), ('Recibido', 'Recibido'), ('No tiene documentos', 'No tiene documentos')],
        'Mayo Doc Fin Mes', compute='_compute_mayo_fin')
    junio_fin = fields.Selection(
        [('Pendiente', 'Pendiente'), ('Recibido', 'Recibido'), ('No tiene documentos', 'No tiene documentos')],
        'Junio Doc Fin Mes', compute='_compute_junio_fin')
    julio_fin = fields.Selection(
        [('Pendiente', 'Pendiente'), ('Recibido', 'Recibido'), ('No tiene documentos', 'No tiene documentos')],
        'Julio Doc Fin Mes', compute='_compute_julio_fin')
    agosto_fin = fields.Selection(
        [('Pendiente', 'Pendiente'), ('Recibido', 'Recibido'), ('No tiene documentos', 'No tiene documentos')],
        'Agosto Doc Fin Mes', compute='_compute_agosto_fin')
    setiembre_fin = fields.Selection(
        [('Pendiente', 'Pendiente'), ('Recibido', 'Recibido'), ('No tiene documentos', 'No tiene documentos')],
        'Setiembre Doc Fin Mes', compute='_compute_setiembre_fin')
    octubre_fin = fields.Selection(
        [('Pendiente', 'Pendiente'), ('Recibido', 'Recibido'), ('No tiene documentos', 'No tiene documentos')],
        'Octubre Doc Fin Mes', compute='_compute_octubre_fin')
    noviembre_fin = fields.Selection(
        [('Pendiente', 'Pendiente'), ('Recibido', 'Recibido'), ('No tiene documentos', 'No tiene documentos')],
        'Noviembre Doc Fin Mes', compute='_compute_noviembre_fin')
    diciembre_fin = fields.Selection(
        [('Pendiente', 'Pendiente'), ('Recibido', 'Recibido'), ('No tiene documentos', 'No tiene documentos')],
        'Diciembre Doc Fin Mes', compute='_compute_diciembre_fin')

    def init(self, cr):
        print ('entrandooooooooooooooo')
        tools.drop_view_if_exists(cr, 'res_partner_reporte_documentos_anio')
        cr.execute("""
                           create or replace view res_partner_reporte_documentos_anio as (
                           select row_number() OVER () AS id, 
                            parent_id, anio,  '' AS enero_quincena,
  '' AS febrero_quincena,
  '' AS marzo_quincena,
  '' AS abril_quincena,
  '' AS mayo_quincena,
  '' AS junio_quincena,
  '' AS julio_quincena,
  '' AS agosto_quincenat,
  '' AS septiembre__quincena,
  '' AS octubre_quincena,
  '' AS noviembre_quincena,
  '' AS diciembre_quincena,
  '' AS enero_fin,
  '' AS febrero_fin,
  '' AS marzo_fin,
  '' AS abril_fin,
  '' AS mayo_fin,
  '' AS junio_fin,
  '' AS julio_fin,
  '' AS agosto_fin,
  '' AS septiembre_fin,
  '' AS octubre_fin,
  '' AS noviembre_fin,
  '' AS diciembre_fin from (SELECT
  ph.parent_id,
  pc.anio
FROM res_partner_documentos ph
  JOIN res_partner_documentos_quincena pc ON ph.documento_quincena_id = pc.parent_detalle_id
union all
SELECT
  ph.parent_id,
  fm.anio
FROM res_partner_documentos ph
  JOIN res_partner_documentos_fin_mes fm ON ph.documento_fin_mes_id = fm.parent_detalle_id) as tbl
GROUP BY parent_id, anio
ORDER BY parent_id ) """)

    @api.multi
    def getQuincena(self, mes):
        idDocumento = self.pool.get('res.partner.documentos').search(self.env.cr, self.env.uid,
                                                                     [('parent_id', '=', self.parent_id.id)])

        documento = self.pool.get('res.partner.documentos').browse(self.env.cr, self.env.uid, idDocumento, context=None)

        id = self.pool.get('res.partner.documentos_quincena').search(self.env.cr, self.env.uid,
                                                                     [('anio', '=', self.anio),
                                                                      ('mes', '=', mes),
                                                                      ('parent_detalle_id', '=',
                                                                       documento.documento_quincena_id.id)])
        detalle = self.pool.get('res.partner.documentos_quincena').browse(self.env.cr, self.env.uid, id, context=None)
        if detalle:
            for cro in detalle:
                return 'Pendiente' if cro.estado == 'Pendiente' else 'Recibido'
        else:
            return 'No tiene documentos'

    @api.multi
    def getFin(self, mes):
        idDocumento = self.pool.get('res.partner.documentos').search(self.env.cr, self.env.uid,
                                                                     [('parent_id', '=', self.parent_id.id)])

        documento = self.pool.get('res.partner.documentos').browse(self.env.cr, self.env.uid, idDocumento,
                                                                   context=None)

        id = self.pool.get('res.partner.documentos_fin_mes').search(self.env.cr, self.env.uid,
                                                                    [('anio', '=', self.anio),
                                                                     ('mes', '=', mes),
                                                                     ('parent_detalle_id', '=',
                                                                      documento.documento_fin_mes_id.id)])
        detalle = self.pool.get('res.partner.documentos_fin_mes').browse(self.env.cr, self.env.uid, id, context=None)

        if detalle:
            for cro in detalle:
                return 'Pendiente' if cro.estado == 'Pendiente' else 'Recibido'
        else:
            return 'No tiene documentos'

    @api.multi
    def _compute_enero_quincena(self):
        for rec in self:
            rec.enero_quincena = rec.getQuincena('1')

    @api.multi
    def _compute_febrero_quincena(self):
        for rec in self:
            rec.febrero_quincena = rec.getQuincena('2')

    @api.multi
    def _compute_marzo_quincena(self):
        for rec in self:
            rec.marzo_quincena = rec.getQuincena('3')

    @api.multi
    def _compute_abril_quincena(self):
        for rec in self:
            rec.abril_quincena = rec.getQuincena('4')

    @api.multi
    def _compute_mayo_quincena(self):
        for rec in self:
            rec.mayo_quincena = rec.getQuincena('5')

    @api.multi
    def _compute_junio_quincena(self):
        for rec in self:
            rec.junio_quincena = rec.getQuincena('6')

    @api.multi
    def _compute_julio_quincena(self):
        for rec in self:
            rec.julio_quincena = rec.getQuincena('7')

    @api.multi
    def _compute_agosto_quincena(self):
        for rec in self:
            rec.agosto_quincena = rec.getQuincena('8')

    @api.multi
    def _compute_setiembre_quincena(self):
        for rec in self:
            rec.setiembre_quincena = rec.getQuincena('9')

    @api.multi
    def _compute_octubre_quincena(self):
        for rec in self:
            rec.octubre_quincena = rec.getQuincena('10')

    @api.multi
    def _compute_noviembre_quincena(self):
        for rec in self:
            rec.noviembre_quincena = rec.getQuincena('11')

    @api.multi
    def _compute_diciembre_quincena(self):
        for rec in self:
            rec.diciembre_quincena = rec.getQuincena('12')

    @api.multi
    def _compute_enero_fin(self):
        for rec in self:
            rec.enero_fin = rec.getFin('1')

    @api.multi
    def _compute_febrero_fin(self):
        for rec in self:
            rec.febrero_fin = rec.getFin('2')

    @api.multi
    def _compute_marzo_fin(self):
        for rec in self:
            rec.marzo_fin = rec.getFin('3')

    @api.multi
    def _compute_abril_fin(self):
        for rec in self:
            rec.abril_fin = rec.getFin('4')

    @api.multi
    def _compute_mayo_fin(self):
        for rec in self:
            rec.mayo_fin = rec.getFin('5')

    @api.multi
    def _compute_junio_fin(self):
        for rec in self:
            rec.junio_fin = rec.getFin('6')

    @api.multi
    def _compute_julio_fin(self):
        for rec in self:
            rec.julio_fin = rec.getFin('7')

    @api.multi
    def _compute_agosto_fin(self):
        for rec in self:
            rec.agosto_fin = rec.getFin('8')

    @api.multi
    def _compute_setiembre_fin(self):
        for rec in self:
            rec.setiembre_fin = rec.getFin('9')

    @api.multi
    def _compute_octubre_fin(self):
        for rec in self:
            rec.octubre_fin = rec.getFin('10')

    @api.multi
    def _compute_noviembre_fin(self):
        for rec in self:
            rec.noviembre_fin = rec.getFin('11')

    @api.multi
    def _compute_diciembre_fin(self):
        for rec in self:
            rec.diciembre_fin = rec.getFin('12')


class res_partner_reporte_pagos_anio(models.Model):
    # # reporte declaraciones

    _name = 'res.partner.reporte.pagos.anio'
    _auto = False
    parent_id = fields.Many2one('res.partner', 'Cliente')
    anio = fields.Char('Año')
    enero_igv = fields.Char('Enero IGV', compute='_compute_enero_igv')
    febrero_igv = fields.Char('Febrero IGV', compute='_compute_febrero_igv')
    marzo_igv = fields.Char('Marzo IGV', compute='_compute_marzo_igv')
    abril_igv = fields.Char('Abril IGV', compute='_compute_abril_igv')
    mayo_igv = fields.Char('Mayo IGV', compute='_compute_mayo_igv')
    junio_igv = fields.Char('Junio IGV', compute='_compute_junio_igv')
    julio_igv = fields.Char('Julio IGV', compute='_compute_julio_igv')
    agosto_igv = fields.Char('Agosto IGV', compute='_compute_agosto_igv')
    setiembre_igv = fields.Char('Setiembre IGV', compute='_compute_setiembre_igv')
    octubre_igv = fields.Char('Octubre IGV', compute='_compute_octubre_igv')
    noviembre_igv = fields.Char('Noviembre IGV', compute='_compute_noviembre_igv')
    diciembre_igv = fields.Char('Diciembre IGV', compute='_compute_diciembre_igv')
    enero_renta = fields.Char('Enero RENTA', compute='_compute_enero_renta')
    febrero_renta = fields.Char('Febrero RENTA', compute='_compute_febrero_renta')
    marzo_renta = fields.Char('Marzo RENTA', compute='_compute_marzo_renta')
    abril_renta = fields.Char('Abril RENTA', compute='_compute_abril_renta')
    mayo_renta = fields.Char('Mayo RENTA', compute='_compute_mayo_renta')
    junio_renta = fields.Char('Junio RENTA', compute='_compute_junio_renta')
    julio_renta = fields.Char('Julio RENTA', compute='_compute_julio_renta')
    agosto_renta = fields.Char('Agosto RENTA', compute='_compute_agosto_renta')
    setiembre_renta = fields.Char('Setiembre RENTA', compute='_compute_setiembre_renta')
    octubre_renta = fields.Char('Octubre RENTA', compute='_compute_octubre_renta')
    noviembre_renta = fields.Char('Noviembre RENTA', compute='_compute_noviembre_renta')
    diciembre_renta = fields.Char('Diciembre RENTA', compute='_compute_diciembre_renta')
    enero_essalud = fields.Char(
        'Enero ESSALUD', compute='_compute_enero_essalud')
    febrero_essalud = fields.Char(
        'Febrero ESSALUD', compute='_compute_febrero_essalud')
    marzo_essalud = fields.Char(
        'Marzo ESSALUD', compute='_compute_marzo_essalud')
    abril_essalud = fields.Char(
        'Abril ESSALUD', compute='_compute_abril_essalud')
    mayo_essalud = fields.Char(
        'Mayo ESSALUD', compute='_compute_mayo_essalud')
    junio_essalud = fields.Char(
        'Junio ESSALUD', compute='_compute_junio_essalud')
    julio_essalud = fields.Char(
        'Julio ESSALUD', compute='_compute_julio_essalud')
    agosto_essalud = fields.Char(
        'Agosto ESSALUD', compute='_compute_agosto_essalud')
    setiembre_essalud = fields.Char(
        'Setiembre ESSALUD', compute='_compute_setiembre_essalud')
    octubre_essalud = fields.Char(
        'Octubre ESSALUD', compute='_compute_octubre_essalud')
    noviembre_essalud = fields.Char(
        'Noviembre ESSALUD', compute='_compute_noviembre_essalud')
    diciembre_essalud = fields.Char(
        'Diciembre ESSALUD', compute='_compute_diciembre_essalud')
    enero_afp = fields.Char(
        'Enero AFP', compute='_compute_enero_afp')
    febrero_afp = fields.Char(
        'Febrero AFP', compute='_compute_febrero_afp')
    marzo_afp = fields.Char(
        'Marzo AFP', compute='_compute_marzo_afp')
    abril_afp = fields.Char(
        'Abril AFP', compute='_compute_abril_afp')
    mayo_afp = fields.Char(
        'Mayo AFP', compute='_compute_mayo_afp')
    junio_afp = fields.Char(
        'Junio AFP', compute='_compute_junio_afp')
    julio_afp = fields.Char(
        'Julio AFP', compute='_compute_julio_afp')
    agosto_afp = fields.Char(
        'Agosto AFP', compute='_compute_agosto_afp')
    setiembre_afp = fields.Char(
        'Setiembre AFP', compute='_compute_setiembre_afp')
    octubre_afp = fields.Char(
        'Octubre AFP', compute='_compute_octubre_afp')
    noviembre_afp = fields.Char(
        'Noviembre AFP', compute='_compute_noviembre_afp')
    diciembre_afp = fields.Char(
        'Diciembre AFP', compute='_compute_diciembre_afp')
    enero_onp = fields.Char(
        'Enero ONP', compute='_compute_enero_onp')
    febrero_onp = fields.Char(
        'Febrero ONP', compute='_compute_febrero_onp')
    marzo_onp = fields.Char(
        'Marzo ONP', compute='_compute_marzo_onp')
    abril_onp = fields.Char(
        'Abril ONP', compute='_compute_abril_onp')
    mayo_onp = fields.Char(
        'Mayo ONP', compute='_compute_mayo_onp')
    junio_onp = fields.Char(
        'Junio ONP', compute='_compute_junio_onp')
    julio_onp = fields.Char(
        'Julio ONP', compute='_compute_julio_onp')
    agosto_onp = fields.Char(
        'Agosto ONP', compute='_compute_agosto_onp')
    setiembre_onp = fields.Char(
        'Setiembre ONP', compute='_compute_setiembre_onp')
    octubre_onp = fields.Char(
        'Octubre ONP', compute='_compute_octubre_onp')
    noviembre_onp = fields.Char(
        'Noviembre ONP', compute='_compute_noviembre_onp')
    diciembre_onp = fields.Char(
        'Diciembre ONP', compute='_compute_diciembre_onp')

    enero_sys = fields.Char(
        'Enero SYS', compute='_compute_enero_sys')
    febrero_sys = fields.Char(
        'Febrero SYS', compute='_compute_febrero_sys')
    marzo_sys = fields.Char(
        'Marzo SYS', compute='_compute_marzo_sys')
    abril_sys = fields.Char(
        'Abril SYS', compute='_compute_abril_sys')
    mayo_sys = fields.Char(
        'Mayo SYS', compute='_compute_mayo_sys')
    junio_sys = fields.Char(
        'Junio SYS', compute='_compute_junio_sys')
    julio_sys = fields.Char(
        'Julio SYS', compute='_compute_julio_sys')
    agosto_sys = fields.Char(
        'Agosto SYS', compute='_compute_agosto_sys')
    setiembre_sys = fields.Char(
        'Setiembre SYS', compute='_compute_setiembre_sys')
    octubre_sys = fields.Char(
        'Octubre SYS', compute='_compute_octubre_sys')
    noviembre_sys = fields.Char(
        'Noviembre SYS', compute='_compute_noviembre_sys')
    diciembre_sys = fields.Char(
        'Diciembre SYS', compute='_compute_diciembre_sys')

    def init(self, cr):
        print ('entrandooooooooooooooo')
        tools.drop_view_if_exists(cr, 'res_partner_reporte_pagos_anio')
        cr.execute("""
                               create or replace view res_partner_reporte_pagos_anio as (
                               select row_number() OVER () AS id, parent_id,
  anio,
  '' as enero_igv,
  '' as febrero_igv,
  '' as marzo_igv,
  '' as abril_igv,
  '' as mayo_igv,
  '' as junio_igv,
  '' as julio_igv,
  '' as agosto_igv,
  '' as setiembre_igv,
  '' as octubre_igv,
  '' as noviembre_igv,
  '' as diciembre_igv,
  '' as enero_renta,
  '' as febrero_renta,
  '' as marzo_renta,
  '' as abril_renta,
  '' as mayo_renta,
  '' as junio_renta,
  '' as julio_renta,
  '' as agosto_renta,
  '' as setiembre_renta,
  '' as octubre_renta,
  '' as noviembre_renta,
  '' as diciembre_renta,
  '' as enero_essalud,
  '' as febrero_essalud,
  '' as marzo_essalud,
  '' as abril_essalud,
  '' as mayo_essalud,
  '' as junio_essalud,
  '' as julio_essalud,
  '' as agosto_essalud,
  '' as setiembre_essalud,
  '' as octubre_essalud,
  '' as noviembre_essalud,
  '' as diciembre_essalud,
  '' as enero_afp,
  '' as febrero_afp,
  '' as marzo_afp,
  '' as abril_afp,
  '' as mayo_afp,
  '' as junio_afp,
  '' as julio_afp,
  '' as agosto_afp,
  '' as setiembre_afp,
  '' as octubre_afp,
  '' as noviembre_afp,
  '' as diciembre_afp,
  '' as enero_onp,
  '' as febrero_onp,
  '' as marzo_onp,
  '' as abril_onp,
  '' as mayo_onp,
  '' as junio_onp,
  '' as julio_onp,
  '' as agosto_onp,
  '' as setiembre_onp,
  '' as octubre_onp,
  '' as noviembre_onp,
  '' as diciembre_onp,
  '' as enero_sys,
  '' as febrero_sys,
  '' as marzo_sys,
  '' as abril_sys,
  '' as mayo_sys,
  '' as junio_sys,
  '' as julio_sys,
  '' as agosto_sys,
  '' as setiembre_sys,
  '' as octubre_sys,
  '' as noviembre_sys,
  '' as diciembre_sys

FROM res_partner_impuestos_pendientes
WHERE parent_id NOTNULL
 ) """)

    @api.multi
    def getImp(self, mes, imp):

        today = datetime.datetime.now()
        a = today.year
        if (a % 4 == 0 and a % 100 != 0 or a % 400 == 0):
            meses = (31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)  # tupla con cantidad de meses
        else:
            meses = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)  # tupla con cantidad de meses

        fecha = date(today.year, int(mes), meses[int(mes) - 1])


        idImp = self.pool.get('res.partner.impuestos_pendientes').search(self.env.cr, self.env.uid,
                                                                         [('parent_id', '=', self.parent_id.id)])

        impuesto = self.pool.get('res.partner.impuestos_pendientes').browse(self.env.cr, self.env.uid, idImp,
                                                                            context=None)
        # cambiar al  año actual(dinamico
        # anio = datetime.now()
        id = self.pool.get('res.partner.impuestos_pendientes_detalle').search(self.env.cr, self.env.uid,
                                                                              [('anio', '=', self.anio),
                                                                               ('mes', '=', mes),
                                                                               ('impuesto', '=', imp),
                                                                               ('parent_detalle_id', '=',
                                                                                impuesto.impuesto_pendiente_detalle_id.id)])
        detalle = self.pool.get('res.partner.impuestos_pendientes_detalle').browse(self.env.cr, self.env.uid, id,
                                                                                   context=None)

        if detalle:
            for cro in detalle:
                valor = str(cro.deuda) + "00" if cro.deuda > 0 else '00'
                return 'Deuda: ' + format(float(valor), '.2f') if cro.deuda > 0 else 'No Deuda'
        else:
            return 'No Deuda'

    @api.multi
    def _compute_enero_igv(self):
        for rec in self:
            rec.enero_igv = rec.getImp('1', 'IGV')

    @api.multi
    def _compute_febrero_igv(self):
        for rec in self:
            rec.febrero_igv = rec.getImp('2', 'IGV')

    @api.multi
    def _compute_marzo_igv(self):
        for rec in self:
            rec.marzo_igv = rec.getImp('3', 'IGV')

    @api.multi
    def _compute_abril_igv(self):
        for rec in self:
            rec.abril_igv = rec.getImp('4', 'IGV')

    @api.multi
    def _compute_mayo_igv(self):
        for rec in self:
            rec.mayo_igv = rec.getImp('5', 'IGV')

    @api.multi
    def _compute_junio_igv(self):
        for rec in self:
            rec.junio_igv = rec.getImp('6', 'IGV')

    @api.multi
    def _compute_julio_igv(self):
        for rec in self:
            rec.julio_igv = rec.getImp('7', 'IGV')

    @api.multi
    def _compute_agosto_igv(self):
        for rec in self:
            rec.agosto_igv = rec.getImp('8', 'IGV')

    @api.multi
    def _compute_setiembre_igv(self):
        for rec in self:
            rec.setiembre_igv = rec.getImp('9', 'IGV')

    @api.multi
    def _compute_octubre_igv(self):
        for rec in self:
            rec.octubre_igv = rec.getImp('10', 'IGV')

    @api.multi
    def _compute_noviembre_igv(self):
        for rec in self:
            rec.noviembre_igv = rec.getImp('11', 'IGV')

    @api.multi
    def _compute_diciembre_igv(self):
        for rec in self:
            rec.diciembre_igv = rec.getImp('12', 'IGV')

    @api.multi
    def _compute_enero_renta(self):
        for rec in self:
            rec.enero_renta = rec.getImp('1', 'RENTA')

    @api.multi
    def _compute_febrero_renta(self):
        for rec in self:
            rec.febrero_renta = rec.getImp('2', 'RENTA')

    @api.multi
    def _compute_marzo_renta(self):
        for rec in self:
            rec.marzo_renta = rec.getImp('3', 'RENTA')

    @api.multi
    def _compute_abril_renta(self):
        for rec in self:
            rec.abril_renta = rec.getImp('4', 'RENTA')

    @api.multi
    def _compute_mayo_renta(self):
        for rec in self:
            rec.mayo_renta = rec.getImp('5', 'RENTA')

    @api.multi
    def _compute_junio_renta(self):
        for rec in self:
            rec.junio_renta = rec.getImp('6', 'RENTA')

    @api.multi
    def _compute_julio_renta(self):
        for rec in self:
            rec.julio_renta = rec.getImp('7', 'RENTA')

    @api.multi
    def _compute_agosto_renta(self):
        for rec in self:
            rec.agosto_renta = rec.getImp('8', 'RENTA')

    @api.multi
    def _compute_setiembre_renta(self):
        for rec in self:
            rec.setiembre_renta = rec.getImp('9', 'RENTA')

    @api.multi
    def _compute_octubre_renta(self):
        for rec in self:
            rec.octubre_renta = rec.getImp('10', 'RENTA')

    @api.multi
    def _compute_noviembre_renta(self):
        for rec in self:
            rec.noviembre_renta = rec.getImp('11', 'RENTA')

    @api.multi
    def _compute_diciembre_renta(self):
        for rec in self:
            rec.diciembre_renta = rec.getImp('12', 'RENTA')

    @api.multi
    def _compute_enero_essalud(self):
        for rec in self:
            rec.enero_essalud = rec.getImp('1', 'ESSALUD')

    @api.multi
    def _compute_febrero_essalud(self):
        for rec in self:
            rec.febrero_essalud = rec.getImp('2', 'ESSALUD')

    @api.multi
    def _compute_marzo_essalud(self):
        for rec in self:
            rec.marzo_essalud = rec.getImp('3', 'ESSALUD')

    @api.multi
    def _compute_abril_essalud(self):
        for rec in self:
            rec.abril_essalud = rec.getImp('4', 'ESSALUD')

    @api.multi
    def _compute_mayo_essalud(self):
        for rec in self:
            rec.mayo_essalud = rec.getImp('5', 'ESSALUD')

    @api.multi
    def _compute_junio_essalud(self):
        for rec in self:
            rec.junio_essalud = rec.getImp('6', 'ESSALUD')

    @api.multi
    def _compute_julio_essalud(self):
        for rec in self:
            rec.julio_essalud = rec.getImp('7', 'ESSALUD')

    @api.multi
    def _compute_agosto_essalud(self):
        for rec in self:
            rec.agosto_essalud = rec.getImp('8', 'ESSALUD')

    @api.multi
    def _compute_setiembre_essalud(self):
        for rec in self:
            rec.setiembre_essalud = rec.getImp('9', 'ESSALUD')

    @api.multi
    def _compute_octubre_essalud(self):
        for rec in self:
            rec.octubre_essalud = rec.getImp('10', 'ESSALUD')

    @api.multi
    def _compute_noviembre_essalud(self):
        for rec in self:
            rec.noviembre_essalud = rec.getImp('11', 'ESSALUD')

    @api.multi
    def _compute_diciembre_essalud(self):
        for rec in self:
            rec.diciembre_essalud = rec.getImp('12', 'ESSALUD')

    @api.multi
    def _compute_enero_afp(self):
        for rec in self:
            rec.enero_afp = rec.getImp('1', 'AFP')

    @api.multi
    def _compute_febrero_afp(self):
        for rec in self:
            rec.febrero_afp = rec.getImp('2', 'AFP')

    @api.multi
    def _compute_marzo_afp(self):
        for rec in self:
            rec.marzo_afp = rec.getImp('3', 'AFP')

    @api.multi
    def _compute_abril_afp(self):
        for rec in self:
            rec.abril_afp = rec.getImp('4', 'AFP')

    @api.multi
    def _compute_mayo_afp(self):
        for rec in self:
            rec.mayo_afp = rec.getImp('5', 'AFP')

    @api.multi
    def _compute_junio_afp(self):
        for rec in self:
            rec.junio_afp = rec.getImp('6', 'AFP')

    @api.multi
    def _compute_julio_afp(self):
        for rec in self:
            rec.julio_afp = rec.getImp('7', 'AFP')

    @api.multi
    def _compute_agosto_afp(self):
        for rec in self:
            rec.agosto_afp = rec.getImp('8', 'AFP')

    @api.multi
    def _compute_setiembre_afp(self):
        for rec in self:
            rec.setiembre_afp = rec.getImp('9', 'AFP')

    @api.multi
    def _compute_octubre_afp(self):
        for rec in self:
            rec.octubre_afp = rec.getImp('10', 'AFP')

    @api.multi
    def _compute_noviembre_afp(self):
        for rec in self:
            rec.noviembre_afp = rec.getImp('11', 'AFP')

    @api.multi
    def _compute_diciembre_afp(self):
        for rec in self:
            rec.diciembre_afp = rec.getImp('12', 'AFP')

    @api.multi
    def _compute_enero_onp(self):
        for rec in self:
            rec.enero_onp = rec.getImp('1', 'ONP')

    @api.multi
    def _compute_febrero_onp(self):
        for rec in self:
            rec.febrero_onp = rec.getImp('2', 'ONP')

    @api.multi
    def _compute_marzo_onp(self):
        for rec in self:
            rec.marzo_onp = rec.getImp('3', 'ONP')

    @api.multi
    def _compute_abril_onp(self):
        for rec in self:
            rec.abril_onp = rec.getImp('4', 'ONP')

    @api.multi
    def _compute_mayo_onp(self):
        for rec in self:
            rec.mayo_onp = rec.getImp('5', 'ONP')

    @api.multi
    def _compute_junio_onp(self):
        for rec in self:
            rec.junio_onp = rec.getImp('6', 'ONP')

    @api.multi
    def _compute_julio_onp(self):
        for rec in self:
            rec.julio_onp = rec.getImp('7', 'ONP')

    @api.multi
    def _compute_agosto_onp(self):
        for rec in self:
            rec.agosto_onp = rec.getImp('8', 'ONP')

    @api.multi
    def _compute_setiembre_onp(self):
        for rec in self:
            rec.setiembre_onp = rec.getImp('9', 'ONP')

    @api.multi
    def _compute_octubre_onp(self):
        for rec in self:
            rec.octubre_onp = rec.getImp('10', 'ONP')

    @api.multi
    def _compute_noviembre_onp(self):
        for rec in self:
            rec.noviembre_onp = rec.getImp('11', 'ONP')

    @api.multi
    def _compute_diciembre_onp(self):
        for rec in self:
            rec.diciembre_onp = rec.getImp('12', 'ONP')

    @api.multi
    def _compute_enero_sys(self):
        for rec in self:
            rec.enero_sys = rec.getImp('1', 'SIS O SYS')

    @api.multi
    def _compute_febrero_sys(self):
        for rec in self:
            rec.febrero_sys = rec.getImp('2', 'SIS O SYS')

    @api.multi
    def _compute_marzo_sys(self):
        for rec in self:
            rec.marzo_sys = rec.getImp('3', 'SIS O SYS')

    @api.multi
    def _compute_abril_sys(self):
        for rec in self:
            rec.abril_sys = rec.getImp('4', 'SIS O SYS')

    @api.multi
    def _compute_mayo_sys(self):
        for rec in self:
            rec.mayo_sys = rec.getImp('5', 'SIS O SYS')

    @api.multi
    def _compute_junio_sys(self):
        for rec in self:
            rec.junio_sys = rec.getImp('6', 'SIS O SYS')

    @api.multi
    def _compute_julio_sys(self):
        for rec in self:
            rec.julio_sys = rec.getImp('7', 'SIS O SYS')

    @api.multi
    def _compute_agosto_sys(self):
        for rec in self:
            rec.agosto_sys = rec.getImp('8', 'SIS O SYS')

    @api.multi
    def _compute_setiembre_sys(self):
        for rec in self:
            rec.setiembre_sys = rec.getImp('9', 'SIS O SYS')

    @api.multi
    def _compute_octubre_sys(self):
        for rec in self:
            rec.octubre_sys = rec.getImp('10', 'SIS O SYS')

    @api.multi
    def _compute_noviembre_sys(self):
        for rec in self:
            rec.noviembre_sys = rec.getImp('11', 'SIS O SYS')

    @api.multi
    def _compute_diciembre_sys(self):
        for rec in self:
            rec.diciembre_sys = rec.getImp('12', 'SIS O SYS')