# -*- coding: utf-8 -*-
import json

from openerp import models, fields, api
from openerp.exceptions import Warning

import requests

from consultaSunat import SUNATRuc

def get_data_doc_number(tipo_doc, numero_doc, format='json'):
    user, password = 'demorest', 'demo1234'
    url = 'http://py-devs.com//api'
    url = '%s/%s/%s' % (url, tipo_doc, str(numero_doc))
    res = {'error': True, 'message': None, 'data': {}}
    try:
        response = requests.get(url, auth=(user, password))
    except requests.exceptions.ConnectionError, e:
        res['message'] = 'Error en la conexion'
        return res
    # print (response.status_code)
    if response.status_code == 200:
        res['error'] = False
        res['data'] = response.json()
    else:
        try:
            res['message'] = response.json()['detail']
        except Exception, e:
            res['error'] = True
    return res


class res_partner(models.Model):
    @api.model
    def create(self, vals):
        record_ids = self.env['res.partner'].search([])
        new_id = super(res_partner, self).create(vals)
        new_object = self.env['res.partner'].browse(new_id.id)
        for r in record_ids:
            if 'doc_number' in vals:
                print (vals['doc_number'])
                print (r.doc_number)
                if vals['doc_number'] == r.doc_number:
                    raise Warning('El RUC ya esta registrado')
        return new_id

    _inherit = "res.partner"


    # company_type = fields.Selection((('person', 'Persona'), ('company',
    # 'Empresa'))) # habilitar odoo9
    workplace = fields.Char('Centro de Trabajo')
    doc_type = fields.Selection(
        string='Tipo de Documento',
        selection=(
            ('dni', 'D.N.I.'),
            ('ruc', 'R.U.C.'),
            ('passport', 'Pasaporte'),
            ('carnet', 'Carnet Extranjeria'),
            ('other', 'Otro'),
        ),
        default='dni',
    )
    doc_number = fields.Char('Número de Documento', required=True)
    country_id = fields.Many2one('res.country', default=lambda self: self.env[
                                 'res.country'].search([('name', '=', 'Perú')]))

    # # sunat
    tipo_contribuyente = fields.Char('Tipo de contribuyente')
    nombre_comercial = fields.Char('Nombre comercial')
    fecha_inscripcion = fields.Date('Fecha de inscripción')
    estado_contribuyente = fields.Char(
        'Estado del contribuyente')
    condicion_contribuyente = fields.Char(
        'Condición del contribuyente')

    agente_retension = fields.Boolean('Agente de Retención')
    agente_retension_apartir_del = fields.Date('A partir del')
    agente_retension_resolucion = fields.Char('Resolución')

    sistema_emision_comprobante = fields.Char('Sistema emisión')
    sistema_contabilidad = fields.Char('Sistema contabilidad')

    ultima_actualizacion_sunat = fields.Date(
        'Última actualización')
    representante_legal_ids = fields.One2many(
        'res.partner.representante_legal', inverse_name='parent_id')


    @api.multi
    def onchange_type(self, is_company):
        res = super(res_partner, self).onchange_type(is_company)

        if 'value' in res.keys():
            doc_type = is_company and 'ruc' or 'dni'
            res['value'].update({'doc_type': doc_type})

        return res

    # odoo 9
    # @api.multi
    # def on_change_company_type(self, company_type):
    #     res = super(res_partner, self).on_change_company_type(company_type)

    #     if 'value' in res.keys():
    #         doc_type = company_type == 'company' and 'ruc' or 'dni'
    #         res['value'].update({'doc_type': doc_type})

    #     return res

    @api.onchange('doc_number')
    def onchange_doc_number(self):
        self.button_update_document()

    @api.one
    def button_update_document(self):
        if self.country_id.name == u'Perú':
            if self.doc_type and self.doc_type == 'dni' and not self.is_company:
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
                    else:
                        sunat_ache = SUNATRuc()
                        d = sunat_ache.search(self.doc_number, True)
                        d = json.loads(d)
                        if d['success']:
                            d = d['result']
                            self.name = d['nombre']
                        else:
                            raise Warning(d['msg'])

            elif self.doc_type and self.doc_type == 'ruc' and self.is_company:
                    # self.company_type == 'company':
                if self.doc_number and len(self.doc_number) != 11:
                    raise Warning('El Ruc debe tener 11 caracteres')
                else:
                    record_ids = self.env['res.partner'].search([])
                    # for r in record_ids:
                    #     if self.doc_number and self.doc_number == r.doc_number:
                    #         raise Warning('El numero de documento ya esta registrado')
                    d = get_data_doc_number(
                        'ruc', self.doc_number, format='json')
                    if not d['error']:
                        print(d['error'])
                        d = d['data']
                        # raise Warning('El servicio de consulta Ruc no se encuentra disponible por el momento, por favor inténtelo más tarde.')
                    else:
                        sunat_ache = SUNATRuc()
                        d = sunat_ache.search(self.doc_number, True)
                        d = json.loads(d)
                        if d['success']:
                            d = d['result']
                        else:
                            raise Warning(d['msg'])

                    # print (d)
                    self.name = d['nombre'] or ''
                    self.street = d['domicilio_fiscal'] or ''
                    # self.street2 = '/'.join((d['departamento'],
                    #                          d['provincia'],
                    #                          d['distrito'])) or ''
                    self.street2 = d['address2'] if d['address2'] else '/'.join((d['departamento'], d['provincia'], d['distrito']))
                    self.tipo_contribuyente = d['tipo_contribuyente'] or ''
                    self.nombre_comercial = d['nombre_comercial'] or ''
                    self.fecha_inscripcion = d['fecha_inscripcion'] or ''
                    self.estado_contribuyente = d['estado_contribuyente'] or ''
                    self.condicion_contribuyente = d['condicion_contribuyente'] or ''

                    if 'agente_retencion' in d:
                        self.agente_retension = d['agente_retencion'] or ''
                        self.agente_retension_apartir_del = d['agente_retencion_apartir_del'] or ''
                        self.agente_retension_resolucion = d['agente_retencion_resolucion'] or ''
                    else:
                        self.agente_retension = False
                        self.agente_retension_apartir_del = ''
                        self.agente_retension_resolucion = ''
                    # self.ultima_actualizacion_sunat = d['ultima_actualizacion']
                    self.sistema_emision_comprobante = d['sistema_emision_comprobante'] or ''
                    self.sistema_contabilidad = d['sistema_contabilidad'] or ''

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

    @api.multi
    @api.depends('name', 'nombre_comercial', 'doc_number')
    def name_get(self):
        result = []
        for table in self:
            l_name = str(table.name) + ' - ' if table.name else ''
            l_name += str(table.nombre_comercial) + ' - ' if table.nombre_comercial else ''
            l_name += str(table.doc_number) if table.doc_number else ''
            # print (l_name)
            result.append((table.id, l_name))
        return result

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.browse()
        if name:
            recs = self.search((args + ['|', ('nombre_comercial', 'ilike', name), ('doc_number', 'ilike', name)]),
                               limit=limit)
        if not recs:
            recs = self.search([('name', operator, name)] + args, limit=limit)
        return recs.name_get()

class res_partner_representante_legal(models.Model):
    _name = 'res.partner.representante_legal'
    _rec_name = 'nombre'

    parent_id = fields.Many2one('res.partner')
    documento = fields.Char('Documento')
    nro_documento = fields.Char('Número')
    nombre = fields.Char('Nombre')
    cargo = fields.Char('Cargo')
    fecha_desde = fields.Date('Cargo desde')
