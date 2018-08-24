    # -*- coding:utf-8 -*-
#
#
#    Copyright (C) 2011,2013 Michael Telahun Makonnen <mmakonnen@gmail.com>.
#    All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
import base64

from openerp import models, fields, tools, api, _

GENDER_SELECTION = [('1', 'Male'),
                    ('2', 'Female'),
                    ('3', 'Otro')]


class HrChildren(models.Model):

    @api.model
    def create(self, vals, context=None):
        new_id = super(HrChildren, self).create(vals)
        new_object = self.env['hr.employee.children'].browse(new_id.id)
        q = "select count(id) as cant from hr_employee_children WHERE employee_id = %s"
        self._cr.execute(q, ([vals['employee_id']]))
        resul = self._cr.fetchone()[0]
        s = "UPDATE hr_employee SET children=%s WHERE id = %s"
        self._cr.execute(s, (resul, vals['employee_id']))
        return new_id

    @api.multi
    def write(self, vals, context=None):
        q = "select count(id) as cant from hr_employee_children WHERE employee_id = %s"
        self._cr.execute(q, ([self.employee_id.id]))
        resul = self._cr.fetchone()[0]
        s = "UPDATE hr_employee SET children=%s WHERE id = %s"
        self._cr.execute(s, (resul, self.employee_id.id))
        return super(HrChildren, self).write(vals)

    @api.multi
    def unlink(self):
        self.employee_id.children -=1
        return super(HrChildren, self).unlink()

    _name = 'hr.employee.children'
    _description = 'HR Employee Children'

    name = fields.Char("Name", required=True)
    apellido_paterno = fields.Char('Apellido Paterno', required=True)
    apellido_materno = fields.Char('Apellido Materno', required=True)
    date_of_birth = fields.Date("Date of Birth", oldname='dob', required=True)
    employee_id = fields.Many2one('hr.employee', "Employee")
    gender = fields.Selection(selection=GENDER_SELECTION, string='Gender', required=True)
    otro_titulo = fields.Char('Otro titulo')
    name_prefix = fields.Char('Prefijo de Nombre')
    country_id = fields.Many2one('res.country', 'País', default=175)
    state_id = fields.Many2one('res.country.state', 'Departamento')
    province_id = fields.Many2one('res.country.state', 'Provincia')
    district_id = fields.Many2one('res.country.state', 'Distrito')
    lugar_nacimiento = fields.Char('Lugar Nac. (Cod. Ubigeo)')
    segunda_nacionalidad = fields.Many2one('catalogo.nacionalidad.4',string='Otra Nac.')
    tercera_nacionalidad = fields.Many2one('catalogo.nacionalidad.4',string='Otra Nac.')
    tipo_documento = fields.Selection(string="Tipo Documento",selection=[('01', 'DNI'), ('04', 'CARNET DE EXTRANJERIA'),('07', 'PASAPORTE'),('09', 'CARNÉ DE SOLICIT DE REFUGIO')], required=False, )
    nro_documento = fields.Char('N° Documento')
    pais_de_emision = fields.Many2one('catalogo.pais.emisor.documento.26', 'País de Emisión')
    nombre_de_soltera_madre = fields.Char('Nombre de soltera de la Madre')

    vinc_fam = fields.Many2one('catalogo.vinculo.familiar.19', 'Vinculo Familiar')
    tipo_doc = fields.Many2one('catalogo.doc.acred.vinc.familiar.27', 'Tipo de doc que acred. Vínculo')
    nro_doc = fields.Char('N.° de Documento')
    mes_concepcion = fields.Selection(string="Mes Estim Concepción (Sólo Gestante)",
                                      selection=[('1', 'Enero'), ('2', 'Febrero'), ('3', 'Marzo'), ('4', 'Abril'),
                                                 ('5', 'Mayo'), ('6', 'Junio'), ('7', 'Julio'), ('8', 'Agosto'),
                                                 ('9', 'Septiembre'), ('10', 'Octubre'), ('11', 'Noviembre'),
                                                 ('12', 'Diciembre'), ])

    dire_det_ids = fields.One2many(comodel_name="hr.direccion.detalle", inverse_name="dire_det_id",
                                   string="Vinculo Familiar", required=False, ondelete='cascade')

    centro_salud = fields.Char('Indic. Centro Asist EsSalud', help='Direcc.que se considerará para Adscripción', default = '1')

    cod_ldn = fields.Many2one('catalogo.codigo.larga.distancia.nac.29','CÓD LDN')
    numero = fields.Char('Número')
    correo_electronico = fields.Char('Correo Electrónico')



    @api.multi
    def onchange_district(self, district_id):
        if district_id:
            state = self.env['res.country.state'].browse(district_id)
            return {'value': {'lugar_nacimiento': state.code}}
        return {}

    @api.multi
    def onchange_state(self, state_id):
        if state_id:
            return {'value': {'country_id': self.env['res.country.state'].browse(state_id).country_id.id}}
        return {}


class HrEmployee(models.Model):
    def _get_def_vinc(self):
        res = self.env['catalogo.vinculo.familiar.19'].search([('code', '=', '2')])
        return res and res[0] or False

    @api.model
    def create(self, vals, context=None):
        new_id = super(HrEmployee, self).create(vals)
        new_object = self.env['hr.employee'].browse(new_id.id)
        q = "select count(id) as cant from hr_employee_children WHERE employee_id = %s"
        self._cr.execute(q, ([new_object.id]))
        resul = self._cr.fetchone()[0]
        s = "UPDATE hr_employee SET children=%s WHERE id = %s"
        self._cr.execute(s, (resul, new_object.id))
        return new_id

    @api.multi
    def write(self, vals, context=None):
        q = "select count(id) as cant from hr_employee_children WHERE employee_id = %s"
        self._cr.execute(q, ([self.id]))
        resul = self._cr.fetchone()[0]
        s = "UPDATE hr_employee SET children=%s WHERE id = %s"
        self._cr.execute(s, (resul, self.id))
        return super(HrEmployee, self).write(vals)

    _inherit = 'hr.employee'

    gender = fields.Selection([('1', 'Male'), ('2', 'Female'), ('3', 'Otro')], 'Gender', required=True)

    children = fields.Integer('Número de Hijos')
    # conyuge
    fam_spouse = fields.Char("Nombres")
    apellido_paterno_conyuge = fields.Char('Apellido Paterno')
    apellidos_materno_conyuge = fields.Char('Apellido Materno')
    otro_titulo = fields.Char('Otro titulo')
    name_prefix = fields.Char('Prefijo de Nombre')
    conyuge_birthday = fields.Date('Fecha de nacimiento')
    country_id_esp = fields.Many2one('res.country', 'Nacionalidad', default=175)
    country_id = fields.Many2one('res.country', default=175, required=True)
    state_id_esp = fields.Many2one('res.country.state', 'Departamento')
    province_id_esp = fields.Many2one('res.country.state', 'Provincia')
    district_id_esp = fields.Many2one('res.country.state', 'Distrito')
    lugar_nacimiento_esp = fields.Char('Lugar Nac.')
    primera_nacionalidad = fields.Many2one('catalogo.nacionalidad.4',string='Nacionalidad', default=193, required=True)
    segunda_nacionalidad = fields.Many2one('catalogo.nacionalidad.4',string='Otra Nac.')
    tercera_nacionalidad = fields.Many2one('catalogo.nacionalidad.4',string='Otra Nac.')
    tipo_documento = fields.Selection(string="Tipo Documento",selection=[('01', 'DNI'), ('04', 'CARNET DE EXTRANJERIA'),('07', 'PASAPORTE'),('09', 'CARNÉ DE SOLICIT DE REFUGIO')], required=True, )
    tipo_documento_esp = fields.Selection(string="Tipo Documento",selection=[('01', 'DNI'), ('04', 'CARNET DE EXTRANJERIA'),('07', 'PASAPORTE'),('09', 'CARNÉ DE SOLICIT DE REFUGIO')], required=False, )
    nro_documento = fields.Char('N° Documento')
    fam_spouse_tel = fields.Char("Telephone.")
    sexo_esp = fields.Selection(string="Sexo (M/F)", selection=[('1', 'Hombre'), ('2', 'Mujer'), ('3', 'Otro'), ], required=False, )


    # padres
    # fam_spouse_employer = fields.Char("Employer")
    fam_children_ids = fields.One2many(
        'hr.employee.children', 'employee_id', "Children")
    fam_father = fields.Char("Father's Name")
    fam_father_date_of_birth = fields.Date(
        "Date of Birth", oldname='fam_father_dob')
    fam_mother = fields.Char("Mother's Name")
    fam_mother_date_of_birth = fields.Date(
        "Date of Birth", oldname='fam_mother_dob')

    # extra
    pais_de_emision = fields.Many2one('catalogo.pais.emisor.documento.26', 'País de Emisión')
    pais_de_emision_esp = fields.Many2one('catalogo.pais.emisor.documento.26', 'País de Emisión')

    primera_lengua = fields.Char(string='Primera Lengua')
    segunda_lengua = fields.Char(string='Segunda Lengua')
    otra_nacionalidad = fields.Many2one('catalogo.nacionalidad.4',string='Otra Nac.')

    state_id = fields.Many2one('res.country.state', 'Departamento')
    province_id = fields.Many2one('res.country.state', 'Provincia')
    district_id = fields.Many2one('res.country.state', 'Distrito')

    vinc_fam = fields.Many2one('catalogo.vinculo.familiar.19', 'Vinculo Familiar', default=_get_def_vinc)
    tipo_doc = fields.Many2one('catalogo.doc.acred.vinc.familiar.27', 'Tipo de doc que acred. Vínculo')
    nro_doc = fields.Char('N.° de Documento')
    mes_concepcion = fields.Selection(string="Mes Estim Concepción (Sólo Gestante)",
                                      selection=[('1', 'Enero'), ('2', 'Febrero'), ('3', 'Marzo'), ('4', 'Abril'),
                                                 ('5', 'Mayo'), ('6', 'Junio'), ('7', 'Julio'), ('8', 'Agosto'),
                                                 ('9', 'Septiembre'), ('10', 'Octubre'), ('11', 'Noviembre'),
                                                 ('12', 'Diciembre'), ])

    centro_salud = fields.Char('Indic. Centro Asist EsSalud', help='Direcc.que se considerará para Adscripción')

    cod_ldn = fields.Many2one('catalogo.codigo.larga.distancia.nac.29', 'CÓD LDN')

    numero = fields.Char('Número')
    correo_electronico = fields.Char('Correo Electrónico')

    direcciones_ids = fields.One2many('hr.direccion', 'direccion_id',' ', ondelete='cascade')
    ruc_employee = fields.Char('RUC')


    @api.multi
    def onchange_district(self, district_id):
        if district_id:
            state = self.env['res.country.state'].browse(district_id)
            return {'value': {'place_of_birth': state.code}}
        return {}

    @api.multi
    def onchange_state(self, state_id):
        if state_id:
            return {'value': {'country_id': self.env['res.country.state'].browse(state_id).country_id.id}}
        return {}

    @api.multi
    def onchange_district_esp(self, district_id_esp):
        if district_id_esp:
            state = self.env['res.country.state'].browse(district_id_esp)
            return {'value': {'lugar_nacimiento_esp': state.code}}
        return {}

    @api.multi
    def onchange_state_esp(self, state_id_esp):
        if state_id_esp:
            return {'value': {'country_id_esp': self.env['res.country.state'].browse(state_id_esp).country_id.id}}
        return {}

    @api.multi
    def button_vinculo(self):
        id = self.pool.get('ir.ui.view').search(self.env.cr, self.env.uid,
                                                [('model', '=', 'hr.direccion'),
                                                 ('type', '=', 'form')])

        existe = self.pool.get('hr.direccion').search(self.env.cr, self.env.uid,
                                                                   [('direccion_id', '=',
                                                                     self.id)])

        course_form = self.pool.get('ir.ui.view').browse(self.env.cr, self.env.uid, id[0], context=None)

        ctx = dict(
            default_direccion_id=self.id,
        )

        if existe:
            print ('hhh')
            return {
                'name': 'Direcciones',
                'type': 'ir.actions.act_window',
                'res_model': 'hr.direccion',
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
            print ('eee')
            return {
                'name': 'Direcciones',
                'type': 'ir.actions.act_window',
                'res_model': 'hr.direccion',
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'views': [(course_form.id, 'form')],
                'view_id': course_form.id,
                'flags': {'action_buttons': True},
                'context': ctx,
            }


class hr_direccion(models.Model):
    _name = 'hr.direccion'
    # _rec_name = 'name'
    # _description = 'New Description'

    direccion_id = fields.Many2one('hr.employee',  ondelete='cascade')
    direccion_or_ids = fields.One2many('hr.direccion.detalle', 'direccion_or_id',ondelete='cascade')


class hr_direccion_detalle(models.Model):
    _name = 'hr.direccion.detalle'
    # _rec_name = 'name'
    # _description = 'New Description'

    tipo_via = fields.Many2one('catalogo.tipo.via.5', 'Tipo Vía', required=True)
    nombre_via = fields.Char('Nombre Vía', required=True)
    nro = fields.Char('N.°', required=True)
    depto_nro = fields.Char('Dpto N.°')
    interior = fields.Char('Interior')
    mza = fields.Char('Mza')
    nro_lote = fields.Char('N.° Lote')
    nro_kilom = fields.Char('N.° Kilom')
    nro_block = fields.Char('N.° Block')
    nro_etapa = fields.Char('N.° Etapa')
    tipo_zona = fields.Many2one('catalogo.tipo.zona.6', 'Tipo Zona')
    nombre_zona = fields.Char('Nombre Zona')

    country_id = fields.Many2one('res.country','País', default=175, required=True)
    state_id = fields.Many2one('res.country.state', 'Departamento', required=True)
    province_id = fields.Many2one('res.country.state', 'Provincia', required=True)
    district_id = fields.Many2one('res.country.state', 'Distrito', required=True)
    referencia = fields.Text('Referencia')
    direco_estado = fields.Selection(string="Dirección De", selection=[('titular', 'Titular'), ('conyuge', 'Conyuge'), ('hijo', 'Hijo'),], required=True, )

    dire_det_id = fields.Many2one('hr.employee.children', 'Detalle Direcciones', ondelete='cascade')

    direccion_or_id = fields.Many2one('hr.direccion', 'Detalle Direcciones', ondelete='cascade')



    @api.multi
    def onchange_state(self, state_id):
        if state_id:
            return {'value': {'country_id': self.env['res.country.state'].browse(state_id).country_id.id}}
        return {}