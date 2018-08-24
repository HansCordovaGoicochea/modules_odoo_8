# -*- coding: utf-8 -*-
import pytz
import requests
from openerp import fields, models, api, _, SUPERUSER_ID
import openerp.addons.decimal_precision as dp
from openerp.exceptions import except_orm, Warning
# from openerp.exceptions import UserError
import logging
import calendar
import time
import datetime
from datetime import date, timedelta
from datetime import datetime as dt
import os
from lxml import etree
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)

ids = ''
fecha_row_cronograma = ''
fecha_row_contrato = ''
dias_ganados = 30.0
dias_vencidos = 30.0
dias_pendientes = 0.0
lst = []
lst_vencidos = []
lst_pendientes = []


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

    if response.status_code == 200:
        res['error'] = False
        res['data'] = response.json()
    else:
        try:
            res['message'] = response.json()['detail']
        except Exception, e:
            res['error'] = True
    return res


class horario_dia_trabajo(models.Model):
    _name = "horario.dia.trabajo"
    _description = 'Horario Trabajo'
    _rec_name = 'codigo'
    # _order = "identificador desc, id desc"

    jornada = fields.Char(string="Jornada", required=True)
    codigo = fields.Char(string="Código", required=True)
    tolerancia_1turno = fields.Float(string="Tolerancia Turno Diurno (HH:MM 24 horas)", help='El formato es 24 horas HH:MM pero tiene un limite de 23:59')
    hora_inicio = fields.Float(string="Hora Inicio Turno Diurno (HH:MM 24 horas)", required=True, help='El formato es 24 horas HH:MM pero tiene un limite de 23:59')
    descanso = fields.Float(string="Tiempo de Descanso Turno Diurno (HH:MM 24 horas)", required=True, help='El formato es 24 horas HH:MM pero tiene un limite de 23:59')
    hora_fin = fields.Float(string="Hora Fin Turno Diurno (HH:MM 24 horas)", required=True, help='El formato es 24 horas HH:MM pero tiene un limite de 23:59')
    tolerancia_2turno = fields.Float(string="Tolerancia Turno Nocturno (HH:MM 24 horas)", help='El formato es 24 horas HH:MM pero tiene un limite de 23:59')
    segundo_hora_inicio = fields.Float(string="Hora Inicio Turno Nocturno (HH:MM 24 horas)", required=True, help='El formato es 24 horas HH:MM pero tiene un limite de 23:59')
    segundo_descanso = fields.Float(string="Tiempo de Descanso Turno Nocturno (HH:MM 24 horas)", required=True, help='El formato es 24 horas HH:MM pero tiene un limite de 23:59')
    segundo_hora_fin = fields.Float(string="Hora Fin Turno Nocturno (HH:MM 24 horas)", required=True, help='El formato es 24 horas HH:MM pero tiene un limite de 23:59')
    trabajo_x_dia = fields.Float(string="Trabajo por Día")
    trabajo_x_semana = fields.Float(string="Trabajo por semana")
    trabajo_x_mes = fields.Float(string="Trabajo por Mes")
    trabajo_x_anio = fields.Float(string="Trabajo por Año")

    @api.one
    @api.onchange('hora_inicio', 'hora_fin', 'descanso', 'segundo_hora_inicio', 'segundo_descanso', 'segundo_hora_fin')
    def _compute_horas(self):
        primer = (self.hora_inicio - self.hora_fin)
        primer_total = (abs(primer) - self.descanso)

        segundo = (self.segundo_hora_inicio - self.segundo_hora_fin)
        segundo_total = (abs(segundo) - self.segundo_descanso)

        total_horas_turnos = primer_total + segundo_total
        total_horas_entero = int(total_horas_turnos)
        total_horas_decimal = (abs(total_horas_turnos) - abs(int(total_horas_turnos))) * 100
        resultado_regla = (total_horas_decimal * 1) / 60

        resultado_general = total_horas_entero + resultado_regla
        self.trabajo_x_dia = resultado_general or 0.0
        self.trabajo_x_semana = (resultado_general * 5) or 0.0
        self.trabajo_x_mes = (self.trabajo_x_semana * 4) or 0.0
        self.trabajo_x_anio = (self.trabajo_x_mes * 12) or 0.0

    @api.one
    @api.onchange('trabajo_x_dia')
    def _compute_x_dia(self):
        self.trabajo_x_semana = (self.trabajo_x_dia * 5) or 0.0
        self.trabajo_x_mes = (self.trabajo_x_semana * 4) or 0.0
        self.trabajo_x_anio = (self.trabajo_x_mes * 12) or 0.0


class horario_esquema_trabajo(models.Model):
    def onchange_dias(self, cr, uid, ids, array_dias, context=None):
        _logger.info("entro onchange_dias")

        res = {}
        esquemadetalle_ids = []
        product_ids = self.pool.get('horario.dia.trabajo').search(cr, uid, [], limit=array_dias)
        # product_ids = self.pool.get('product.product').search(cr, uid, [], limit=5)
        # for p in self.pool.get('product.product').browse(cr, uid, product_ids):
        for p in range(array_dias):
            # for p in self.pool.get('horario.dia.trabajo').browse(cr, uid, product_ids):
            esquemadetalle_ids.append((0, 0, {'sequence': p + 1}))
        res['esquemadetalle_ids'] = esquemadetalle_ids

        return {'value': res}

    @api.model
    def create(self, vals):
        _logger.info('entre create >>>>>>>>>>>>>>')
        seq = []
        for a in range(self.array_dias):
            b = a + 1
            seq.append(b)
        vals['sequence'] = seq
        if 'esquemadetalle_ids' in vals:
            for idx, line in enumerate(vals['esquemadetalle_ids']):
                line[2]['sequence'] = idx + 1

        return super(horario_esquema_trabajo, self).create(vals)

    _name = "horario.esquema.trabajo"
    _description = "Esquema de trabajo"
    _rec_name = "nombre"

    nombre = fields.Char(string="Nombre", required=True)
    array_dias = fields.Integer(string="# Dias Trabajo", default=1)
    esquemadetalle_ids = fields.One2many('horario.detalle.esquema.trabajo',
                                         'esquema_id',
                                         ondelete='cascade',
                                         copy=True)


class horario_detalle_esquema_trabajo(models.Model):
    @api.onchange('codigo_dias')
    def onchange_place_codigo_dias(self):
        # res = {}
        # if self.jornada_name:
        #     res['domain'] = {'jornada_name': [('jornada_name', '=', self.codigo_dias.id)]}
        # return res
        r = self.env['horario.dia.trabajo'].search([['id', '=', self.codigo_dias.id]])
        if r:
            print (r.jornada)
            self.jornada_name = r.jornada

    _name = "horario.detalle.esquema.trabajo"
    _description = "Detalle esquema de trabajo"
    _rec_name = "sequence"

    sequence = fields.Integer(string='N#', default=1)
    codigo_dias = fields.Many2one('horario.dia.trabajo', 'Dia de Trabajo')
    jornada_name = fields.Char('Jornada')
    esquema_id = fields.Many2one('horario.esquema.trabajo', string='Detalle Esquema de Trabajo', ondelete='cascade')


class horario_hr_employee(models.Model):
    """segundo nombre y apellidos agreados al empleado"""

    @api.model
    def create(self, vals):
        _logger.info('entre create >>>>>>>>>>>>>>')
        # if len(vals['horario_empleado_ids']) < 1:
        #     raise Warning('Error!', 'Porfavor cree al menos un horario en la pestaña (Horario)!!')

        res = super(horario_hr_employee, self).create(vals)
        new_object = self.env['hr.employee'].browse(res.id)
        new_object.write({'stage': '2'})
        return res

    @api.multi
    def terminar_proceso_empleado(self):
        self.write({'stage': '1'})

    # @api.multi
    # def write(self, vals, context=None):
    #     # raise Warning(self)
    #     if int(self.stage) == 3:
    #         vals['stage'] = '4'
    #     return super(horario_hr_employee, self).write(vals)

    # funcion que permite quitar los sheet al modulo
    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        res = models.Model.fields_view_get(self, cr, uid, view_id=view_id, view_type=view_type, context=context,
                                           toolbar=toolbar, submenu=submenu)
        if view_type == 'form':
            doc = etree.XML(res['arch'])
            for sheet in doc.xpath("//sheet"):
                parent = sheet.getparent()
                index = parent.index(sheet)
                for child in sheet:
                    parent.insert(index, child)
                    index += 1
                parent.remove(sheet)
            res['arch'] = etree.tostring(doc)
            # raise Warning(cr)
        return res

    @api.onchange('primer_nombre', 'segundo_nombre', 'apellido_paterno', 'apellido_materno')
    def _onchange_nombre_completo(self):
        self.name = ''
        for table in self:
            if table.primer_nombre or table.segundo_nombre or table.apellido_paterno or table.apellido_materno:
                primer = table.primer_nombre or ''
                segundo = table.segundo_nombre or ''
                paterno = table.apellido_paterno or ''
                materno = table.apellido_materno or ''

            else:
                primer = ''
                segundo = ''
                paterno = ''
                materno = ''

            self.name += str(primer) + ' ' + str(segundo) + ' ' + str(paterno) + ' ' + str(materno)

    # @api.v8
    # def _judiciales_count(self, cr, uid, ids, field_name, arg, context=None):
    #     Contract = self.pool['hr.judiciales']
    #     return {
    #         employee_id: Contract.search_count(cr, SUPERUSER_ID, [('employee_id', '=', employee_id)], context=context)
    #         for employee_id in ids
    #     }

    def _def_address_home(self):
        user = self.pool.get('res.users').browse(self._cr, self._uid, [self._uid])[0]
        return user.company_id.partner_id.id

    _inherit = "hr.employee"

    address_home_id = fields.Many2one('res.partner', 'Dirección Particular', default=_def_address_home)

    primer_nombre = fields.Char(string='Primer Nombre', required=True)
    segundo_nombre = fields.Char(string="Segundo Nombre")
    apellido_paterno = fields.Char(string="Apellido Paterno", required=True)
    apellido_materno = fields.Char(string="Apellido Materno", required=True)
    # nombre_completo = fields.Char(compute="_compute_display_nombrecito")

    horas_extra = fields.Float(string="Horas Extra", compute='_traer_horas_')
    horario_empleado_ids = fields.One2many('horario.horario.empleado',
                                           'horario_empleado_id',
                                           ondelete='cascade',
                                           copy=True)

    horario_marcacion_ids = fields.One2many('horario.marcaciones.empleado',
                                            'horario_marcacion_id', copy=True)

    horario_asistencias_empleado_ids = fields.One2many('horario.asistencias',
                                                       'employee_id', copy=True)

    horario_horas_extra_ids = fields.One2many('horas.extra',
                                              'employee_id', copy=True)

    horas_extra_empleado_ids = fields.One2many('horas.extra.empleado',
                                               'employee_id', copy=True)

    horario_vacaciones_ids = fields.One2many('horario.vacaciones.x.empleado',
                                             'employee_id', copy=True)

    afp = fields.Many2one('hr.afps', 'AFP', required=True)
    cupps = fields.Char('CUSPP')
    situacion_educativa = fields.Many2one('catalogo.situacion.educativa.9')
    discapacidad = fields.Boolean('Discapacidad')
    sctr_pension = fields.Selection(string='SCTR Pensión', selection=[('0', 'Ninguno'),
                                                                      ('1', 'ONP'),
                                                                      ('2', 'CIA PRIVADA')])
    ocupacion = fields.Many2one(comodel_name="catalogo.ocupacion.10", required=True)
    es_sindicalizado = fields.Boolean('Sindicalizado')
    situacion = fields.Selection(string='Situación', selection=[('0', 'BAJA'),
                                                                ('1', 'ACTIVO O SUBSIDIADO'),
                                                                ('2', 'SIN VINC. LAB. CON CONC PEND POR LIQUIDAR'),
                                                                ('3', 'SUSPENSIÓN PERFECTA DE LABORES')])

    situacion_especial = fields.Selection(string='Sit. Especial', selection=[('0', 'NINGUNO'),
                                                                             ('1', 'TRABAJADOR DE DIRECCION'),
                                                                             ('2', 'TRABAJADOR DE CONFIANZA')])
    categoria_ocupacional = fields.Many2one('catalogo.categoria.ocupacional.24', 'Categoria Ocupacional', required=True)

    doble_tributacion = fields.Selection(string='Convenio para evitar Doble Tributación', selection=[('0', 'NINGUNO'),
                                                                                                     ('1', 'CANADA'),
                                                                                                     ('2', 'CHILE'),
                                                                                                     ('3', 'CAN'),
                                                                                                     ('4', 'BRASIL')])

    tipo_trabajador = fields.Many2one('catalogo.tipo.trabajador.8', 'Tipo de Trabajador', required=True)
    categoria_trabajador = fields.Selection(string='Categoría', selection=[('1', 'Trabajador'),
                                                                           ('2', 'Pensionista'),
                                                                           ('4', 'Personal de Terceros'),
                                                                           ('5',
                                                                            'Personal en Formación-modalidad formativa laboral')], required=True)
    concluidos_ids = fields.One2many('hr.estudios.concluidos', 'employee_id', 'Estudios Superiores Concluidos', required=True)
    judiciales_ids = fields.One2many('hr.judiciales', 'employee_id', 'Judiciales')

    seleccionar_tareo = fields.Selection(string='Seleccion de Tareo', selection=[('manual', 'Reg. Manual'),
                                                                                 ('conductor', 'Prog. Coductores'),
                                                                                 ('reloj', 'Reloj Marcador'),
                                                                                 ('ninguno', 'Ninguno')],
                                         default='conductor', required=True)

    documento_empleado_ids = fields.One2many('hr.documentos.empleado',
                                           'employee_id')

    vehicle_distance = fields.Float('Movilidad S/.')

    # judiciales_count = fields.Char(string="Judiciales Count")

    stage = fields.Selection([
        ('1', 'Informacion Personal'),
        ('2', 'Contrato'),
        ('3', 'Horarios'),
        ('4', 'Asistencias'),
        ('5', 'Rec. Vacaciones'),
        ('6', 'Judiciales'),
    ], 'Status', select=True, default='1', help='Procesos de registro de empleado')


    # @api.one
    # @api.depends()
    # def judiciales_count(self):
    #     print ('count judiciales')
    #     employee_id = self.env['hr.judiciales'].search_count([('employee_id', '=', self.id)])
    #     self.judiciales_count = '10'

    @api.one
    def _traer_horas_(self):
        # q = "SELECT sum(horas_extra_empleado) AS ho FROM horas_extra_empleado WHERE employee_id = %s"
        q = "SELECT (SELECT COALESCE(SUM(horas), 0) AS ho FROM horas_extra WHERE employee_id = %s AND  motivo=5 AND estado_pag=False) - (SELECT COALESCE(SUM(horas), 0) AS ho FROM horas_extra WHERE employee_id = %s AND  motivo=7 AND estado_pag=False) as total"
        self._cr.execute(q, (self.id, self.id))
        res = self._cr.fetchone()[0]
        self.horas_extra = res

    @api.multi
    def read(self, fields=None, load='_classic_read'):
        global ids
        id = 0
        for record in self:
            ids = record.id
        print (ids)
        res = super(horario_hr_employee, self).read(fields=fields, load=load)
        return res

    @api.onchange('identification_id')
    def onchange_doc_number(self):
        self.button_update_document()

    @api.one
    def button_update_document(self):
        if self.country_id.name == u'Perú':
            if self.identification_id and len(self.identification_id) != 8:
                raise Warning('El Dni debe tener 8 caracteres')
            else:
                d = get_data_doc_number(
                    'dni', self.identification_id, format='json')
                if not d['error']:
                    d = d['data']
                    print (d)
                    nom = d['nombres']
                    lst = nom.split(' ')
                    if lst[0] == 'DEL':
                        indices = [0, 1]
                        self.primer_nombre = " ".join([e for i, e in enumerate(lst) if i in indices])
                    else:
                        self.primer_nombre = '%s' % (lst[0])

                    if len(lst) > 1 and lst[0] != 'DEL':
                        self.segundo_nombre = " ".join(lst[1:])
                    elif len(lst) > 1 and lst[0] == 'DEL':
                        self.segundo_nombre = " ".join(lst[2:])
                    else:
                        self.segundo_nombre = '%s' % ("")

                    self.apellido_paterno = '%s' % (d['ape_paterno'])
                    self.apellido_materno = '%s' % (d['ape_materno'])

    @api.multi
    def load_pantalla_empresa_anterior(self):
        print ('entre')
        id = self.pool.get('ir.ui.view').search(self.env.cr, self.env.uid,
                                                [('model', '=', 'hr.liquidacion.empresa.anterior'),('type', '=', 'form')])

        print (id)

        existeEspecifica = self.pool.get('hr.liquidacion.empresa.anterior').search(self.env.cr, self.env.uid,[('employee_id', '=',self.id)])

        print (existeEspecifica)

        course_form = self.pool.get('ir.ui.view').browse(self.env.cr, self.env.uid, id[0], context=None)
        print (course_form)

        ctx = dict(
            default_employee_id=self.id,
        )
        print (ctx)

        if existeEspecifica:
            return {
                'name': 'Empresa Anterior',
                'type': 'ir.actions.act_window',
                'res_model': 'hr.liquidacion.empresa.anterior',
                'res_id': existeEspecifica[0],
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
                'name': 'Empresa Anterior',
                'type': 'ir.actions.act_window',
                'res_model': 'hr.liquidacion.empresa.anterior',
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'views': [(course_form.id, 'form')],
                'view_id': course_form.id,
                'flags': {'action_buttons': True},
                'context': ctx,
            }

class hr_estudios_concluidos(models.Model):
    _name = 'hr.estudios.concluidos'
    _rec_name = 'codigo_inst_educativa'
    # _description = 'New Description'

    employee_id = fields.Many2one('hr.employee', string='Empleado', ondelete='cascade')
    superior_completa = fields.Many2one('catalogo.situacion.educativa.9')
    ind_superior_completa = fields.Selection([('1', 'Si'), ('0', 'No')], 'Ind. Educ. Sup. Completa', default='0')
    codigo_inst_educativa = fields.Many2one('catalogo.instituciones.educativas.34')
    anio_egreso = fields.Date('Año de Egreso')


class horario_horario_empleado(models.Model):
    """horario x empleado de acuerdo a un esquema"""

    # ejecutar cada fin de año
    @api.model
    def _cron_refresh_horario_ref(self):
        self._onchange_horario_ref()

    @api.multi
    def _onchange_horario_ref(self):
        order_by = "fecha_inicio"
        print('Actualizandooo Horariosq!!!!!!!!')
        # employees = self.env['hr.employee'].search([['active', '=', True], ['id', '=', 25]])
        employees = self.env['hr.employee'].search([['active', '=', True]])
        for emp in employees:
            horarios_emp = self.search([['horario_empleado_id', '=', emp.id]], limit=1, order='fecha_inicio desc')
            if horarios_emp:
                ultima_fecha = date(int(horarios_emp.fecha_inicio[0:4]), int(horarios_emp.fecha_inicio[5:7]),int(horarios_emp.fecha_inicio[-2:]))
                # ultimo mes y dia del año actual
                fecha_anio = date(int(ultima_fecha.year)+1, int(1),int(1))
                dateMonthEnd = "%s-%s-%s" % (fecha_anio.year, 12, calendar.monthrange(fecha_anio.year, 12)[1])
                filtro_fin_de_anio = "%s-%s-%s" % (ultima_fecha.year, 12, calendar.monthrange(fecha_anio.year, 12)[1])

                # resta del mes elegido con ultimo mes y dia del año actual
                d1 = date(int(fecha_anio.year), int(1), int(1))
                d2 = date(int(dateMonthEnd[0:4]), int(dateMonthEnd[5:7]), int(dateMonthEnd[-2:]))
                diff = d2 - d1
                print (diff)
                horario_empleado = self.env['horario.x.empleado'].search([['empleado', '=', emp.id], ['fechas','=', filtro_fin_de_anio]], limit=1)
                esquema_detalle1 = self.env['horario.detalle.esquema.trabajo'].search([['esquema_id', '=', horarios_emp.esquema.id]], limit=1, order='id desc')
                if horario_empleado and esquema_detalle1:
                    if horario_empleado.sequencia == esquema_detalle1.sequence:
                        dia_trabajo_mas = 1
                    else:
                        dia_trabajo_mas = int(horario_empleado.sequencia) + 1
                    esquema_detalle = self.env['horario.detalle.esquema.trabajo'].search([['esquema_id', '=', horarios_emp.esquema.id], ['sequence', '=', dia_trabajo_mas]], limit=1)
                    ultimo_id_creado = self.create({
                        'esquema': horarios_emp.esquema.id,
                        'fecha_inicio': fecha_anio.strftime('%Y-%m-%d'),
                        'dia_trabajo': esquema_detalle.id,
                        'horario_empleado_id': emp.id,
                    })

    # funcion que permite darle un filtro para los dias de trabajo
    @api.onchange('esquema')
    def onchange_place(self):
        res = {}
        if self.esquema:
            res['domain'] = {'dia_trabajo': [('esquema_id', '=', self.esquema.id)]}
        return res

    _name = "horario.horario.empleado"
    _order = "fecha_inicio desc"

    esquema = fields.Many2one('horario.esquema.trabajo', 'Esquema de Trabajo', required=True)
    fecha_inicio = fields.Date(string="Fecha Inicio", required=True)
    dia_trabajo = fields.Many2one('horario.detalle.esquema.trabajo', 'Dia de Trabajo', required=True)
    horario_empleado_id = fields.Many2one('hr.employee', string='Detalle Empleado', ondelete='cascade')
    horario_x_empleado_ids = fields.One2many('horario.x.empleado', 'horario_x_empleado_id', 'horario emp')

    # metodo sobreescrito para poder crer la tabla horario_x_empleado
    @api.model
    def create(self, vals, context=None):
        print ('---------------')
        print (vals)
        print ('---------------')
        new_id = super(horario_horario_empleado, self).create(vals)
        new_object = self.env['horario.horario.empleado'].browse(new_id.id)
        if vals['esquema'] and vals['fecha_inicio'] and vals['dia_trabajo']:
            new_object.write({'fecha_inicio': vals['fecha_inicio'], })
            # ultimo mes y dia del año actual
            fecha_anio = date(int(vals['fecha_inicio'][0:4]), int(vals['fecha_inicio'][5:7]), int(vals['fecha_inicio'][-2:]))
            # today = datetime.datetime.now()
            dateMonthEnd = "%s-%s-%s" % (fecha_anio.year, 12, calendar.monthrange(fecha_anio.year, 12)[1])

            # resta del mes elegido con ultimo mes y dia del año actual
            d1 = date(int(vals['fecha_inicio'][0:4]), int(vals['fecha_inicio'][5:7]), int(vals['fecha_inicio'][-2:]))
            d2 = date(int(dateMonthEnd[0:4]), int(dateMonthEnd[5:7]), int(dateMonthEnd[-2:]))
            # print (d2 - d1)
            diff = d2 - d1
            print (diff)
            # para borrar de la fecha seleccionada hasta el ultimo dia del año
            for j in range(0, (int(str(diff).split(' ', 1)[0]) + 1), 1):
                # print ('entreeeeeeeeeeee')
                diasDelete = timedelta(days=j)
                fechaDelete = d1 + diasDelete
                # self.env['horario.x.empleado'].write({'fecha_inicio': vals['fecha_inicio']})
                self._cr.execute(
                    """ DELETE FROM horario_x_empleado WHERE fechas=%s AND empleado=%s AND horario_x_empleado_id=%s""",
                    (fechaDelete, vals['horario_empleado_id'], new_object.id))

            # crear las variables para fechas y los codigo de trabajo
            aa = vals['dia_trabajo']
            self._cr.execute("""SELECT sequence FROM horario_detalle_esquema_trabajo WHERE id = %s""", [aa])
            resultado = self._cr.fetchone()
            inicio = resultado[0]
            to = vals['esquema']
            self._cr.execute("""SELECT array_dias FROM horario_esquema_trabajo WHERE id = %s""", [to])
            resultado_to = self._cr.fetchone()
            to_dias = resultado_to[0]
            for i in range(0, (int(str(diff).split(' ', 1)[0]) + 1), 1):
                dias = timedelta(days=i)
                fecha = d1 + dias
                # sacar todos los dias de trabajo con su codigo
                self._cr.execute(
                    """SELECT det.sequence, codigo FROM horario_horario_empleado he INNER JOIN horario_esquema_trabajo et ON he.esquema = et.id INNER JOIN horario_detalle_esquema_trabajo det INNER JOIN horario_dia_trabajo dt ON det.codigo_dias = dt.id ON et.id = det.esquema_id WHERE he.horario_empleado_id = %s ORDER BY sequence""",
                    [vals['horario_empleado_id']])
                c = self._cr.dictfetchall()
                # c = self.env['horario.dia.trabajo'].search_read([], ['codigo'])
                a = [element for element in c if element['sequence'] == inicio]
                # para poder sacar solo el codigo
                for item in a:
                    cod = item['codigo']
                    sequencia = item['sequence']
                # print (employee_id.id)
                valores = \
                    {
                        'empleado': vals['horario_empleado_id'],
                        'fechas': fecha,
                        'codigo_trabajo': cod,
                        'sequencia': sequencia,
                        'horario_x_empleado_id': new_object.id
                    }
                # print (aa)
                if to_dias != inicio:
                    inicio += 1
                    # print (inicio)
                else:
                    inicio = 1
                self.env['horario.x.empleado'].create(valores)

        return new_id

    # metodo sobreescrito para poder actualizar todos los registros a partir de la fecha
    @api.multi
    def write(self, vals, context=None):
        today = datetime.datetime.now()
        dateMonthEnd = "%s-%s-%s" % (today.year, 12, calendar.monthrange(today.year, today.month)[1])

        d1 = date(int(vals['fecha_inicio'][0:4]), int(vals['fecha_inicio'][5:7]), int(vals['fecha_inicio'][-2:]))
        d2 = date(int(dateMonthEnd[0:4]), int(dateMonthEnd[5:7]), int(dateMonthEnd[-2:]))
        diff = d2 - d1

        # para borrar de la fecha seleccionada hasta el ultimo dia del año
        for j in range(0, (int(str(diff).split(' ', 1)[0]) + 1), 1):
            # print ('entreeeeeeeeeeee')
            diasDelete = timedelta(days=j)
            fechaDelete = d1 + diasDelete
            self._cr.execute(
                """ DELETE FROM horario_x_empleado WHERE fechas=%s AND empleado=%s AND horario_x_empleado_id=%s""",
                (fechaDelete, self.horario_empleado_id.id, self.id))

        aa = self.dia_trabajo.sequence
        to = self.esquema.array_dias
        for i in range(0, (int(str(diff).split(' ', 1)[0]) + 1), 1):
            dias = timedelta(days=i)
            fecha = d1 + dias
            # sacar todos los dias de trabajo con su codigo
            self._cr.execute(
                """SELECT det.sequence, codigo FROM horario_horario_empleado he INNER JOIN horario_esquema_trabajo et ON he.esquema = et.id INNER JOIN horario_detalle_esquema_trabajo det INNER JOIN horario_dia_trabajo dt ON det.codigo_dias = dt.id ON et.id = det.esquema_id WHERE he.horario_empleado_id = %s ORDER BY sequence""",
                [self.horario_empleado_id.id])
            c = self._cr.dictfetchall()
            # c = self.env['horario.dia.trabajo'].search_read([], ['codigo'])
            # a = [element for element in c if element['sequence'] == inicio]
            a = [element for element in c if element['sequence'] == aa]
            # para poder sacar solo el codigo
            for item in a:
                cod = item['codigo']
                sequencia = item['sequence']
            valores = \
                {
                    'empleado': self.horario_empleado_id.id,
                    'fechas': fecha,
                    'codigo_trabajo': cod,
                    'sequencia': sequencia,
                    'horario_x_empleado_id': self.id
                }
            if to != aa:
                aa += 1
            else:
                aa = 1
            # print (vals)
            self.env['horario.x.empleado'].create(valores)

        return super(horario_horario_empleado, self).write(vals)

    # @api.onchange('esquema', 'fecha_inicio', 'dia_trabajo')
    # def _change_horario(self):
    #     self.agregarHorario()

    # funcion sobreescrita para eliminar tambien los datos relacionados con la tabla
    @api.multi
    def unlink(self):
        today = datetime.datetime.now()
        dateMonthEnd = "%s-%s-%s" % (today.year, 12, calendar.monthrange(today.year, today.month)[1])

        d1 = date(int(self.fecha_inicio[0:4]), int(self.fecha_inicio[5:7]), int(self.fecha_inicio[-2:]))
        d2 = date(int(dateMonthEnd[0:4]), int(dateMonthEnd[5:7]), int(dateMonthEnd[-2:]))
        diff = d2 - d1

        # para borrar de la fecha seleccionada hasta el ultimo dia del año
        # self.env['horario.x.empleado'].write({'fecha_inicio': vals['fecha_inicio']})
        for j in range(0, (int(str(diff).split(' ', 1)[0]) + 1), 1):
            print ('entreeeeeeeeeeee')
            diasDelete = timedelta(days=j)
            fechaDelete = d1 + diasDelete
            # self.env['horario.x.empleado'].write({'fecha_inicio': vals['fecha_inicio']})
            self._cr.execute(
                """ DELETE FROM horario_x_empleado WHERE fechas=%s AND empleado=%s AND horario_x_empleado_id=%s""",
                (fechaDelete, self.horario_empleado_id.id, self.id))
        return super(horario_horario_empleado, self).unlink()


class horario_x_empleado(models.Model):
    """creada a partir de un horario de empleado"""
    _name = "horario.x.empleado"

    fechas = fields.Date(string="Fechas")
    codigo_trabajo = fields.Char(string="Codigo dia de Trabajo")
    sequencia = fields.Integer(string="Secuencia")
    empleado = fields.Many2one('hr.employee', string='Detalle Empleado')
    horario_x_empleado_id = fields.Many2one('horario.horario.empleado', string='Detalle Empleado', ondelete='cascade')


class horario_marcaciones_empleado(models.Model):
    """Marcaciones del empleado"""

    def default_get_jornada(self):
        self._cr.execute(
            """SELECT id FROM horario_horario_empleado WHERE horario_empleado_id = %s ORDER BY id DESC LIMIT 1""",
            [ids])

        id_jor = self._cr.fetchone()

        if id_jor:
            id_hor = id_jor[0]
            print (id_hor)
        else:
            raise Warning('Debe crear un Horario')

        today = datetime.datetime.now()
        fecha_actual = "%s-%s-%s" % (today.year, str(today.month).zfill(2), today.day)
        self._cr.execute(
            """SELECT dt.jornada FROM horario_horario_empleado he INNER JOIN horario_x_empleado hxe ON he.id = hxe.horario_x_empleado_id INNER JOIN horario_dia_trabajo dt ON hxe.codigo_trabajo = dt.codigo WHERE horario_empleado_id = %s AND hxe.fechas=%s AND hxe.horario_x_empleado_id = %s""",
            (ids, fecha_actual, id_hor))
        jornada = self._cr.fetchone()
        print (ids, fecha_actual)
        if jornada:
            return jornada[0]

    _name = 'horario.marcaciones.empleado'
    _rec_name = 'horario_marcacion_id'
    _description = 'Marcaciones de empleados por supervisor'

    fecha = fields.Date(string="Fecha", default=lambda *a: dt.now().strftime('%Y-%m-%d'))
    jornada_name = fields.Char(string="Jornada", default=default_get_jornada)
    hora_entrada = fields.Float(string='1° Hora de Entrada')
    hora_salida = fields.Float(string='1° Hora de Salida')
    segunda_hora_entrada = fields.Float(string='2° Hora de Entrada')
    segunda_hora_salida = fields.Float(string='2° Hora de Salida')
    horario_marcacion_id = fields.Many2one('hr.employee', string='Empleado', ondelete='cascade')

    # funcion que permite obtener las horas de entrada y salida dependiendo si la fecha ya esta registrada
    @api.onchange('fecha')
    def _onchange_fecha(self):
        self._cr.execute(
            """SELECT id FROM horario_horario_empleado WHERE horario_empleado_id = %s ORDER BY id DESC LIMIT 1""",
            [ids])

        id_jor = self._cr.fetchone()
        if id_jor:
            id_hor = id_jor[0]
            print (id_hor)
        else:
            raise Warning('Debe crear un Horario')

        self._cr.execute(
            """SELECT dt.jornada FROM horario_horario_empleado he INNER JOIN horario_x_empleado hxe ON he.id = hxe.horario_x_empleado_id INNER JOIN horario_dia_trabajo dt ON hxe.codigo_trabajo = dt.codigo WHERE horario_empleado_id = %s AND hxe.fechas=%s AND hxe.horario_x_empleado_id = %s""",
            (ids, self.fecha, id_hor))
        jornada = self._cr.fetchone()
        print (ids, self.fecha)
        if jornada:
            self.jornada_name = jornada[0]

        fecha = self.env['horario.marcaciones.empleado'].search([['fecha', '=', self.fecha],
                                                                 ['horario_marcacion_id', '=', ids]])

        if fecha.id:
            # if fecha.fecha == self.fecha:
            #     raise except_orm(_('Error!'),
            #                      _("La fecha ya esta registrada no puede registrarse otra vez !!"))
            if fecha.hora_entrada:
                self.hora_entrada = fecha.hora_entrada
            if fecha.hora_salida:
                self.hora_salida = fecha.hora_salida
            if fecha.segunda_hora_entrada:
                self.segunda_hora_entrada = fecha.segunda_hora_entrada
            if fecha.segunda_hora_salida:
                self.segunda_hora_salida = fecha.segunda_hora_salida

        else:
            self.hora_entrada = 0.0
            self.hora_salida = 0.0
            self.segunda_hora_entrada = 0.0
            self.segunda_hora_salida = 0.0


class horario_asistencias(models.Model):
    """Para controlar las asistencias"""

    @api.one
    @api.onchange('fecha_inicio', 'fecha_fin')
    def _check_date(self):
        for holiday in self:
            domain = [
                ('fecha_inicio', '<=', holiday.fecha_fin),
                ('fecha_fin', '>=', holiday.fecha_inicio),
                ('employee_id', '=', holiday.employee_id.id),
            ]
            nholidays = self.search_count(domain)
            print ('nholidays>>>>>>>>>>',str(nholidays))
            if nholidays > 0:
                # return False
                raise Warning('Error!', '¡No puedes tener 2 fechas que se superponen el mismo día!!!')
        return True

    @api.multi
    def ir_al_empleado_2(self):
        id = self.pool.get('ir.ui.view').search(self.env.cr, self.env.uid,
                                                [('model', '=', 'hr.employee'),
                                                 ('type', '=', 'form')])

        existeEspecifica = self.pool.get('hr.employee').search(self.env.cr, self.env.uid,
                                                               [('id', '=', self.employee_id.id)])
        # raise  Warning(id)
        course_form = self.pool.get('ir.ui.view').browse(self.env.cr, self.env.uid, id[0], context=None)

        ctx = dict(
            default_employee_id=self.employee_id.id,
        )
        return {
            'name': 'Empleado',
            'type': 'ir.actions.act_window',
            'res_model': 'hr.employee',
            'res_id': existeEspecifica[0],
            'view_type': 'form',
            'view_mode': 'form',
            # 'target': 'current',
            # 'views': [(course_form.id, 'form')],
            # 'view_id': course_form.id,
            # 'flags': {'action_buttons': True},
            'context': ctx,
        }

    # funcion sobreescrita que permite no volver a registrar la mis fechas ya registradas
    @api.model
    def create(self, vals):
        _logger.info('entre create >>>>>>>>>>>>>>')
        # if len(vals['horario_empleado_ids']) < 1:
        #     raise Warning('Error!', 'Porfavor cree al menos un horario en la pestaña (Horario)!!')
        #     if new_object:

        domain = [
            ('fecha_inicio', '<=', vals['fecha_fin']),
            ('fecha_fin', '>=', vals['fecha_inicio']),
            ('employee_id', '=', vals['employee_id']),
        ]
        nholidays = self.search_count(domain)
        print ('nholidays>>>>>>>>>>', str(nholidays))
        if nholidays > 0:
            # return False
            raise Warning('Error!', '¡No puedes tener 2 fechas que se superponen el mismo día!!!')

        linea_em = self.env['horario.asistencias'].search([['employee_id','=',vals['employee_id']]])[0]
        if linea_em.fecha_inicio == vals['fecha_inicio'] and linea_em.fecha_fin == vals['fecha_fin']:
            raise except_orm(_('Error!'),_("Fechas Ya registradas !!"))
        res = super(horario_asistencias, self).create(vals)
        new_object = self.env['hr.employee'].browse(res.employee_id.id)
        new_object.write({'stage': '5'})
        return res

    # @api.multi
    # def read(self, fields=None, load='_classic_read'):
    #     global ids
    #     id = 0
    #     # idis = []
    #     for record in self:
    #         ids = record.id
    #         # idis.append(ids)
    #     print ('><<<<<<<<<',str(ids))
    #     res = super(horario_asistencias, self).read(fields=fields, load=load)
    #     return res

    # funcion que permite quitar los sheet al modulo
    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        res = models.Model.fields_view_get(self, cr, uid, view_id=view_id, view_type=view_type, context=context,
                                           toolbar=toolbar, submenu=submenu)
        if view_type == 'form':
            doc = etree.XML(res['arch'])
            for sheet in doc.xpath("//sheet"):
                parent = sheet.getparent()
                index = parent.index(sheet)
                for child in sheet:
                    parent.insert(index, child)
                    index += 1
                parent.remove(sheet)
            res['arch'] = etree.tostring(doc)
        return res

    # verificar si existe contrato
    def _default_fecha_inicio(self):

        q = "SELECT date_start FROM hr_contract WHERE employee_id = %s ORDER BY date_start DESC LIMIT 1"
        self._cr.execute(q, [ids])
        r = self._cr.fetchone()
        if not r:
            raise except_orm(_('Error!'),
                             _("No existe contrato !!"))
        else:
            return r[0]

    # metodo para pasar las fechas a la tabla tambien por ahora las horas de entrada y salida
    @api.model
    def _cron_refresh_asistencias(self):
        self._onchange_fechas_action()

    @api.multi
    def _onchange_fechas_action(self):
        order_by = "fecha_inicio"
        print('Actualizandooo Asistencias!!!!!!!!')
        # employees = self.env['hr.employee'].search([['active', '=', True],['id', '=', 25]])
        employees = self.env['hr.employee'].search([['active', '=', True]])
        for emp in employees:
            asistencias_emp = self.search([['employee_id', '=', emp.id]], limit=1, order='fecha_inicio desc')
            if asistencias_emp:
                print('Entre 1° if')
                ultima_fecha = date(int(asistencias_emp.fecha_fin[0:4]), int(asistencias_emp.fecha_fin[5:7]), int(asistencias_emp.fecha_fin[-2:]))
                print ('ultima_fecha old---->', str(ultima_fecha))
                ultima_fecha = ultima_fecha + relativedelta(months=1)
                print ('ultima_fecha new---->',str(ultima_fecha))
                print ('ultima_fecha month---->',str(ultima_fecha.month))
                print ('ultima_fecha year---->',str(ultima_fecha.year))
                dateMonthStart = "%s-%s-01" % (int(ultima_fecha.year), str(ultima_fecha.month).zfill(2))
                dateMonthEnd = "%s-%s-%s" % (int(ultima_fecha.year), str(ultima_fecha.month).zfill(2), calendar.monthrange(int(ultima_fecha.year), int(ultima_fecha.month))[1])
                print('-------------')
                print (dateMonthStart, dateMonthEnd)
                print('-------------')
                horario_empleado = self.env['horario.horario.empleado'].search([['horario_empleado_id','=',emp.id]], limit=1, order=order_by)
                horario_asistencias_ids = []
                if dateMonthStart and dateMonthEnd and horario_empleado:  # si existen valores
                    print('Entre 2° if')
                    print('Entre generar asistencias')
                    d1 = date(int(dateMonthStart[0:4]), int(dateMonthStart[5:7]), int(dateMonthStart[-2:]))
                    d2 = date(int(dateMonthEnd[0:4]), int(dateMonthEnd[5:7]), int(dateMonthEnd[-2:]))
                    diff = d2 - d1  # restas las fechas
                    lst_f = []

                    self._cr.execute(
                        """SELECT dt.hora_inicio,dt.hora_fin FROM horario_detalle_esquema_trabajo edt INNER JOIN horario_esquema_trabajo et ON edt.esquema_id = et.id INNER JOIN horario_horario_empleado he ON he.esquema = et.id INNER JOIN horario_dia_trabajo dt ON dt.id = edt.codigo_dias WHERE he.horario_empleado_id = %s""",
                        [emp.id])
                    resultado_to = self._cr.dictfetchall()
                    # print (resultado_to)
                    ini = 1
                    resul_count = len(resultado_to)
                    for j in range(0, (int(str(diff).split(' ', 1)[0]) + 1), 1):
                        dias = timedelta(days=j)
                        fechas = d1 + dias
                        lst_f.append(fechas)  # almacenar todas la fechas en un array
                        self._cr.execute(
                            """SELECT hxe.fechas, dt.jornada, codigo,hora_inicio, hora_fin, segundo_hora_inicio, segundo_hora_fin FROM horario_horario_empleado he INNER JOIN horario_x_empleado hxe ON he.id = hxe.horario_x_empleado_id INNER JOIN horario_dia_trabajo dt ON hxe.codigo_trabajo = dt.codigo WHERE horario_empleado_id = %s AND hxe.fechas = %s""",
                            (emp.id, fechas))
                        resultado_to2 = self._cr.dictfetchall()
                        for e in resultado_to2:
                            fec = e['fechas']
                            hora_entrada = e['hora_inicio']
                            hora_salida = e['hora_fin']
                            segunda_hora_entrada = e['segundo_hora_inicio']
                            segunda_hora_salida = e['segundo_hora_fin']
                            codigo = e['codigo']

                        horario_asistencias_ids.append((0, 0, {
                            'fecha': fec,
                            'hora_entrada': hora_entrada,
                            'hora_salida': hora_salida,
                            'segunda_hora_entrada': segunda_hora_entrada,
                            'segunda_hora_salida': segunda_hora_salida,
                            'codigo_dias': codigo
                        }))
                        if resul_count != ini:
                            ini += 1
                            # print (ini)
                        else:
                            ini = 1
                    # print (horario_asistencias_ids)
                    self.create({
                        'fecha_inicio': dateMonthStart,
                        'fecha_fin': dateMonthEnd,
                        'horario_asistencias_ids':horario_asistencias_ids,
                        'employee_id':emp.id,
                    })
                        # asistencias_emp.horario_asistencias_ids = horario_asistencias_ids

    @api.onchange('fecha_inicio', 'fecha_fin')
    def _onchange_fechas(self):
        order_by = "fecha_inicio"
        horario_empleado = self.env['horario.horario.empleado'].search([['horario_empleado_id','=',self.employee_id.id]], limit=1, order=order_by)
        horario_asistencias_ids = []
        if self.fecha_inicio and self.fecha_fin:  # si existen valores
            if self.fecha_fin <= self.fecha_inicio:  # si las fechas son iguales o menos que el inicio
                raise except_orm(_('Error!'),
                                 _("La fecha de FIN no puede ser menor que la de INICIO !!"))
            elif self.fecha_inicio < horario_empleado.fecha_inicio:
                raise except_orm(_('Error!'),
                                 _("Elija una fecha dentro del Horario seleccionado anteriormente !"))
            else:
                d1 = date(int(self.fecha_inicio[0:4]), int(self.fecha_inicio[5:7]), int(self.fecha_inicio[-2:]))
                d2 = date(int(self.fecha_fin[0:4]), int(self.fecha_fin[5:7]), int(self.fecha_fin[-2:]))
                diff = d2 - d1  # restas las fechas
                lst_f = []

                self._cr.execute(
                    """SELECT dt.hora_inicio,dt.hora_fin FROM horario_detalle_esquema_trabajo edt INNER JOIN horario_esquema_trabajo et ON edt.esquema_id = et.id INNER JOIN horario_horario_empleado he ON he.esquema = et.id INNER JOIN horario_dia_trabajo dt ON dt.id = edt.codigo_dias WHERE he.horario_empleado_id = %s""",
                    [self.employee_id.id])
                resultado_to = self._cr.dictfetchall()
                # print (resultado_to)
                ini = 1
                resul_count = len(resultado_to)
                for j in range(0, (int(str(diff).split(' ', 1)[0]) + 1), 1):
                    dias = timedelta(days=j)
                    fechas = d1 + dias
                    lst_f.append(fechas)  # almacenar todas la fechas en un array
                    self._cr.execute(
                        """SELECT hxe.fechas, dt.jornada, codigo,hora_inicio, hora_fin, segundo_hora_inicio, segundo_hora_fin FROM horario_horario_empleado he INNER JOIN horario_x_empleado hxe ON he.id = hxe.horario_x_empleado_id INNER JOIN horario_dia_trabajo dt ON hxe.codigo_trabajo = dt.codigo WHERE horario_empleado_id = %s AND hxe.fechas = %s""",
                        (self.employee_id.id, fechas))
                    resultado_to2 = self._cr.dictfetchall()
                    for e in resultado_to2:
                        fec = e['fechas']
                        hora_entrada = e['hora_inicio']
                        hora_salida = e['hora_fin']
                        segunda_hora_entrada = e['segundo_hora_inicio']
                        segunda_hora_salida = e['segundo_hora_fin']
                        codigo = e['codigo']

                    horario_asistencias_ids.append((0, 0, {
                        'fecha': fec,
                        'hora_entrada': hora_entrada,
                        'hora_salida': hora_salida,
                        'segunda_hora_entrada': segunda_hora_entrada,
                        'segunda_hora_salida': segunda_hora_salida,
                        'codigo_dias': codigo
                    }))
                    if resul_count != ini:
                        ini += 1
                        # print (ini)
                    else:
                        ini = 1
                        # print (horario_asistencias_ids)
                self.horario_asistencias_ids = horario_asistencias_ids

    _name = 'horario.asistencias'
    # _inherit = 'hr.employee'
    _rec_name = 'employee_id'
    _description = 'Estas son las asistencias'
    fecha_inicio = fields.Date(string="Fecha Inicio", default=_default_fecha_inicio)
    fecha_fin = fields.Date(string="Fecha Fin")
    horario_asistencias_ids = fields.One2many('horario.detalle.asistencias', 'horario_asistencias_id',
                                              ondelete='cascade', copy=True, string="Detalle de asistencias")
    employee_id = fields.Many2one('hr.employee', ondelete='cascade', required=True)


class horario_detalle_asistencias(models.Model):
    """detalle de asistencias por empleado"""

    @api.one
    @api.depends('fecha')
    def _compute_fecha(self):
        today = datetime.datetime.now()
        fecha_actual = "%s-%s-%s" % (today.year, str(today.month).zfill(2), today.day)
        # print ('iddddddd>', str(ids), fecha_actual)
        # print (fecha_actual)
        self._cr.execute(
            """SELECT id FROM horario_horario_empleado WHERE horario_empleado_id = %s ORDER BY id DESC LIMIT 1""",
            [ids])

        id_jor = self._cr.fetchone()
        if id_jor:
            id_hor = id_jor[0]
            # print (id_hor)
        else:
            raise except_orm(_('No hay Horario!'),
                             _('Debe crear un Horario.'))

        self._cr.execute(
            """SELECT dt.jornada FROM horario_horario_empleado he INNER JOIN horario_x_empleado hxe ON he.id = hxe.horario_x_empleado_id INNER JOIN horario_dia_trabajo dt ON hxe.codigo_trabajo = dt.codigo WHERE horario_empleado_id = %s AND hxe.fechas=%s AND hxe.horario_x_empleado_id = %s""",
            (ids, self.fecha, id_hor))
        jornada = self._cr.fetchone()

        if jornada:
            self.jornada_name = jornada[0]

    @api.multi
    def button_verificar(self):
        _logger.info("entro traer marcas")
        self._cr.execute("""DELETE FROM horas_extra WHERE employee_id=%s AND estado_pag=%s""", (ids, False))

        s = self.env['horario.marcaciones.empleado'].search(
            [['horario_marcacion_id', '=', self.horario_asistencias_id.employee_id.id],
             ['fecha', '=', self.fecha]]
        )

        if not s:
            raise except_orm(_('No hay Marcaciones!'),
                             _('Porfavor cree al menos una Marcación.'))

        horario_asis_tipo_ids = []
        today = datetime.datetime.now()
        fecha_actual = "%s-%s-%s" % (today.year, str(today.month).zfill(2), today.day)
        # print (self.fecha,dateMonthEnd)
        # if self.fecha >= fecha_actual:
        # print (self.id)
        if self.horario_asistencias_id.employee_id.id:
            self._cr.execute(
                """DELETE FROM horario_det_asistencias_tipo WHERE horario_asis_tipo_id = %s""", [self.id])
        self._cr.execute(
                        """SELECT *
            FROM horario_marcaciones_empleado
            WHERE horario_marcacion_id = %s""",
            [self.horario_asistencias_id.employee_id.id])
        resultado_to2 = self._cr.dictfetchall()
        # print (resultado_to2)

        for r in resultado_to2:
            if self.fecha == r['fecha']:
                ahora = dt.now()
                hora = ahora.hour
                minutos = ahora.minute
                m_dec = float(minutos) / 60
                hora_actual_dec = hora + m_dec
                # self.traer_marcas_ahora = hora_actual_dec
                # print("Hora Actual:", hora_actual_dec)  # Muestra hora

                primera_entrada = r['hora_entrada']
                primera_salida = r['hora_salida']
                segunda_entrada = r['segunda_hora_entrada']
                segunda_salida = r['segunda_hora_salida']
                resta = self.hora_entrada - 0.16666666667
                suma = self.hora_entrada + 0.16666666667
                # print (self.hora_entrada, self.hora_salida, self.segunda_hora_entrada, self.segunda_hora_salida)
                if self.hora_entrada == 0.0 and self.hora_salida == 0.0 and self.segunda_hora_entrada == 0.0 and self.segunda_hora_salida == 0.0:
                    if primera_entrada:
                        tipo_primera_salida = 'espera'
                        horario_asis_tipo_ids.append((0, 0, {
                            'primera_hora_entrada': primera_entrada,
                            'primera_marca_entrada': primera_salida,
                            'horario_asis_tipo_id': self.id,
                            'tipo_primera_entrada': tipo_primera_salida

                        }))
                    if segunda_entrada:
                        tipo_primera_salida = 'espera'
                        horario_asis_tipo_ids.append((0, 0, {
                            'primera_hora_entrada': segunda_entrada,
                            'primera_marca_entrada': segunda_salida,
                            'horario_asis_tipo_id': self.id,
                            'tipo_primera_entrada': tipo_primera_salida

                        }))
                    break

                # verificar la entrada para poder asignar una fila mas para la presencia hasta
                # la hora adecuada
                if self.hora_entrada:
                    if primera_entrada < resta:
                        # self.traer_marcas_ahora = resta
                        motivo = 'espera'
                        horario_asis_tipo_ids.append((0, 0, {
                            'primera_hora_entrada': primera_entrada,
                            'primera_marca_entrada': self.hora_entrada,
                            'horario_asis_tipo_id': self.id,
                            'tipo_primera_entrada': motivo

                        }))

                    elif primera_entrada > suma:
                        # self.traer_marcas_ahora= suma
                        motivo = 'falta'
                        # print(suma)
                        # print(resta)
                        horario_asis_tipo_ids.append((0, 0, {
                            'primera_hora_entrada': self.hora_entrada,
                            'primera_marca_entrada': primera_entrada,
                            'horario_asis_tipo_id': self.id,
                            'tipo_primera_entrada': motivo

                        }))
                    elif resta <= primera_entrada <= suma:
                        # print(suma)
                        # print(resta)
                        motivo = 'presencia'
                        if resta <= primera_entrada:
                            horario_asis_tipo_ids.append((0, 0, {
                                'primera_hora_entrada': self.hora_entrada,
                                'primera_marca_entrada': primera_entrada,
                                'horario_asis_tipo_id': self.id,
                                'tipo_primera_entrada': motivo

                            }))
                        elif primera_entrada < suma:
                            horario_asis_tipo_ids.append((0, 0, {
                                'primera_hora_entrada': primera_entrada,
                                'primera_marca_entrada': self.hora_entrada,
                                'horario_asis_tipo_id': self.id,
                                'tipo_primera_entrada': motivo

                            }))

                    if primera_entrada <= resta:
                        if primera_salida > self.hora_salida:
                            tipo_primera_salida = 'presencia'
                            horario_asis_tipo_ids.append((0, 0, {
                                'primera_hora_entrada': self.hora_entrada,
                                'primera_marca_entrada': self.hora_salida,
                                'horario_asis_tipo_id': self.id,
                                'tipo_primera_entrada': tipo_primera_salida

                            }))
                        else:
                            tipo_primera_salida = 'presencia'
                            horario_asis_tipo_ids.append((0, 0, {
                                'primera_hora_entrada': self.hora_entrada,
                                'primera_marca_entrada': primera_salida,
                                'horario_asis_tipo_id': self.id,
                                'tipo_primera_entrada': tipo_primera_salida

                            }))
                    else:
                        if primera_salida > self.hora_salida:
                            tipo_primera_salida = 'presencia'
                            horario_asis_tipo_ids.append((0, 0, {
                                'primera_hora_entrada': primera_entrada,
                                'primera_marca_entrada': self.hora_salida,
                                'horario_asis_tipo_id': self.id,
                                'tipo_primera_entrada': tipo_primera_salida

                            }))
                        else:
                            tipo_primera_salida = 'presencia'
                            horario_asis_tipo_ids.append((0, 0, {
                                'primera_hora_entrada': primera_entrada,
                                'primera_marca_entrada': primera_salida,
                                'horario_asis_tipo_id': self.id,
                                'tipo_primera_entrada': tipo_primera_salida

                            }))
                # verificamos si existe una primera salida para poder asignar los valores adecuados
                if primera_salida:

                    if primera_salida < self.hora_salida:
                        tipo_primera_salida = 'falta'

                        horario_asis_tipo_ids.append((0, 0, {
                            'primera_hora_entrada': primera_salida,
                            'primera_marca_entrada': self.hora_salida,
                            'horario_asis_tipo_id': self.id,
                            'tipo_primera_entrada': tipo_primera_salida

                        }))

                    elif primera_salida > self.hora_salida:
                        tipo_primera_salida = 'espera'

                        horario_asis_tipo_ids.append((0, 0, {
                            'primera_hora_entrada': self.hora_salida,
                            'primera_marca_entrada': primera_salida,
                            'horario_asis_tipo_id': self.id,
                            'tipo_primera_entrada': tipo_primera_salida

                        }))

                    # verificamos si existe segunda entrada para poder dibujar la siguiente fila
                    if segunda_entrada:
                        if primera_salida > self.hora_salida:
                            tipo_primera_salida = 'almuerzo'
                            horario_asis_tipo_ids.append((0, 0, {
                                'primera_hora_entrada': primera_salida,
                                'primera_marca_entrada': self.segunda_hora_entrada,
                                'horario_asis_tipo_id': self.id,
                                'tipo_primera_entrada': tipo_primera_salida

                            }))
                        else:
                            tipo_primera_salida = 'almuerzo'
                            horario_asis_tipo_ids.append((0, 0, {
                                'primera_hora_entrada': self.hora_salida,
                                'primera_marca_entrada': self.segunda_hora_entrada,
                                'horario_asis_tipo_id': self.id,
                                'tipo_primera_entrada': tipo_primera_salida

                            }))
                        resta_segundo = self.segunda_hora_entrada - 0.16666666667
                        suma_segundo = self.segunda_hora_entrada + 0.16666666667
                        if segunda_entrada < resta_segundo:
                            # self.traer_marcas_ahora = resta
                            motivo = 'espera'
                            horario_asis_tipo_ids.append((0, 0, {
                                'primera_hora_entrada': segunda_entrada,
                                'primera_marca_entrada': self.segunda_hora_entrada,
                                'horario_asis_tipo_id': self.id,
                                'tipo_primera_entrada': motivo

                            }))

                        elif segunda_entrada > suma_segundo:
                            # self.traer_marcas_ahora= suma
                            motivo = 'falta'
                            # print(suma)
                            # print(resta)
                            horario_asis_tipo_ids.append((0, 0, {
                                'primera_hora_entrada': self.segunda_hora_entrada,
                                'primera_marca_entrada': segunda_entrada,
                                'horario_asis_tipo_id': self.id,
                                'tipo_primera_entrada': motivo

                            }))
                        elif resta_segundo <= segunda_entrada <= suma_segundo:
                            # print(suma)
                            # print(resta)
                            motivo = 'presencia'
                            if resta_segundo <= segunda_entrada:
                                horario_asis_tipo_ids.append((0, 0, {
                                    'primera_hora_entrada': self.segunda_hora_entrada,
                                    'primera_marca_entrada': segunda_entrada,
                                    'horario_asis_tipo_id': self.id,
                                    'tipo_primera_entrada': motivo

                                }))
                            elif segunda_entrada < suma_segundo:
                                horario_asis_tipo_ids.append((0, 0, {
                                    'primera_hora_entrada': segunda_entrada,
                                    'primera_marca_entrada': self.segunda_hora_entrada,
                                    'horario_asis_tipo_id': self.id,
                                    'tipo_primera_entrada': motivo

                                }))

                        # para verificar si hay dos turnos
                        if self.segunda_hora_entrada:
                            if segunda_entrada <= resta:
                                if segunda_salida > self.segunda_hora_salida:

                                    tipo_primera_salida = 'presencia'
                                    horario_asis_tipo_ids.append((0, 0, {
                                        'primera_hora_entrada': self.segunda_hora_entrada,
                                        'primera_marca_entrada': self.segunda_hora_salida,
                                        'horario_asis_tipo_id': self.id,
                                        'tipo_primera_entrada': tipo_primera_salida

                                    }))
                                else:
                                    tipo_primera_salida = 'presencia'
                                    horario_asis_tipo_ids.append((0, 0, {
                                        'primera_hora_entrada': self.segunda_hora_entrada,
                                        'primera_marca_entrada': segunda_salida,
                                        'horario_asis_tipo_id': self.id,
                                        'tipo_primera_entrada': tipo_primera_salida

                                    }))
                            else:
                                if segunda_salida > self.segunda_hora_salida:
                                    tipo_primera_salida = 'presencia'
                                    horario_asis_tipo_ids.append((0, 0, {
                                        'primera_hora_entrada': segunda_entrada,
                                        'primera_marca_entrada': self.segunda_hora_salida,
                                        'horario_asis_tipo_id': self.id,
                                        'tipo_primera_entrada': tipo_primera_salida
                                    }))
                                else:
                                    tipo_primera_salida = 'presencia'
                                    horario_asis_tipo_ids.append((0, 0, {
                                        'primera_hora_entrada': segunda_entrada,
                                        'primera_marca_entrada': segunda_salida,
                                        'horario_asis_tipo_id': self.id,
                                        'tipo_primera_entrada': tipo_primera_salida
                                    }))
                            if segunda_salida:
                                if segunda_salida < self.segunda_hora_salida:
                                    tipo_primera_salida = 'falta'
                                    horario_asis_tipo_ids.append((0, 0, {
                                        'primera_hora_entrada': segunda_salida,
                                        'primera_marca_entrada': self.segunda_hora_salida,
                                        'horario_asis_tipo_id': self.id,
                                        'tipo_primera_entrada': tipo_primera_salida

                                    }))

                                elif primera_salida > self.hora_salida:
                                    tipo_primera_salida = 'espera'
                                    horario_asis_tipo_ids.append((0, 0, {
                                        'primera_hora_entrada': self.segunda_hora_salida,
                                        'primera_marca_entrada': segunda_salida,
                                        'horario_asis_tipo_id': self.id,
                                        'tipo_primera_entrada': tipo_primera_salida

                                    }))
                if not self.hora_entrada and not primera_salida:
                    resta_segundo = self.segunda_hora_entrada - 0.16666666667
                    suma_segundo = self.segunda_hora_entrada + 0.16666666667

                    if segunda_entrada < resta_segundo:

                        # self.traer_marcas_ahora = resta
                        motivo = 'espera'
                        horario_asis_tipo_ids.append((0, 0, {
                            'primera_hora_entrada': segunda_entrada,
                            'primera_marca_entrada': self.segunda_hora_entrada,
                            'horario_asis_tipo_id': self.id,
                            'tipo_primera_entrada': motivo

                        }))

                    elif segunda_entrada > suma_segundo:

                        motivo = 'falta'
                        horario_asis_tipo_ids.append((0, 0, {
                            'primera_hora_entrada': self.segunda_hora_entrada,
                            'primera_marca_entrada': segunda_entrada,
                            'horario_asis_tipo_id': self.id,
                            'tipo_primera_entrada': motivo

                        }))
                    elif resta_segundo <= segunda_entrada <= suma_segundo:
                        # print(suma)
                        # print(resta)
                        motivo = 'presencia'
                        if resta_segundo <= segunda_entrada:
                            horario_asis_tipo_ids.append((0, 0, {
                                'primera_hora_entrada': self.segunda_hora_entrada,
                                'primera_marca_entrada': segunda_entrada,
                                'horario_asis_tipo_id': self.id,
                                'tipo_primera_entrada': motivo
                            }))
                        elif segunda_entrada < suma_segundo:
                            horario_asis_tipo_ids.append((0, 0, {
                                'primera_hora_entrada': segunda_entrada,
                                'primera_marca_entrada': self.segunda_hora_entrada,
                                'horario_asis_tipo_id': self.id,
                                'tipo_primera_entrada': motivo

                            }))

                    if segunda_entrada <= resta_segundo:
                        if segunda_salida > self.segunda_hora_salida:
                            tipo_primera_salida = 'presencia'
                            horario_asis_tipo_ids.append((0, 0, {
                                'primera_hora_entrada': self.segunda_hora_entrada,
                                'primera_marca_entrada': self.segunda_hora_salida,
                                'horario_asis_tipo_id': self.id,
                                'tipo_primera_entrada': tipo_primera_salida

                            }))
                        else:
                            tipo_primera_salida = 'presencia'
                            horario_asis_tipo_ids.append((0, 0, {
                                'primera_hora_entrada': self.segunda_hora_entrada,
                                'primera_marca_entrada': segunda_salida,
                                'horario_asis_tipo_id': self.id,
                                'tipo_primera_entrada': tipo_primera_salida

                            }))
                    else:

                        if segunda_salida > self.segunda_hora_salida:
                            tipo_primera_salida = 'presencia'
                            horario_asis_tipo_ids.append((0, 0, {
                                'primera_hora_entrada': segunda_entrada,
                                'primera_marca_entrada': self.segunda_hora_salida,
                                'horario_asis_tipo_id': self.id,
                                'tipo_primera_entrada': tipo_primera_salida

                            }))
                        else:
                            tipo_primera_salida = 'presencia'
                            horario_asis_tipo_ids.append((0, 0, {
                                'primera_hora_entrada': segunda_entrada,
                                'primera_marca_entrada': segunda_salida,
                                'horario_asis_tipo_id': self.id,
                                'tipo_primera_entrada': tipo_primera_salida
                            }))

                    if segunda_salida:
                        if segunda_salida < self.segunda_hora_salida:
                            tipo_primera_salida = 'falta'
                            horario_asis_tipo_ids.append((0, 0, {
                                'primera_hora_entrada': segunda_salida,
                                'primera_marca_entrada': self.segunda_hora_salida,
                                'horario_asis_tipo_id': self.id,
                                'tipo_primera_entrada': tipo_primera_salida

                            }))

                        else:
                            tipo_primera_salida = 'espera'
                            horario_asis_tipo_ids.append((0, 0, {
                                'primera_hora_entrada': self.segunda_hora_salida,
                                'primera_marca_entrada': segunda_salida,
                                'horario_asis_tipo_id': self.id,
                                'tipo_primera_entrada': tipo_primera_salida

                            }))

        # para pasarles los valores a la tabla
        # print (horario_asis_tipo_ids)
        self.horario_asis_tipo_ids = horario_asis_tipo_ids

        # ldld = self.env['horario.det.asistencias.tipo'].search[['horario_asis_tipo_id.horario_asistencias_id.employee_id','=',ids]]
        # print (ldld)
        self._cr.execute(
            """SELECT hd.fecha, hd.hora_entrada, hd.hora_salida, hd.segunda_hora_entrada, hd.segunda_hora_salida, primera_hora_entrada,primera_marca_entrada, diferencia_horas, ha.employee_id
  FROM horario_detalle_asistencias hd INNER JOIN horario_asistencias ha
    ON hd.horario_asistencias_id = ha.id INNER JOIN horario_det_asistencias_tipo hdt
    ON hdt.horario_asis_tipo_id = hd.id
WHERE ha.employee_id = %s AND tipo_primera_entrada = 'espera'""", [ids])
        get_horas_extra = self._cr.dictfetchall()

        for he in get_horas_extra:
            valores = \
                {
                    'fecha': he['fecha'],
                    'hora_inicio_diurno': he['hora_entrada'],
                    'hora_fin_diurno': he['hora_salida'],
                    'hora_inicio_nocturno': he['segunda_hora_entrada'],
                    'hora_fin_nocturno': he['segunda_hora_salida'],
                    'motivo': 10,
                    # 'concepto': 'compensar',
                    'hora_inicio': he['primera_hora_entrada'],
                    'hora_fin': he['primera_marca_entrada'],
                    'horas': he['diferencia_horas'],
                    'employee_id': he['employee_id'],
                    # 'horas_extra_ids': [(0,0,{'horas_extra_empleado': he['diferencia_horas'], 'fecha': he['fecha'], 'employee_id': he['employee_id']})]
                }
            self.env['horas.extra'].create(valores)

        self._cr.execute(
            """SELECT hd.fecha, hd.hora_entrada, hd.hora_salida, hd.segunda_hora_entrada, hd.segunda_hora_salida, primera_hora_entrada,primera_marca_entrada, diferencia_horas, ha.employee_id
  FROM horario_detalle_asistencias hd INNER JOIN horario_asistencias ha
    ON hd.horario_asistencias_id = ha.id INNER JOIN horario_det_asistencias_tipo hdt
    ON hdt.horario_asis_tipo_id = hd.id
WHERE ha.employee_id = %s AND tipo_primera_entrada = 'falta'""", [ids])
        get_horas_falta = self._cr.dictfetchall()

        for hf in get_horas_falta:
            valores2 = \
                {
                    'fecha': hf['fecha'],
                    'hora_inicio_diurno': hf['hora_entrada'],
                    'hora_fin_diurno': hf['hora_salida'],
                    'hora_inicio_nocturno': hf['segunda_hora_entrada'],
                    'hora_fin_nocturno': hf['segunda_hora_salida'],
                    'motivo': 7,
                    # 'concepto': 'compensar',
                    'hora_inicio': hf['primera_hora_entrada'],
                    'hora_fin': hf['primera_marca_entrada'],
                    'horas': hf['diferencia_horas'],
                    'employee_id': hf['employee_id'],
                    # 'horas_extra_ids': [(0,0,{'horas_extra_empleado': he['diferencia_horas'], 'fecha': he['fecha'], 'employee_id': he['employee_id']})]
                }
            self.env['horas.extra'].create(valores2)

    _name = 'horario.detalle.asistencias'
    _description = 'Estas son las asistencias'

    jornada_name = fields.Char('', compute='_compute_fecha')
    fecha = fields.Date(string='Fechas', )
    hora_entrada = fields.Float(string='1° Turno de Entrada')
    hora_salida = fields.Float(string='1° Turno de Salida')
    segunda_hora_entrada = fields.Float(string='2° Turno de Entrada')
    segunda_hora_salida = fields.Float(string='2° Turno de Salida')
    codigo_dias = fields.Char(readonly=1)
    # primer_control_entrada = fields.Float(string='Primer Control', compute='_get_marcas')
    # segundo_control_entrada = fields.Float(string='Segundo Control', compute='_get_marcas')
    horario_asistencias_id = fields.Many2one('horario.asistencias', ondelete='cascade')

    horario_asis_tipo_ids = fields.One2many(comodel_name="horario.det.asistencias.tipo",
                                            inverse_name="horario_asis_tipo_id", string="Detalle Asistencias",
                                            required=False, ondelete='cascade')
    # traer_marcas_ahora = fields.Float()


class horario_det_asistencias_tipo(models.Model):
    @api.one
    @api.depends('primera_hora_entrada', 'primera_marca_entrada')
    def _get_diferencia_horas(self):
        """
        @api.depends() should contain all fields that will be used in the calculations.
        """
        self.diferencia_horas = abs(self.primera_hora_entrada - self.primera_marca_entrada)

    _name = 'horario.det.asistencias.tipo'
    # _rec_name = 'name'
    # _description = 'New Description'

    primera_hora_entrada = fields.Float(string='Hora')
    primera_marca_entrada = fields.Float(string='Hora')
    tipo_primera_entrada = fields.Selection(string="Motivo",
                                            selection=[('presencia', 'Presencia'), ('falta', 'Falta Injustificada'),
                                                       ('espera', 'Tiempo en Espera'),
                                                       ('almuerzo', 'Almuerzo')], required=False, )

    diferencia_horas = fields.Float(string="Diferencia", compute="_get_diferencia_horas", store=True)

    # primera_hora_salida = fields.Float(string='1° Hora Salida')
    # primera_marca_salida = fields.Float(string='1° Hora Salida')
    # tipo_primera_salida = fields.Selection(string="Motivo",
    #                                        selection=[('presencia', 'Presencia'), ('falta', 'Falta Injustificada'),
    #                                                   ('espera', 'Tiempo en Espera')], required=False, )
    horario_asis_tipo_id = fields.Many2one('horario.detalle.asistencias', ondelete='cascade')


class horas_extra_empleado(models.Model):
    _name = 'horas.extra.empleado'
    # _rec_name = 'name'
    # _description = 'New Description'

    horas_extra_empleado = fields.Float()
    fecha = fields.Date()
    employee_id = fields.Many2one('hr.employee', ondelete='cascade')
    horas_extra_id = fields.Many2one('horas_extra', ondelete='cascade')


class horas_extra(models.Model):
    """horas y extra y demas por cada empleado"""

    @api.model
    def create(self, vals, context=None):
        new_id = super(horas_extra, self).create(vals)
        new_object = self.env['horas.extra'].browse(new_id.id)
        # print ('Entreeeeeeeeeeeeeeeeeeeee')

        horas = vals['horas']
        sql = "SELECT name FROM hr_holidays_status hs WHERE id = %s"
        self._cr.execute(sql, ([vals['motivo']]))
        fil = self._cr.fetchone()
        # print (fil)

        q = "SELECT (SELECT COALESCE(SUM(horas), 0) AS ho FROM horas_extra WHERE employee_id = %s AND  motivo=5 AND estado_pag=False) - (SELECT COALESCE(SUM(horas), 0) AS ho FROM horas_extra WHERE employee_id = %s AND  motivo=7 AND estado_pag=False) as total"
        # q = "SELECT sum(horas_extra_empleado) AS ho FROM horas_extra_empleado WHERE employee_id = %s"
        self._cr.execute(q, (vals['employee_id'], vals['employee_id']))
        resul = self._cr.fetchone()

        if fil[0] == u'Permiso Compensatorio':
            horas *= -1
        elif fil[0] == u'Hora Extra':
            horas = horas
        # horas = r['horas_permiso'] - resul[0]
        valores = \
            {
                'employee_id': vals['employee_id'],
                'fecha': vals['fecha'],
                'horas_extra_empleado': horas,
                'horas_extra_id': new_object.id
            }
        if fil[0] == u'Permiso Compensatorio' and resul[0] < abs(horas):
            raise except_orm(_('Error!'),
                             _("No tiene suficientes Horas Extra!!"))
        else:
            self.env['horas.extra.empleado'].create(valores)
        return new_id

    @api.multi
    def write(self, vals, context=None):
        if vals.has_key('horas'):
            horas = vals['horas']
            sql = "SELECT name FROM hr_holidays_status hs WHERE id = %s"
            self._cr.execute(sql, [self.motivo.id])
            fil = self._cr.fetchone()

            q = "SELECT (SELECT COALESCE(SUM(horas), 0) AS ho FROM horas_extra WHERE employee_id = %s AND motivo=5 AND estado_pag=False) - (SELECT COALESCE(SUM(horas), 0) AS ho FROM horas_extra WHERE employee_id = %s AND motivo=7 AND estado_pag=False) AS total"
            # q = "SELECT sum(horas_extra_empleado) AS ho FROM horas_extra_empleado WHERE employee_id = %s"
            self._cr.execute(q, (self.employee_id.id, self.employee_id.id))
            resul = self._cr.fetchone()

            if fil[0] == u'Permiso Compensatorio':
                horas *= -1
            elif fil[0] == u'Hora Extra':
                horas = horas
            # horas = r['horas_permiso'] - resul[0]
            valores = \
                {
                    'employee_id': self.employee_id.id,
                    'fecha': self.fecha,
                    'horas_extra_empleado': horas,
                    'horas_extra_id': self.id
                }
            if fil[0] == u'Permiso Compensatorio' and resul[0] < abs(horas):
                raise except_orm(_('Error!'),
                                 _("No tiene suficientes Horas Extra!!"))
            else:
                self._cr.execute(
                    """ DELETE FROM horas_extra_empleado WHERE horas_extra_id=%s""", [self.id])
                self.env['horas.extra.empleado'].create(valores)

        return super(horas_extra, self).write(vals)

    @api.multi
    def unlink(self):
        self._cr.execute(
            """ DELETE FROM horas_extra_empleado WHERE horas_extra_id=%s""", [self.id])
        return super(horas_extra, self).unlink()

    @api.onchange('hora_inicio', 'hora_fin')
    def _onchange_horas(self):
        # dec = round((abs(grados) + ((minutos * 60.0) + segundos) / 3600.0) * 1000000.0) / 1000000.0
        self.horas = abs((self.hora_fin - self.hora_inicio) or 0.0)

    @api.onchange('fecha')
    def _onchange_fecha(self):
        print (ids)
        self._cr.execute("""SELECT hxe.fechas, hora_inicio, hora_fin, segundo_hora_inicio, segundo_hora_fin
  FROM horario_horario_empleado he INNER JOIN horario_x_empleado hxe
    ON he.id = hxe.horario_x_empleado_id INNER JOIN horario_dia_trabajo dt
    ON hxe.codigo_trabajo = dt.codigo
WHERE horario_empleado_id = %s""", [ids])
        horas = self._cr.dictfetchall()
        for h in horas:
            if self.fecha == h['fechas']:
                self.hora_inicio_diurno = h['hora_inicio']
                self.hora_fin_diurno = h['hora_fin']
                self.hora_inicio_nocturno = h['segundo_hora_inicio']
                self.hora_fin_nocturno = h['segundo_hora_fin']

    _name = 'horas.extra'
    # _rec_name = 'name'
    _description = 'Registro de horas extra'

    departamento = fields.Char(related='employee_id.department_id.complete_name', string="Departamento", store=True)
    titulo_trabajo = fields.Char(related='employee_id.job_id.name', string="Titulo de Trabajo", store=True,
                                 readonly=True)
    motivo = fields.Many2one('hr.holidays.status', string="Motivo", required=True)
    motivo_id_name = fields.Char(related='motivo.name')
    concepto = fields.Selection(string="Concepto", selection=[('pago', 'Por Pago'), ('compensar', 'Por Compensar'), ])
    fecha = fields.Date(string="Fecha", required=True)
    hora_inicio_diurno = fields.Float(string="Entrada Turno Diurno", store=True)
    hora_fin_diurno = fields.Float(string="Salida Turno Diurno", store=True)
    hora_inicio_nocturno = fields.Float(string="Entrada Turno Nocturno", store=True)
    hora_fin_nocturno = fields.Float(string="Salida Turno Nocturno", store=True)
    hora_inicio = fields.Float(string="Hora de Inicio")
    hora_fin = fields.Float(string="Hora de Termino")
    horas = fields.Float(string="N° Horas")
    estado_pag = fields.Boolean(string="Pagado?")
    employee_id = fields.Many2one(comodel_name="hr.employee", string="Empleados")
    horas_extra_ids = fields.One2many("horas.extra.empleado", 'horas_extra_id', string="horas extra")


class hr_holidays(models.Model):
    """campo para colocar el filtro para poder traer solo datos seleccionado a horaas extra"""

    @api.model
    def create(self, vals, context=None):
        if "date_from" in vals:
            start = datetime.datetime.strptime(vals['date_from'], "%Y-%m-%d %H:%M:%S") - timedelta(hours=5)
            tz = pytz.timezone('America/Bogota')
            start2 = tz.localize(start)
            tz_date = start2.strftime("%Y-%m-%d %H:%M:%S")
            vals['date_from'] = tz_date

        if "date_to" in vals:
            to = datetime.datetime.strptime(vals['date_to'], "%Y-%m-%d %H:%M:%S") - timedelta(hours=5)
            tz = pytz.timezone('America/Bogota')
            to = tz.localize(to)
            tz_date_to = to.strftime("%Y-%m-%d %H:%M:%S")
            vals['date_to'] = tz_date_to

        vals['dias_restando_vac'] = vals['number_of_days_temp']

        new_id = super(hr_holidays, self).create(vals)
        new_object = self.env['hr.holidays'].browse(new_id.id)
        # print (vals['holiday_status_id'])
        # print (vals['number_of_days_temp'])

        if vals['holiday_status_id'] == 8:
            if vals['number_of_days_temp'] < 7:
                raise except_orm(_('Error!'), _("%s") % self.holiday_status_id.error)
        return new_id

    @api.multi
    def write(self, vals, context=None):
        # print (vals)
        if "date_from" in vals:
            start = datetime.datetime.strptime(vals['date_from'], "%Y-%m-%d %H:%M:%S") - timedelta(hours=5)
            tz = pytz.timezone('America/Bogota')
            start2 = tz.localize(start)
            tz_date = start2.strftime("%Y-%m-%d %H:%M:%S")
            vals['date_from'] = tz_date

        if "date_to" in vals:
            to = datetime.datetime.strptime(vals['date_to'], "%Y-%m-%d %H:%M:%S") - timedelta(hours=5)
            tz = pytz.timezone('America/Bogota')
            to = tz.localize(to)
            tz_date_to = to.strftime("%Y-%m-%d %H:%M:%S")
            vals['date_to'] = tz_date_to

        if "number_of_days_temp" in vals:
            vals['dias_restando_vac'] = vals['number_of_days_temp']
        # print (vals)
        # self.dias_restando_vac = vals['number_of_days_temp']
        return super(hr_holidays, self).write(vals)

    @api.multi
    def onchange_date_from(self, date_to, date_from):
        res = super(hr_holidays, self).onchange_date_from(date_to, date_from)

        if self.holiday_status_id.name == 'Vacaciones':
            if self.number_of_days_temp < 7:
                raise except_orm(_('Error!'), _("%s") % self.holiday_status_id.error)
        return res

    _inherit = 'hr.holidays'

    relacion_con_vacaciones_gozadas_ids = fields.One2many('horario.detalle.vacaciones',
                                                          'relacion_con_vacaciones_gozadas')
    name = fields.Text('Descripción')
    dias_trabajados_caja = fields.Float('Dias Trabajados')
    dias_notrabajados_caja = fields.Float('Dias No Trabajados')

    dias_restando_vac = fields.Float('Dias')

    @api.v7
    def onchange_type(self, cr, uid, ids, holiday_type, employee_id=False, context=None):
        res = super(hr_holidays, self).onchange_type(cr, uid, ids, holiday_type, employee_id=employee_id)
        print (context)
        emp_id = context.get('default_employee_id', False)
        if holiday_type == 'employee' and emp_id:
            res['value'] = {
                'employee_id': emp_id
            }
        elif holiday_type == 'employee' and not emp_id:
            res['value'] = {
                'employee_id': False
            }
        return res

    @api.v8
    def holidays_validate(self):
        count = self.dias_restando_vac
        empleado = self.employee_id.id
        if self.holiday_status_id.name == 'Vacaciones':
            if self.number_of_days_temp < 7:
                raise except_orm(_('Error!'), _("%s") % self.holiday_status_id.error)

            # query = "SELECT nro_dias FROM horario_balance_saldos hh INNER JOIN horario_detalle_balance_saldos hs ON hh.id = hs.balance_saldos_id WHERE employee_id = %s"
            # self._cr.execute(query, [ids])
            # r = self._cr.fetchone()[0]
            master_query = "SELECT sum(saldo) FROM horario_vacaciones_x_empleado hh INNER JOIN horario_detalle_vacaciones hs ON hh.id = hs.detalle_vacaciones_ids WHERE hh.employee_id = %s"
            self._cr.execute(master_query, [empleado])
            saldo_master = self._cr.fetchone()[0]
            if saldo_master < count:
                raise except_orm(_('Error!'), _("Solo tiene %s dias de vacaciones disponibles!!!") % int(saldo_master))

            print (' while count fueraaaaaaa',str(count))
            while count > 0:
                query1 = "SELECT date_start FROM hr_contract WHERE employee_id = %s ORDER BY date_start DESC LIMIT 1"
                self._cr.execute(query1, [empleado])
                fecha_minima = self._cr.fetchone()[0]
                print (fecha_minima)
                saldo = 10
                while saldo >= 0:
                    query2 = "SELECT saldo FROM horario_vacaciones_x_empleado hh INNER JOIN horario_detalle_vacaciones hs ON hh.id = hs.detalle_vacaciones_ids WHERE hh.employee_id = %s AND hs.fecha_inicio = %s"
                    self._cr.execute(query2, (empleado, fecha_minima))
                    saldo = self._cr.fetchone()
                    if saldo:
                        saldo = saldo[0]
                    # if saldo < count:
                    #     raise except_orm(_('Error!'), _("No tiene suficientes vacaciones!!!!!"))
                    if saldo > 0:
                        fecha_a_registrar = fecha_minima
                        print ('fexcha minima', str(fecha_minima))
                        print ('saldo', str(saldo))
                        break
                    else:
                        d1 = date(int(fecha_minima[0:4]), int(fecha_minima[5:7]), int(fecha_minima[-2:]))
                        fecha_minima = d1 + relativedelta(years=1)
                        print ('fexcha minima + 1', str(fecha_minima))
                        fecha_minima = str(fecha_minima)[:10]
                        print ('fexcha minima :10', str(fecha_minima))
                if saldo:
                    count = count - saldo
                    print ('if count ', str(count))
                    self.write({'dias_restando_vac': count})
                    query3 = "SELECT dias_gozados FROM horario_vacaciones_x_empleado hh INNER JOIN horario_detalle_vacaciones hs ON hh.id = hs.detalle_vacaciones_ids WHERE hh.employee_id = %s AND hs.fecha_inicio = %s"
                    self._cr.execute(query3, (empleado, fecha_minima))
                    saldo_a_sumar = self._cr.fetchone()[0]
                    if count > 0:
                        self.dias_indemnizados = fecha_a_registrar
                        # actualizamos la tabla de vaciones con el saldo que queda
                        query2 = "UPDATE horario_detalle_vacaciones AS h SET dias_gozados = %s, saldo= %s, dias_vencidos= %s, relacion_con_vacaciones_gozadas = %s FROM horario_vacaciones_x_empleado AS he WHERE H.fecha_inicio = %s AND he.employee_id = %s"
                        self._cr.execute(query2, (saldo + saldo_a_sumar, 0, 0, self.id, fecha_minima, empleado))

                    else:
                        if count == 0:
                            query2 = "UPDATE horario_detalle_vacaciones AS h SET dias_gozados = %s, saldo= %s, dias_vencidos= %s, relacion_con_vacaciones_gozadas = %s  FROM horario_vacaciones_x_empleado AS he WHERE H.fecha_inicio = %s AND he.employee_id = %s"
                            self._cr.execute(query2,
                                             (saldo + saldo_a_sumar, 0, 0, self.id, fecha_minima, empleado))
                            break
                        else:
                            resto = count + saldo
                            print (resto)
                            saldo_restante = saldo - resto
                            print (saldo_restante)
                            print (resto + saldo_a_sumar)
                            query2 = "UPDATE horario_detalle_vacaciones AS h SET dias_gozados = %s, saldo= %s, dias_vencidos= %s, relacion_con_vacaciones_gozadas = %s  FROM horario_vacaciones_x_empleado AS he WHERE H.fecha_inicio = %s AND he.employee_id = %s"
                            self._cr.execute(query2, (resto + saldo_a_sumar, saldo_restante, saldo_restante, self.id, fecha_minima, empleado))


        primer_date = date(int(self.date_from[0:4]), int(self.date_from[5:7]), int(self.date_from[8:10]))
        ultimo_date = date(int(self.date_to[0:4]), int(self.date_to[5:7]), int(self.date_to[8:10]))

        ids_horario_x_empleado = self.env['horario.x.empleado'].search([['empleado','=', empleado],['fechas','>=', primer_date],['fechas','<=', ultimo_date]])
        dias_trabajados_caja = 0
        dias_notrabajados_caja = 0
        for hxe in ids_horario_x_empleado:
            if hxe.codigo_trabajo in ('OO', 'OFF'):
                dias_notrabajados_caja += 1
            else:
                dias_trabajados_caja +=1
        self.write({'dias_trabajados_caja': dias_trabajados_caja, 'dias_notrabajados_caja':dias_notrabajados_caja})

        return super(hr_holidays, self).holidays_validate()


class hr_holidays_status(models.Model):
    """campo para colocar el filtro para poder traer solo datos seleccionado a horaas extra"""
    _inherit = 'hr.holidays.status'

    filtro_he = fields.Boolean(string="Listar en Horas Extra")

    agrupador = fields.Char(string="Agrupador", required=True)
    descripcion_ingles = fields.Char(string='Tipo ausencia (Ingles)')
    indicador_ausentismo = fields.Char(string='Indicador Ausentismo')
    unidad = fields.Selection(string='Unidad', selection=[('dias', 'Dias'), ('horas', 'Horas-Minutos')], default='dias')
    min_tiempo = fields.Float(string="cant. Min.")
    max_tiempo = fields.Float(string="cant. Max.")
    min_tiempo_horas = fields.Float(string="cant. Min.")
    max_tiempo_horas = fields.Float(string="cant. Max.")
    reg_fecha_inicio = fields.Boolean(string='Registrar Fecha Inicio en día de descanso?')
    reg_fecha_fin = fields.Boolean(string='Registrar Fecha Fin en descanso?')
    pagada = fields.Boolean(string='Pagada?')
    trabajo_efectivo = fields.Boolean(string='Se considera trabajo Efectivo para Utilidades')
    observaciones = fields.Text(string="Observaciones", required=False, )
    regla_computo = fields.Char(string="Regla de Cómputo", required=False, )
    dia_semana_inicio = fields.Selection(string='Dia Inicio',
                                         selection=[('0', 'Lunes'), ('1', 'Martes'), ('2', 'Miercoles'),
                                                    ('3', 'Jueves'), ('4', 'Viernes'), ('5', 'Sabado'),
                                                    ('6', 'Domingo')], default='0')
    dia_semana_fin = fields.Selection(string='Dia Fin',
                                      selection=[('0', 'Lunes'), ('1', 'Martes'), ('2', 'Miercoles'), ('3', 'Jueves'),
                                                 ('4', 'Viernes'), ('5', 'Sabado'), ('6', 'Domingo')], default='6')
    festivos_ids = fields.Many2many(comodel_name="hr.holidays.st.festivos",
                                    relation="hr_holidays_status_group_fetivos_rel", column1="hr_holiday_group_id",
                                    column2="hr_holiday_id", string="Dias Festivos que Aplica", )
    tipo_dia_ids = fields.Many2many(comodel_name="hr.holidays.st.tipo.dia",
                                    relation="hr_holidays_status_group_tipo_dia_rel", column1="hr_holiday_id",
                                    column2="hr_holiday_tipo_id", string="Tipo Dia",
                                    help="Tipo de Día, quiere decir si es día de trabajo será trabajado pagado, si es día de descanso será libre pagado dependiendo del día que tenga la configuración será como SAP compute (cuente) los días.")

    error = fields.Text('Mensaje de Advertencia!!!')

    afecta_quinta = fields.Boolean('Afectación a 5ta Cat.')


class hr_holidays_st_fetivos(models.Model):
    _name = 'hr.holidays.st.festivos'
    # _rec_name = 'name'
    # _description = 'New Description'

    name = fields.Char('Nombre', required=True)
    holidays_status_ids = fields.Many2many(comodel_name="hr.holidays.status",
                                           relation="hr_holidays_status_group_fetivos_rel", column1="hr_holiday_id",
                                           column2="hr_holiday_group_id", string="Dias Festivos que Aplica", )


class hr_holidays_st_tipo_dia(models.Model):
    _name = 'hr.holidays.st.tipo.dia'
    # _rec_name = 'name'
    # _description = 'New Description'

    name = fields.Char('Nombre', required=True)
    holidays_status_ids = fields.Many2many(comodel_name="hr.holidays.status",
                                           relation="hr_holidays_status_group_tipo_dia_rel", column1="hr_holiday_id",
                                           column2="hr_holiday_tipo_id", string="Tipo Dia", )


class horario_cronograma(models.Model):
    """Para hacer el cronograma de horarios"""

    # verificar si existe contrato
    def _default_fecha_inicio(self):

        q = "SELECT date_start FROM hr_contract WHERE employee_id = %s ORDER BY date_start DESC LIMIT 1"
        self._cr.execute(q, [ids])
        r = self._cr.fetchone()
        if not r:
            raise except_orm(_('Error!'),
                             _("No existe contrato !!"))
        else:
            return r[0]

    # funcion que permite quitar los sheet al modulo
    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        res = models.Model.fields_view_get(self, cr, uid, view_id=view_id, view_type=view_type, context=context,
                                           toolbar=toolbar, submenu=submenu)
        if view_type == 'form':
            doc = etree.XML(res['arch'])
            for sheet in doc.xpath("//sheet"):
                parent = sheet.getparent()
                index = parent.index(sheet)
                for child in sheet:
                    parent.insert(index, child)
                    index += 1
                parent.remove(sheet)
            res['arch'] = etree.tostring(doc)
        return res

    # funcion sobreescrita que permite no volver a registrar la mis fechas ya registradas
    # @api.model
    # def create(self, vals, context=None):
    #     new_id = super(horario_cronograma, self).create(vals)
    #     new_object = self.env['horario.cronograma'].browse(new_id.id)
    #     print (new_object)
    #     # employee_id = self.env['horario.asistencias'].search(['employee_id','',])
    #     # print (new_object)
    #     if new_object:
    #         linea_em = self.env['horario.cronograma'].search([['employee_id','=',vals['employee_id']]])[0]
    #         print (linea_em)
    #         if linea_em.fecha_inicio == vals['fecha_inicio'] or linea_em.fecha_fin == vals['fecha_fin']:
    #             raise except_orm(_('Error!'),
    #                                  _("Fechas Ya registradas !!"))
    #     return new_id

    # metodo para pasar las fechas a la tabla tambien por ahora las horas de entrada y salida
    @api.onchange('fecha_inicio', 'fecha_fin')
    def _onchange_fechas(self):
        horario_cronograma_ids = []
        if self.fecha_inicio and self.fecha_fin:  # si existen valores
            order_by = 'create_date desc'
            fecha_horario = self.env['horario.horario.empleado'].search([['horario_empleado_id','=',self.employee_id.id]], limit=1, order=order_by)
            if self.fecha_fin <= self.fecha_inicio:  # si las fechas son iguales o menos que el inicio
                raise except_orm(_('Error!'),
                                 _("La fecha de FIN no puede ser menor que la de INICIO !!"))
            elif fecha_horario.fecha_inicio > self.fecha_inicio:
                raise except_orm(_('Error!'),
                                 _("No existe Horario para esta fecha !!"))
            else:
                d1 = date(int(self.fecha_inicio[0:4]), int(self.fecha_inicio[5:7]), int(self.fecha_inicio[-2:]))
                d2 = date(int(self.fecha_fin[0:4]), int(self.fecha_fin[5:7]), int(self.fecha_fin[-2:]))
                diff = d2 - d1  # restas las fechas
                lst_f = []

                self._cr.execute(
                    """SELECT dt.hora_inicio,dt.hora_fin FROM horario_detalle_esquema_trabajo edt INNER JOIN horario_esquema_trabajo et ON edt.esquema_id = et.id INNER JOIN horario_horario_empleado he ON he.esquema = et.id INNER JOIN horario_dia_trabajo dt ON dt.id = edt.codigo_dias WHERE he.horario_empleado_id = %s""",
                    [self.employee_id.id])
                resultado_to = self._cr.dictfetchall()
                print (resultado_to)
                ini = 1
                resul_count = len(resultado_to)
                # for i, j in enumerate(resultado_to):
                #     enum = i + 1
                #     print (enum)
                #     print (ini)
                for j in range(0, (int(str(diff).split(' ', 1)[0]) + 1), 1):
                    dias = timedelta(days=j)
                    fechas = d1 + dias
                    lst_f.append(fechas)  # almacenar todas la fechas en un array

                    # self._cr.execute(
                    #     """SELECT edt.sequence,dt.hora_inicio,dt.hora_fin,dt.segundo_hora_inicio,dt.segundo_hora_fin,dt.codigo FROM horario_detalle_esquema_trabajo edt INNER JOIN horario_esquema_trabajo et ON edt.esquema_id = et.id INNER JOIN horario_horario_empleado he ON he.esquema = et.id INNER JOIN horario_dia_trabajo dt ON dt.id = edt.codigo_dias WHERE he.horario_empleado_id = %s""",
                    #     [self.employee_id.id])
                    self._cr.execute(
                        """SELECT hxe.fechas, dt.jornada, codigo,hora_inicio, hora_fin, segundo_hora_inicio, segundo_hora_fin FROM horario_horario_empleado he INNER JOIN horario_x_empleado hxe ON he.id = hxe.horario_x_empleado_id INNER JOIN horario_dia_trabajo dt ON hxe.codigo_trabajo = dt.codigo WHERE horario_empleado_id = %s AND hxe.fechas = %s""",
                        (self.employee_id.id, fechas))
                    resultado_to2 = self._cr.dictfetchall()
                    # print(resultado_to2)
                    # a = [element for element in resultado_to2 if element['sequence'] == ini]
                    for e in resultado_to2:
                        fec = e['fechas']
                        hora_entrada = e['hora_inicio']
                        hora_salida = e['hora_fin']
                        segunda_hora_entrada = e['segundo_hora_inicio']
                        segunda_hora_salida = e['segundo_hora_fin']
                        codigo = e['codigo']

                    horario_cronograma_ids.append((0, 0, {
                        'fecha': fec,
                        'hora_entrada': hora_entrada,
                        'hora_salida': hora_salida,
                        'segunda_hora_entrada': segunda_hora_entrada,
                        'segunda_hora_salida': segunda_hora_salida,
                        'codigo': codigo
                    }))
                    if resul_count != ini:
                        ini += 1
                        # print (ini)
                    else:
                        ini = 1
                        # print (horario_asistencias_ids)

                self.horario_cronograma_ids = horario_cronograma_ids

    _name = 'horario.cronograma'
    # _inherit = 'hr.employee'
    _rec_name = 'employee_id'
    # _description = 'Estas son las asistencias'
    fecha_inicio = fields.Date(string="Fecha Inicio", default=_default_fecha_inicio)
    fecha_fin = fields.Date(string="Fecha Fin")
    state = fields.Selection([
        ('aprobar', 'Para Aprobar'),
        ('aprobado', 'Aprobado'),
    ], default='aprobar')

    horario_cronograma_ids = fields.One2many('horario.detalle.cronograma', 'horario_cronograma_id',
                                             ondelete='cascade', copy=True)

    employee_id = fields.Many2one('hr.employee', ondelete='cascade')

    @api.one
    def concept_progressbar(self):
        self.write({
            'state': 'aprobado',
        })

    # This function is triggered when the user clicks on the button 'Set to started'
    @api.one
    def started_progressbar(self):
        self.write({
            'state': 'aprobar'
        })


class horario_detalle_cronograma(models.Model):
    """detale de cronograma por empleado"""

    # @api.multi
    # def write(self, vals, context=None):
    #     v = self.env['horario.detalle.cronograma.vehi'].search([['fecha', '=', fecha_row_cronograma.fecha]])
    #     print (v)
    #     return super(horario_detalle_cronograma, self).write(vals)

    _name = 'horario.detalle.cronograma'

    # _description = 'Estas son las asistencias'
    fecha = fields.Date(string='Fechas', store=True)
    hora_entrada = fields.Float(string='1° Turno de Entrada', store=True)
    hora_salida = fields.Float(string='1° Turno de Salida', store=True)
    segunda_hora_entrada = fields.Float(string='2° Turno de Entrada', store=True)
    segunda_hora_salida = fields.Float(string='2° Turno de Salida', store=True)
    codigo = fields.Char(string="Codigo de Trabajo")
    horario_cronograma_id = fields.Many2one('horario.cronograma', ondelete='cascade')
    horario_det_vehi_ids = fields.One2many('horario.detalle.cronograma.vehi', 'horario_det_vehi_id',
                                           ondelete='cascade', copy=True, string="Detalle Vehiculos-Rutas")

    @api.multi
    def read(self, fields=None, load='_classic_read'):
        global fecha_row_cronograma
        id = 0
        for record in self:
            # print (record.fecha)
            fecha_row_cronograma = record
        # print (fecha_row_cronograma)
        res = super(horario_detalle_cronograma, self).read(fields=fields, load=load)
        return res


class horario_detalle_cronograma_vehi(models.Model):
    """detale de cronograma por empleado"""

    @api.model
    def create(self, vals):
        new_id = super(horario_detalle_cronograma_vehi, self).create(vals)
        new_object = self.env['horario.detalle.cronograma.vehi'].browse(new_id.id)
        lst_entrada = []
        lst_salida = []
        v = self.env['horario.detalle.cronograma.vehi'].search(
            [['fecha', '=', fecha_row_cronograma.fecha], ['horario_det_vehi_id', '=', vals['horario_det_vehi_id']]])
        for entrada in v:
            lst_entrada.append(entrada.hora_entrada)
            lst_salida.append(entrada.hora_salida)
        print (lst_entrada)
        print (lst_salida)

        self._cr.execute(
            """SELECT id FROM horario_horario_empleado WHERE horario_empleado_id = %s ORDER BY id DESC LIMIT 1""",
            [ids])

        id_jor = self._cr.fetchone()
        if id_jor:
            id_hor = id_jor[0]
        else:
            raise Warning('Debe crear un Horario')

        self._cr.execute(
            """SELECT dt.jornada, dt.codigo FROM horario_horario_empleado he INNER JOIN horario_x_empleado hxe ON he.id = hxe.horario_x_empleado_id INNER JOIN horario_dia_trabajo dt ON hxe.codigo_trabajo = dt.codigo WHERE horario_empleado_id = %s AND hxe.fechas=%s AND hxe.horario_x_empleado_id = %s""",
            (ids, fecha_row_cronograma.fecha, id_hor))
        jornada = self._cr.fetchone()
        if jornada:
            jorn_name = jornada[0]
            codigo = jornada[1]
            # print (jorn_name)

        # print (ids, fecha_row_cronograma.fecha, id_hor)

        if codigo[0] != 'N':
            valores = \
                {
                    'horario_marcacion_id': ids,
                    'fecha': fecha_row_cronograma.fecha,
                    'hora_entrada': lst_entrada[0],
                    'hora_salida': lst_salida[-1],
                    'segunda_hora_entrada': 0,
                    'segunda_hora_salida': 0,
                    'jornada_name': jorn_name
                }

            self._cr.execute(
                """DELETE FROM horario_marcaciones_empleado WHERE horario_marcacion_id=%s AND fecha = %s""",
                (ids, fecha_row_cronograma.fecha))
            self.env['horario.marcaciones.empleado'].create(valores)
        else:
            valores = \
                {
                    'horario_marcacion_id': ids,
                    'fecha': fecha_row_cronograma.fecha,
                    'hora_entrada': 0,
                    'hora_salida': 0,
                    'segunda_hora_entrada': lst_entrada[0],
                    'segunda_hora_salida': lst_salida[-1],
                    'jornada_name': jorn_name
                }
            self._cr.execute(
                """DELETE FROM horario_marcaciones_empleado WHERE horario_marcacion_id=%s AND fecha = %s""",
                (ids, fecha_row_cronograma.fecha))
            self.env['horario.marcaciones.empleado'].create(valores)
        return new_id

    @api.multi
    def write(self, vals, context=None):
        lst_entrada = []
        lst_salida = []
        v = self.env['horario.detalle.cronograma.vehi'].search(
            [['fecha', '=', fecha_row_cronograma.fecha], ['horario_det_vehi_id', '=', self.horario_det_vehi_id.id]])
        for entrada in v:
            lst_entrada.append(entrada.hora_entrada)
            lst_salida.append(entrada.hora_salida)
        self._cr.execute(
            """SELECT id FROM horario_horario_empleado WHERE horario_empleado_id = %s ORDER BY id DESC LIMIT 1""",
            [ids])

        id_jor = self._cr.fetchone()
        if id_jor:
            id_hor = id_jor[0]
        else:
            raise Warning('Debe crear un Horario')

        self._cr.execute(
            """SELECT dt.jornada FROM horario_horario_empleado he INNER JOIN horario_x_empleado hxe ON he.id = hxe.horario_x_empleado_id INNER JOIN horario_dia_trabajo dt ON hxe.codigo_trabajo = dt.codigo WHERE horario_empleado_id = %s AND hxe.fechas=%s AND hxe.horario_x_empleado_id = %s""",
            (ids, fecha_row_cronograma.fecha, id_hor))
        jornada = self._cr.fetchone()
        if jornada:
            jorn_name = jornada[0]
            # print (jorn_name)
        # if vals.has_key('hora_entrada'):
        #     ent = vals['hora_entrada']
        #     print (ent)
        # else:
        #     ent = lst_entrada[0]
        if vals.has_key('hora_salida'):
            sal = vals['hora_salida']
            print (sal)
        else:
            sal = lst_salida[-1]
        if lst_entrada[0] < 13.0:
            valores = \
                {
                    'horario_marcacion_id': ids,
                    'fecha': fecha_row_cronograma.fecha,
                    'hora_entrada': lst_entrada[0],
                    'hora_salida': sal,
                    'segunda_hora_entrada': 0,
                    'segunda_hora_salida': 0,
                    'jornada_name': jorn_name
                }

            self._cr.execute(
                """DELETE FROM horario_marcaciones_empleado WHERE horario_marcacion_id=%s AND fecha = %s""",
                (ids, fecha_row_cronograma.fecha))
            self.env['horario.marcaciones.empleado'].create(valores)
        else:
            valores = \
                {
                    'horario_marcacion_id': ids,
                    'fecha': fecha_row_cronograma.fecha,
                    'hora_entrada': 0,
                    'hora_salida': 0,
                    'hora_entrada': lst_entrada[0],
                    'hora_salida': sal,
                    'jornada_name': jorn_name
                }
            self._cr.execute(
                """DELETE FROM horario_marcaciones_empleado WHERE horario_marcacion_id=%s AND fecha = %s""",
                (ids, fecha_row_cronograma.fecha))

            self.env['horario.marcaciones.empleado'].create(valores)

        return super(horario_detalle_cronograma_vehi, self).write(vals)

    @api.multi
    def unlink(self):

        lst_entrada = []
        lst_salida = []
        self._cr.execute(
            """DELETE FROM horario_marcaciones_empleado WHERE horario_marcacion_id=%s AND fecha = %s""",
            (ids, fecha_row_cronograma.fecha))

        v = self.env['horario.detalle.cronograma.vehi'].search(
            [['fecha', '=', fecha_row_cronograma.fecha], ['horario_det_vehi_id', '=', self.horario_det_vehi_id.id]])
        for entrada in v:
            lst_entrada.append(entrada.hora_entrada)
            lst_salida.append(entrada.hora_salida)
        # self._cr.execute(
        #     """SELECT hdcv.hora_entrada FROM horario_cronograma hc INNER JOIN horario_detalle_cronograma hdc ON hc.id = hdc.horario_cronograma_id INNER JOIN horario_detalle_cronograma_vehi hdcv ON hdc.id = hdcv.horario_det_vehi_id WHERE employee_id = %s AND horario_det_vehi_id = %s AND hdcv.fecha = %s ORDER BY hdcv.hora_entrada ASC LIMIT 1""",
        #     (ids, self.horario_det_vehi_id.id, self.fecha))
        # entrada = self._cr.fetchone()
        # if entrada:
        #     id_hor_entrada = entrada[0]
        # self._cr.execute(
        #     """SELECT hdcv.hora_salida FROM horario_cronograma hc INNER JOIN horario_detalle_cronograma hdc ON hc.id = hdc.horario_cronograma_id INNER JOIN horario_detalle_cronograma_vehi hdcv ON hdc.id = hdcv.horario_det_vehi_id WHERE employee_id = %s AND horario_det_vehi_id = %s AND hdcv.fecha = %s ORDER BY hdcv.hora_salida DESC LIMIT 1""",
        #     (ids, self.horario_det_vehi_id.id, fecha_row_cronograma.fecha))
        # salida = self._cr.fetchone()
        # if salida:
        #     id_hor_salida = salida[0]
        self._cr.execute(
            """SELECT id FROM horario_horario_empleado WHERE horario_empleado_id = %s ORDER BY id DESC LIMIT 1""",
            [ids])

        id_jor = self._cr.fetchone()
        if id_jor:
            id_hor = id_jor[0]
        else:
            raise Warning('Debe crear un Horario')

        self._cr.execute(
            """SELECT dt.jornada FROM horario_horario_empleado he INNER JOIN horario_x_empleado hxe ON he.id = hxe.horario_x_empleado_id INNER JOIN horario_dia_trabajo dt ON hxe.codigo_trabajo = dt.codigo WHERE horario_empleado_id = %s AND hxe.fechas=%s AND hxe.horario_x_empleado_id = %s""",
            (ids, fecha_row_cronograma.fecha, id_hor))
        jornada = self._cr.fetchone()
        if jornada:
            jorn_name = jornada[0]
            # print (jorn_name)
        if lst_entrada[1] < 18.0:
            valores = \
                {
                    'horario_marcacion_id': ids,
                    'fecha': fecha_row_cronograma.fecha,
                    'hora_entrada': lst_entrada[0],
                    'hora_salida': lst_salida[-1],
                    'segunda_hora_entrada': 0,
                    'segunda_hora_salida': 0,
                    'jornada_name': jorn_name
                }

            self._cr.execute(
                """DELETE FROM horario_marcaciones_empleado WHERE horario_marcacion_id=%s AND fecha = %s""",
                (ids, fecha_row_cronograma.fecha))
            self.env['horario.marcaciones.empleado'].create(valores)
        else:
            valores = \
                {
                    'horario_marcacion_id': ids,
                    'fecha': fecha_row_cronograma.fecha,
                    'hora_entrada': 0,
                    'hora_salida': 0,
                    'segunda_hora_entrada': lst_entrada[1],
                    'segunda_hora_salida': lst_salida[-1],
                    'jornada_name': jorn_name
                }

            self.env['horario.marcaciones.empleado'].create(valores)

        return super(horario_detalle_cronograma_vehi, self).unlink()

    def _default_fecha(self):
        return fecha_row_cronograma.fecha

    def default_t_jor(self):
        self._cr.execute(
            """SELECT id FROM horario_horario_empleado WHERE horario_empleado_id = %s ORDER BY id DESC LIMIT 1""",
            [ids])

        id_jor = self._cr.fetchone()

        if id_jor:
            id_hor = id_jor[0]
        else:
            raise Warning('Debe crear un Horario')

        self._cr.execute(
            """SELECT dt.jornada FROM horario_horario_empleado he INNER JOIN horario_x_empleado hxe ON he.id = hxe.horario_x_empleado_id INNER JOIN horario_dia_trabajo dt ON hxe.codigo_trabajo = dt.codigo WHERE horario_empleado_id = %s AND hxe.fechas=%s AND hxe.horario_x_empleado_id = %s""",
            (ids, fecha_row_cronograma.fecha, id_hor))
        jornada = self._cr.fetchone()
        if jornada:
            return jornada[0]

    _name = 'horario.detalle.cronograma.vehi'
    _rec_name = 'fecha'
    # _description = 'Estas son las asistencias'

    fecha = fields.Date(string='Fechas', readonly=True, store=True, default=_default_fecha)
    hora_entrada = fields.Float(string='Hora Inicio', required=True)
    hora_salida = fields.Float(string='Hora Fin', required=True)
    vehiculo = fields.Many2one('fleet.vehicle', string='Vehiculo', required=True)
    ruta = fields.Many2one('modulo_valorizaciones.ruta', string='Ruta', required=True)
    horario_det_vehi_id = fields.Many2one('horario.detalle.cronograma', ondelete='cascade')

    jornada_name = fields.Char(string="Jornada", default=default_t_jor)


class horario_vacaciones_x_empleado(models.Model):
    @api.multi
    def ir_al_empleado_3(self):
        id = self.pool.get('ir.ui.view').search(self.env.cr, self.env.uid,
                                                [('model', '=', 'hr.employee'),
                                                 ('type', '=', 'form')])

        existeEspecifica = self.pool.get('hr.employee').search(self.env.cr, self.env.uid,
                                                               [('id', '=', self.employee_id.id)])
        # raise  Warning(id)
        course_form = self.pool.get('ir.ui.view').browse(self.env.cr, self.env.uid, id[0], context=None)

        ctx = dict(
            default_employee_id=self.employee_id.id,
        )
        return {
            'name': 'Empleado',
            'type': 'ir.actions.act_window',
            'res_model': 'hr.employee',
            'res_id': existeEspecifica[0],
            'view_type': 'form',
            'view_mode': 'form',
            # 'target': 'current',
            # 'views': [(course_form.id, 'form')],
            # 'view_id': course_form.id,
            # 'flags': {'action_buttons': True},
            'context': ctx,
        }

    @api.model
    def create(self, vals):
        _logger.info('entre create >>>>>>>>>>>>>>')
        # if len(vals['horario_empleado_ids']) < 1:
        #     raise Warning('Error!', 'Porfavor cree al menos un horario en la pestaña (Horario)!!')

        res = super(horario_vacaciones_x_empleado, self).create(vals)
        new_object = self.env['hr.employee'].browse(res.employee_id.id)
        new_object.write({'stage': '6'})
        return res

    def _default_fecha_inicio(self):

        q = "SELECT date_start FROM hr_contract WHERE employee_id = %s ORDER BY date_start DESC LIMIT 1"
        self._cr.execute(q, [ids])
        r = self._cr.fetchone()
        if not r:
            raise except_orm(_('Error!'),
                             _("No existe contrato !!"))
        else:
            return r[0]

    def _default_fecha_actual(self):
        today = datetime.datetime.now()
        fecha_actual = "%s-%s-%s" % (today.year, str(today.month).zfill(2), today.day)
        d1 = date(int(fecha_actual[0:4]), int(fecha_actual[5:7]), int(fecha_actual[-2:]))
        # print (d1)
        return d1

    @api.onchange('fecha_inicio', 'fecha_fin')
    def _onchange_fechas(self):
        global dias_ganados
        global dias_vencidos
        global dias_pendientes
        detalle_vacaciones_ids = []
        if self.fecha_inicio and self.fecha_fin:  # si existen valores

            d1 = date(int(self.fecha_inicio[0:4]), int(self.fecha_inicio[5:7]), int(self.fecha_inicio[-2:]))
            d2 = date(int(self.fecha_fin[0:4]), int(self.fecha_fin[5:7]), int(self.fecha_fin[-2:]))
            # print (d1)
            # print (d2)
            diff = d2 - d1  # restas las fechas
            anios = int((int(str(diff).split(' ', 1)[0]) + 1) / 365)
            # print (anios)
            resto = int((int(str(diff).split(' ', 1)[0]) + 1) % 365)
            # print (resto)
            di = int((int(str(diff).split(' ', 1)[0])))
            # print (di)
            if resto == 0:
                for j in range(0, anios):
                    dias = relativedelta(years=j)
                    fechas = d1 + dias
                    fechasmasuno = fechas - timedelta(days=1) + relativedelta(years=1)
                    lst.append(dias_ganados)
                    lst_vencidos.append(dias_vencidos)
                    lst_pendientes.append(dias_pendientes)
                    for l in lst:
                        dias_g = l
                    for v in lst_vencidos:
                        dias_v = v
                    for p in lst_pendientes:
                        dias_p = p
                    detalle_vacaciones_ids.append((0, 0, {
                        'fecha_inicio': fechas,
                        'fecha_fin': fechasmasuno,
                        'dias_ganados': dias_g,
                        'dias_vencidos': dias_v,
                        'dias_pendientes': dias_p,
                    }))
            else:
                # for i in range(0, anios + 1):
                #     lst.append(dias_ganados)
                # lst[-1] = (float(resto) * 30) / 365
                # print (lst)
                inicio = 1
                fin = len(lst)
                for j in range(0, anios + 1):
                    dias = relativedelta(years=j)
                    fechas = d1 + dias
                    # print (fechas)
                    fechasmasuno = fechas - timedelta(days=1) + relativedelta(years=1)
                    # print (dias_ganados)
                    lst.append(dias_ganados)
                    lst_vencidos.append(dias_vencidos)
                    lst_pendientes.append(dias_pendientes)
                    for l in lst:
                        dias_g = l
                    for v in lst_vencidos:
                        dias_v = v
                    for p in lst_pendientes:
                        dias_p = p
                    detalle_vacaciones_ids.append((0, 0, {
                        'fecha_inicio': fechas,
                        'fecha_fin': fechasmasuno,
                        'dias_ganados': dias_g,
                        'dias_vencidos': dias_v,
                        'dias_pendientes': dias_p,
                    }))
                    if fin != inicio:
                        inicio += 1
                    else:
                        inicio = 1

                # print (detalle_vacaciones_ids)
                # for d in detalle_vacaciones_ids[-2::]:
                detalle_vacaciones_ids[-1][-1]['dias_vencidos'] = 0.0
                f1 = date(int(self.fecha_inicio[0:4]), int(self.fecha_inicio[5:7]), int(self.fecha_inicio[-2:]))
                f2 = date(int(self.fecha_fin[0:4]), int(self.fecha_fin[5:7]), int(self.fecha_fin[-2:]))
                if (f2.year - f1.year) > 1:
                    detalle_vacaciones_ids[-2][-1]['dias_vencidos'] = 0.0
                    detalle_vacaciones_ids[-2][-1]['dias_pendientes'] = 30.0
                detalle_vacaciones_ids[-1][-1]['dias_ganados'] = (float(resto) * 30) / 365
                ### por ahoraaaaaaaaaaaaaaaaaa
                # detalle_vacaciones_ids[-1][-1]['dias_pendientes'] = (float(resto) * 30) / 365

                # detalle_vacaciones_ids[-2::][-2]['dias_vencidos'] = 0.0
            # for dic in detalle_vacaciones_ids[-1]:
            #     print (dic[-1])
            self.detalle_vacaciones_ids = detalle_vacaciones_ids

    _name = 'horario.vacaciones.x.empleado'
    _rec_name = 'employee_id'
    # _description = 'New Description'

    fecha_inicio = fields.Date(string='Fecha Inicio', default=_default_fecha_inicio)
    # fecha_fin = fields.Date(string='Fecha Fin', default=_default_fecha_actual)
    fecha_fin = fields.Date(string='Fecha Fin')
    detalle_vacaciones_ids = fields.One2many('horario.detalle.vacaciones', 'detalle_vacaciones_ids')
    employee_id = fields.Many2one(comodel_name="hr.employee", string="Empleado", required=True, )
    state = fields.Selection([
        ('aprobar', 'Para Aprobar'),
        ('aprobado', 'Aprobado'),
    ], default='aprobar')

    @api.one
    def concept_progressbar(self):
        self.write({
            'state': 'aprobado',
        })

    # This function is triggered when the user clicks on the button 'Set to started'
    @api.one
    def started_progressbar(self):
        self.write({
            'state': 'aprobar'
        })

    @api.model
    def _cron_refresh_holidays(self):
        self.actualizar_fecha_vacaciones()

    @api.multi
    def actualizar_fecha_vacaciones(self):
        print('Actualizandooo Vacaciones!!!!!!!!')
        employees = self.env['hr.employee'].search([['active', '=', True]])
        for emp in employees:
            vacaciones = self.search([['employee_id','=',emp.id]], limit=1)
            if vacaciones:
                fecha_actual = datetime.datetime.now()
                f = date(int(fecha_actual.year), int(fecha_actual.month), int(fecha_actual.day))
                fecha_fin = date(int(vacaciones.fecha_fin[0:4]), int(vacaciones.fecha_fin[5:7]), int(vacaciones.fecha_fin[-2:]))
                if fecha_fin <= f:
                    # fecha_fin_mas_uno = datetime.datetime.strptime(vacaciones.fecha_fin, "%Y-%m-%d") + timedelta(days=1)
                    fecha_fin_mas_uno = date(int(vacaciones.fecha_fin[0:4]), int(vacaciones.fecha_fin[5:7]), int(vacaciones.fecha_fin[-2:])) + timedelta(days=1)
                    vacaciones.write({'fecha_fin': fecha_fin_mas_uno})
                    order_desc = 'id desc'
                    vacaciones_lineas = self.env['horario.detalle.vacaciones'].search([['detalle_vacaciones_ids','=',vacaciones.id]], order=order_desc, limit=1)
                    for va in vacaciones_lineas:
                        global dias_ganados
                        global dias_vencidos
                        global dias_pendientes
                        detalle_vacaciones_ids = []
                        nueva_fecha_fin = str(fecha_fin_mas_uno)

                        print('entreeeeeeee Vacaciones!!!!!!!!',str(nueva_fecha_fin))
                        print('entreeeeeeee Vacaciones!!!!!!!!')
                        d1 = date(int(vacaciones.fecha_inicio[0:4]), int(vacaciones.fecha_inicio[5:7]), int(vacaciones.fecha_inicio[-2:]))
                        d2 = date(int(nueva_fecha_fin[0:4]), int(nueva_fecha_fin[5:7]), int(nueva_fecha_fin[-2:]))
                        # print (d1)
                        # print (d2)
                        diff = d2 - d1  # restas las fechas
                        anios = int((int(str(diff).split(' ', 1)[0]) + 1) / 365)
                        # print (anios)
                        resto = int((int(str(diff).split(' ', 1)[0]) + 1) % 365)
                        # print (resto)
                        di = int((int(str(diff).split(' ', 1)[0])))
                        # print (di)
                        if resto == 0:
                            for j in range(0, anios):
                                dias = relativedelta(years=j)
                                fechas = d1 + dias
                                fechasmasuno = fechas - timedelta(days=1) + relativedelta(years=1)
                                lst.append(dias_ganados)
                                lst_vencidos.append(dias_vencidos)
                                lst_pendientes.append(dias_pendientes)
                                for l in lst:
                                    dias_g = l
                                for v in lst_vencidos:
                                    dias_v = v
                                for p in lst_pendientes:
                                    dias_p = p
                                detalle_vacaciones_ids.append((1, va.id, {
                                    'fecha_inicio': fechas,
                                    'fecha_fin': fechasmasuno,
                                    'dias_ganados': dias_g,
                                    'dias_vencidos': dias_v,
                                    'dias_pendientes': dias_p,
                                }))
                        else:
                            # for i in range(0, anios + 1):
                            #     lst.append(dias_ganados)
                            # lst[-1] = (float(resto) * 30) / 365
                            # print (lst)
                            inicio = 1
                            fin = len(lst)
                            for j in range(0, anios + 1):
                                dias = relativedelta(years=j)
                                fechas = d1 + dias
                                # print (fechas)
                                fechasmasuno = fechas - timedelta(days=1) + relativedelta(years=1)
                                # print (dias_ganados)
                                lst.append(dias_ganados)
                                lst_vencidos.append(dias_vencidos)
                                lst_pendientes.append(dias_pendientes)
                                for l in lst:
                                    dias_g = l
                                for v in lst_vencidos:
                                    dias_v = v
                                for p in lst_pendientes:
                                    dias_p = p
                                detalle_vacaciones_ids.append((1, va.id, {
                                    'fecha_inicio': fechas,
                                    'fecha_fin': fechasmasuno,
                                    'dias_ganados': dias_g,
                                    'dias_vencidos': dias_v,
                                    'dias_pendientes': dias_p,
                                }))
                                if fin != inicio:
                                    inicio += 1
                                else:
                                    inicio = 1

                            # print (detalle_vacaciones_ids)
                            # for d in detalle_vacaciones_ids[-2::]:
                            detalle_vacaciones_ids[-1][-1]['dias_vencidos'] = 0.0
                            f1 = date(int(vacaciones.fecha_inicio[0:4]), int(vacaciones.fecha_inicio[5:7]), int(vacaciones.fecha_inicio[-2:]))
                            f2 = date(int(nueva_fecha_fin[0:4]), int(nueva_fecha_fin[5:7]), int(nueva_fecha_fin[-2:]))
                            if (f2.year - f1.year) > 1:
                                detalle_vacaciones_ids[-2][-1]['dias_vencidos'] = 0.0
                                detalle_vacaciones_ids[-2][-1]['dias_pendientes'] = 30.0
                            detalle_vacaciones_ids[-1][-1]['dias_ganados'] = (float(resto) * 30) / 365
                        vacaciones.detalle_vacaciones_ids = detalle_vacaciones_ids


class horario_detalle_vacaciones(models.Model):
    # @api.one
    # @api.depends('dias_ganados')
    # def _dias_vencidos(self):
    #     today = datetime.datetime.now()
    #     fecha_actual = "%s-%s-%s" % (today.year, str(today.month).zfill(2), today.day)
    #     d1 = date(int(fecha_actual[0:4]), int(fecha_actual[5:7]), int(fecha_actual[-2:]))
    #     fecha_menos = d1 - relativedelta(years=2)
    #     fecha_menos = str(fecha_menos)[:10]
    #     for r in self:
    #         if fecha_actual >= fecha_menos:
    #             if r.dias_ganados == 30.0:
    #                     self.dias_vencidos = r.dias_ganados

    @api.one
    @api.depends('dias_ganados')
    def _onchange_dias_ganados(self):
        if self.dias_ganados < 30.0:
            self.dias_truncos = self.dias_ganados
        else:
            self.dias_truncos = 0.0

    @api.one
    @api.depends('fecha_inicio', 'fecha_fin')
    def _get_def_dm(self):
        query = "SELECT hh.date_from, hh.date_to,hh.number_of_days_temp FROM hr_holidays hh INNER JOIN hr_holidays_status hs ON hh.holiday_status_id = hs.id WHERE employee_id = %s AND state='validate' AND hs.name='Descanso Medico'"
        self._cr.execute(query, ([ids]))
        r = self._cr.dictfetchall()
        # print (ids)
        # print (self.fecha_inicio)
        # print (self.fecha_fin)
        for resul in r:
            a = resul['date_from'].split(' ')
            b = resul['date_to'].split(' ')

            if str(a[0]) >= str(self.fecha_inicio) and str(self.fecha_fin) >= str(b[0]):
                # print ('entreee')
                self.dias_no_efectivos = resul['number_of_days_temp']
            else:
                self.dias_no_efectivos = 0

    @api.one
    @api.depends('dias_ganados', 'dias_indemnizados', 'dias_gozados', 'dias_adelantados', 'dias_no_efectivos',
                 'dias_comprados', 'dias_vencidos', 'dias_pendientes', 'dias_truncos', 'saldo')
    def _get_saldo_total(self):
        abc = self.dias_ganados - self.dias_gozados - self.dias_indemnizados - self.dias_adelantados - self.dias_no_efectivos
        # if abc < 0:
        #     raise except_orm(_('Error!'),
        #                      _("Ya no te quedan Dias!!!!"))
        # else:
        self.saldo = abc

    _name = 'horario.detalle.vacaciones'

    fecha_inicio = fields.Date(string='Fecha Inicio')
    fecha_fin = fields.Date(string='Fecha Fin')
    dias_ganados = fields.Float(string="Dias Ganados", store=True)
    dias_indemnizados = fields.Float(string="Dias de Balance", default=0.0, store=True)
    dias_gozados = fields.Float(string='Dias Gozados', default=0.0, store=True)
    dias_adelantados = fields.Float(string='Dias Adelantados', default=0.0, store=True)
    dias_no_efectivos = fields.Float(string='Dias No Efectivos por DM', compute='_get_def_dm', default=0.0, store=True)
    dias_comprados = fields.Float(string="Dias Convenio", default=0.0, store=True)
    dias_vencidos = fields.Float(string="Dias Vencidos", default=0.0, store=True)
    dias_pendientes = fields.Float(string="Dias Pendientes", required=False, default=0.0, store=True)
    dias_truncos = fields.Float(string="Dias Truncos", compute='_onchange_dias_ganados', store=True)
    saldo = fields.Float(string="Saldo", compute="_get_saldo_total", default=10.0, store=True)
    detalle_vacaciones_ids = fields.Many2one(comodel_name="horario.vacaciones.x.empleado", string="", )

    relacion_con_balances = fields.Many2one('horario.detalle.balance.saldos')
    relacion_con_vacaciones_gozadas = fields.Many2one('hr_holidays')


class horario_balance_saldos(models.Model):
    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        global ids
        ids = self.employee_id.id
        print (ids)

    _name = 'horario.balance.saldos'
    _rec_name = 'employee_id'
    # _description = 'New Description'

    employee_id = fields.Many2one('hr.employee', 'Empleado')
    balance_saldos_ids = fields.One2many('horario.detalle.balance.saldos', 'balance_saldos_id', ondelete="cascade")


class horario_detalle_balance_saldos(models.Model):
    def default_em(self):
        return ids

    @api.model
    def create(self, vals):
        new_id = super(horario_detalle_balance_saldos, self).create(vals)
        new_object = self.env['horario.detalle.balance.saldos'].browse(new_id.id)
        # print ('entre')
        # print (vals['employee_id'])
        # query = "SELECT nro_dias FROM horario_balance_saldos hh INNER JOIN horario_detalle_balance_saldos hs ON hh.id = hs.balance_saldos_id WHERE employee_id = %s"
        # self._cr.execute(query, [ids])
        # r = self._cr.fetchone()[0]
        count = vals['nro_dias']
        while count > 0:
            query1 = "SELECT date_start FROM hr_contract WHERE employee_id = %s ORDER BY date_start DESC LIMIT 1"
            self._cr.execute(query1, [vals['employee_id']])
            fecha_minima = self._cr.fetchone()[0]
            # print (fecha_minima)
            saldo = 10
            while saldo >= 0:
                print (vals['employee_id'], fecha_minima)
                query2 = "SELECT saldo, hs.id, hs.fecha_inicio, hs.fecha_fin FROM horario_vacaciones_x_empleado hh INNER JOIN horario_detalle_vacaciones hs ON hh.id = hs.detalle_vacaciones_ids WHERE hh.employee_id = %s AND hs.fecha_inicio = %s"
                self._cr.execute(query2, (vals['employee_id'], fecha_minima))
                res = self._cr.fetchone()
                # print (res)
                saldo = res[0]
                id_vac = res[1]
                fecha_inicio_rel = res[2]
                fecha_fin_rel = res[3]
                if saldo > 0:
                    fecha_a_registrar = fecha_minima
                    # print (fecha_minima)
                    # print (saldo)
                    break
                else:
                    d1 = date(int(fecha_minima[0:4]), int(fecha_minima[5:7]), int(fecha_minima[-2:]))
                    fecha_minima = d1 + relativedelta(years=1)
                    fecha_minima = str(fecha_minima)[:10]
            count -= saldo
            query3 = "SELECT dias_indemnizados FROM horario_vacaciones_x_empleado hh INNER JOIN horario_detalle_vacaciones hs ON hh.id = hs.detalle_vacaciones_ids WHERE hh.employee_id = %s AND hs.fecha_inicio = %s"
            self._cr.execute(query3, (vals['employee_id'], fecha_minima))
            saldo_a_sumar = self._cr.fetchone()[0]
            if count > 0:
                self.dias_indemnizados = fecha_a_registrar
                # actualizamos la tabla de vaciones con el saldo que queda
                query2 = "UPDATE horario_detalle_vacaciones AS h SET dias_indemnizados = %s, dias_vencidos = %s, saldo= %s FROM horario_vacaciones_x_empleado AS he WHERE H.fecha_inicio = %s AND he.employee_id = %s"
                self._cr.execute(query2, (saldo + saldo_a_sumar, 0, 0, fecha_minima, vals['employee_id']))

                valores = {
                    'id_fila_balances': new_object.id,
                    'id_fila_vacaciones': id_vac,
                    'fecha_inicio': fecha_inicio_rel,
                    'fecha_fin': fecha_fin_rel,
                    'dias': saldo,
                    'id_employee': vals['employee_id']
                }
                self.env['relacion.vacaciones.balances'].create(valores)

            else:
                if count == 0:
                    query2 = "UPDATE horario_detalle_vacaciones AS h SET dias_indemnizados = %s, dias_vencidos = %s, saldo= %s FROM horario_vacaciones_x_empleado AS he WHERE H.fecha_inicio = %s AND he.employee_id = %s"
                    self._cr.execute(query2,
                                     (saldo + saldo_a_sumar, 0, 0, fecha_minima, vals['employee_id']))

                    valores = {
                        'id_fila_balances': new_object.id,
                        'id_fila_vacaciones': id_vac,
                        'fecha_inicio': fecha_inicio_rel,
                        'fecha_fin': fecha_fin_rel,
                        'dias': saldo,
                        'id_employee': vals['employee_id']
                    }
                    self.env['relacion.vacaciones.balances'].create(valores)

                    break
                else:
                    resto = count + saldo
                    saldo_restante = saldo - resto
                    query2 = "UPDATE horario_detalle_vacaciones AS h SET dias_indemnizados = %s, dias_vencidos = %s, saldo= %s FROM horario_vacaciones_x_empleado AS he WHERE H.fecha_inicio = %s AND he.employee_id = %s"
                    self._cr.execute(query2, (
                        resto + saldo_a_sumar, saldo_restante, saldo_restante, fecha_minima, vals['employee_id']))

                    valores = {
                        'id_fila_balances': new_object.id,
                        'id_fila_vacaciones': id_vac,
                        'fecha_inicio': fecha_inicio_rel,
                        'fecha_fin': fecha_fin_rel,
                        'dias': resto,
                        'id_employee': vals['employee_id']
                    }
                    self.env['relacion.vacaciones.balances'].create(valores)
        return new_id

    #
    @api.multi
    def write(self, vals, context=None):
        print ('entre')
        # query = "SELECT nro_dias FROM horario_balance_saldos hh INNER JOIN horario_detalle_balance_saldos hs ON hh.id = hs.balance_saldos_id WHERE hh.employee_id = %s and hs.id = %s"
        # self._cr.execute(query, (self.employee_id.id, self.id))
        # r = self._cr.fetchone()[0]
        # for r in self.relcion_con_det_vacaciones:
        #     aa = r
        # query6 = "UPDATE horario_detalle_vacaciones as h SET dias_indemnizados = %s, saldo= %s FROM horario_vacaciones_x_empleado as he WHERE h.relacion_con_balances = %s AND he.employee_id = %s"
        # self._cr.execute(query6, (0, aa.dias_indemnizados, self.id, self.employee_id.id))

        nro_dias_pasado = self.nro_dias
        count = vals['nro_dias']
        print (count)
        saldo_a_sumar = count - nro_dias_pasado
        print (saldo_a_sumar)
        #     while count > 0:
        #
        #
        #         query1 = "SELECT date_start from hr_contract WHERE employee_id = %s"
        #         self._cr.execute(query1, [self.employee_id.id])
        #         fecha_minima = self._cr.fetchone()[0]
        #
        #         saldo = 10
        #         while saldo >= 0:
        #             query2 = "SELECT saldo FROM horario_vacaciones_x_empleado hh INNER JOIN horario_detalle_vacaciones hs ON hh.id = hs.detalle_vacaciones_ids WHERE hh.employee_id = %s and hs.fecha_inicio = %s"
        #             self._cr.execute(query2, (self.employee_id.id, fecha_minima))
        #             saldo = self._cr.fetchone()
        #             if saldo:
        #                 saldo = saldo[0]
        #             if saldo > 0:
        #                 print ('entre al if')
        #                 fecha_a_registrar = fecha_minima
        #                 print (fecha_minima)
        #                 print (saldo)
        #                 break
        #             else:
        #                 print ('entre al else')
        #                 d1 = date(int(fecha_minima[0:4]), int(fecha_minima[5:7]), int(fecha_minima[-2:]))
        #                 fecha_minima = d1 + relativedelta(years=1)
        #                 fecha_minima = str(fecha_minima)[:10]
        #         count -= saldo
        #         query3 = "SELECT dias_indemnizados FROM horario_vacaciones_x_empleado hh INNER JOIN horario_detalle_vacaciones hs ON hh.id = hs.detalle_vacaciones_ids WHERE hh.employee_id = %s and hs.fecha_inicio = %s"
        #         self._cr.execute(query3, (self.employee_id.id, fecha_minima))
        #         saldo_a_sumar = self._cr.fetchone()[0]
        #         if count > 0:
        #             self.dias_indemnizados = fecha_a_registrar
        #             # actualizamos la tabla de vaciones con el saldo que queda
        #             query2 = "UPDATE horario_detalle_vacaciones as h SET dias_indemnizados = %s, saldo= %s FROM horario_vacaciones_x_empleado as he WHERE h.fecha_inicio = %s AND he.employee_id = %s"
        #             self._cr.execute(query2, (saldo + saldo_a_sumar, 0, fecha_minima, self.employee_id.id))
        #
        #         else:
        #             if count == 0:
        #                 query2 = "UPDATE horario_detalle_vacaciones as h SET dias_indemnizados = %s, saldo= %s FROM horario_vacaciones_x_empleado as he WHERE h.fecha_inicio = %s AND he.employee_id = %s"
        #                 self._cr.execute(query2, (saldo + saldo_a_sumar, 0, fecha_minima, self.employee_id.id))
        #                 break
        #             else:
        #                 resto = count + saldo
        #                 saldo_restante = saldo - resto
        #                 query2 = "UPDATE horario_detalle_vacaciones as h SET dias_indemnizados = %s, saldo= %s FROM horario_vacaciones_x_empleado as he WHERE h.fecha_inicio = %s AND he.employee_id = %s"
        #                 self._cr.execute(query2, (resto + saldo_a_sumar, saldo_restante, fecha_minima, self.employee_id.id))
        #
        return super(horario_detalle_balance_saldos, self).write(vals)

    @api.multi
    def unlink(self):
        print (self.employee_id.id, self.id)
        self._cr.execute("""SELECT id_fila_vacaciones FROM horario_detalle_vacaciones h INNER JOIN relacion_vacaciones_balances rv
  ON h.id = rv.id_fila_vacaciones WHERE rv.id_employee = %s AND id_fila_balances = %s""",
                         (self.employee_id.id, self.id))
        data_ids = self._cr.fetchall()
        # print (data_ids)
        for a in data_ids:
            for un in a:
                print (un, self.id)
                self._cr.execute(
                    """UPDATE horario_detalle_vacaciones SET saldo = h.saldo + he.dias, dias_vencidos = h.dias_vencidos + he.dias, dias_indemnizados = h.dias_indemnizados - he.dias FROM horario_detalle_vacaciones as h INNER JOIN relacion_vacaciones_balances as he on h.id = he.id_fila_vacaciones WHERE he.id_fila_balances = {0} and horario_detalle_vacaciones.id = {1}""".format(
                        int(self.id), un))

        return super(horario_detalle_balance_saldos, self).unlink()

    _name = 'horario.detalle.balance.saldos'
    # _rec_name = 'name'
    # _description = 'New Description'

    fecha = fields.Date(string="Fecha", required=True)
    nro_dias = fields.Integer(string="Dias", required=True)
    employee_id = fields.Many2one('hr.employee', 'Empleado', default=default_em, required=True)
    balance_saldos_id = fields.Many2one('horario.balance.saldos', ondelete="cascade")

    # relcion_con_det_vacaciones = fields.One2many('horario.detalle.vacaciones', 'relacion_con_balances',
    # ondelete="cascade")


class relacion_vacaciones_balances(models.Model):
    _name = 'relacion.vacaciones.balances'
    # _rec_name = 'name'
    # _description = 'New Description'

    id_fila_balances = fields.Many2one('horario.detalle.balance.saldos')
    id_fila_vacaciones = fields.Many2one('horario.detalle.vacaciones')
    id_employee = fields.Many2one('hr.employee')
    fecha_inicio = fields.Date('Fecha Inicio')
    fecha_fin = fields.Date('Fecha Fin')
    dias = fields.Integer(string="Dias")


class hr_saldo_vacaciones(models.Model):
    def fields_view_get(self, cr, uid, view_id=None, view_type='form',
                        context=None, toolbar=False, submenu=False):
        if context is None:
            context = {}
        res = super(hr_saldo_vacaciones, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type,
                                                               context=context, toolbar=toolbar, submenu=False)
        cr.execute("""DELETE FROM hr_saldo_vacaciones""")

        # print ('holaaaaaaaaaaaaaaa')
        cr.execute("""SELECT vxe.employee_id, COALESCE(CONCAT(apellido_paterno,' ',apellido_materno,', ',primer_nombre,' ',segundo_nombre)) AS Nombre, vxe.fecha_inicio,cast(SUM(dias_vencidos) AS DECIMAL(18,2)) AS Vencidos, cast(SUM(dias_pendientes) AS DECIMAL(18,2)) AS Pendientes, cast(SUM(dias_truncos) AS DECIMAL(18,2)) AS Truncos, (cast(SUM(dias_vencidos) AS DECIMAL(18,2)) + cast(SUM(dias_pendientes) AS DECIMAL(18,2)) + cast(SUM(dias_truncos) AS DECIMAL(18,2))) AS Total
FROM horario_vacaciones_x_empleado vxe INNER JOIN horario_detalle_vacaciones hdv
  ON vxe.id = hdv.detalle_vacaciones_ids INNER JOIN hr_employee he
  ON he.id = vxe.employee_id INNER JOIN hr_contract hc ON he.id = hc.employee_id
GROUP BY vxe.employee_id, vxe.fecha_inicio, Nombre
ORDER BY vxe.employee_id""")
        re = cr.dictfetchall()
        # print (re)
        for r in re:
            # print (r)
            id = r['employee_id']
            nombre = r['nombre']
            contrato = r['fecha_inicio']
            vencidas = r['vencidos']
            pendientes = r['pendientes']
            truncos = r['truncos']
            total = r['total']

            valores = \
                {
                    'codigo_employee': id,
                    'id_employee': nombre,
                    'fecha_contrato': contrato,
                    'vencidas': vencidas,
                    'pendientes': pendientes,
                    'truncos': truncos,
                    'total': total
                }
            self.pool.get('hr.saldo.vacaciones').create(cr, uid, valores)

        cr.execute("""DELETE FROM hr_saldo_vacaciones WHERE fecha_contrato IN (SELECT min(fecha_contrato) FROM hr_saldo_vacaciones
GROUP BY codigo_employee HAVING count(*) > 1)""")

        return res

    _name = 'hr.saldo.vacaciones'
    # _rec_name = 'name'
    # _description = 'New Description'

    codigo_employee = fields.Char(string='ID')
    id_employee = fields.Char('Empleado')
    fecha_contrato = fields.Date('Fecha Contrato')
    vencidas = fields.Float('Vencidas')
    pendientes = fields.Float('Pendientes')
    truncos = fields.Float('Truncos')
    total = fields.Float('Total')


id_contrato = 0
class hr_contract(models.Model):

    # _name = 'new_module.new_module'
    _inherit = 'hr.contract'

    @api.multi
    def ir_al_empleado(self):
        id = self.pool.get('ir.ui.view').search(self.env.cr, self.env.uid,
                                                [('model', '=', 'hr.employee'),
                                                 ('type', '=', 'form')])

        existeEspecifica = self.pool.get('hr.employee').search(self.env.cr, self.env.uid,[('id', '=', self.employee_id.id)])
        # raise  Warning(id)
        course_form = self.pool.get('ir.ui.view').browse(self.env.cr, self.env.uid, id[0], context=None)

        ctx = dict(
            default_employee_id= self.employee_id.id,
        )
        return {
            'name': 'Empleado',
            'type': 'ir.actions.act_window',
            'res_model': 'hr.employee',
            'res_id': existeEspecifica[0],
            'view_type': 'form',
            'view_mode': 'form',
            # 'target': 'current',
            # 'views': [(course_form.id, 'form')],
            # 'view_id': course_form.id,
            # 'flags': {'action_buttons': True},
            'context': ctx,
        }

    @api.model
    def create(self, vals):
        _logger.info('entre create >>>>>>>>>>>>>>')
        # if len(vals['horario_empleado_ids']) < 1:
        #     raise Warning('Error!', 'Porfavor cree al menos un horario en la pestaña (Horario)!!')
        res = super(hr_contract, self).create(vals)
        new_object = self.env['hr.employee'].browse(res.employee_id.id)
        new_object.write({'stage': '4'})
        return res

    regimen_laboral = fields.Many2one('catalogo.regimen.laboral.33')
    type_id = fields.Many2one('catalogo.tipo.contrato.12')
    regimen_acumulativo = fields.Boolean('Regimen Acumulativo',
                                         help="Sujeto a régimen alternativo, acumulativo o atípico de jornada de trabajo y descanso.")
    jornada_maxima = fields.Boolean('Jornada Maxima', help="Sujeto a jornada de trabajo máxima")
    horario_nocturno = fields.Boolean('Horario Nocturno', help="Sujeto a horario nocturno")
    renta_5_exonerada = fields.Boolean('Rentas 5ta cat. exon.')
    tipo_pago = fields.Selection(string='Tipo de Pago', selection=[('1', 'EFECTIVO'),
                                                                   ('2', 'DEPOSITO EN CUENTA'),
                                                                   ('3', 'OTROS')])

    periodicidad_remu = fields.Selection(string='Periodo Remuneracion', selection=[('1', 'MENSUAL'),
                                                                                   ('2', 'QUINCENAL'),
                                                                                   ('3', 'SEMANAL'),
                                                                                   ('4', 'DIARIA'),
                                                                                   ('5', 'OTROS')])

    periodo_ids = fields.One2many('hr.contract.periodos', 'periodo_id')
    grati_julio = fields.Boolean('Grat. Julio', default=True)
    grati_dici = fields.Boolean('Grat. Diciembre', default=True)
    grati_julio_caja = fields.Float('Grat. Julio', digits=dp.get_precision('Account'))
    grati_dici_caja = fields.Float('Grat. Diciembre', digits=dp.get_precision('Account'))

    calculo_gratificacion = fields.Boolean('Cal. Grati. Días Efec.', help="Si esta marcado el calculo se hara por los dias del mes que corresponda caso contrario se hara por un numero estandar de 30")

    salarios_ids = fields.One2many('hr.contract.salarios', 'salarios_id')
    wage = fields.Float('Salario', digits=(16, 2), required=True, help="Salario Basico del Empleado")

    contrato_activo = fields.Boolean(string="Activo",  )

    @api.multi
    def read(self, fields=None, load='_classic_read'):
        global id_contrato
        for record in self:
           id_contrato = record.id
        res = super(hr_contract, self).read(fields=fields, load=load)
        return res

    @api.model
    def default_get(self, vals):
        global fecha_row_contrato
        res = super(hr_contract, self).default_get(vals)
        if 'date_start' in res:
            fecha_row_contrato = res['date_start']
        return res

    @api.onchange('date_start')
    def _onchange_date_start(self):
        global fecha_row_contrato
        fecha_row_contrato = self.date_start

    # @api.one
    # @api.onchange('date_start')
    # @api.constrains('date_start')
    # def _check_limit(self):
    #     print (len(self.date_start))
    #     if len(self.date_start) == 10 or len(self.date_start) == 0:
    #         return True
    #     else:
    #         raise except_orm(_('Error!'), _("No debe sobrepasar los 8 caracteres"))
    #
    # @api.one
    # @api.onchange('date_end')
    # @api.constrains('date_end')
    # def _check_limit(self):
    #     print (len(self.date_end))
    #     if len(self.date_end) == 10 or len(self.date_end) == 0:
    #         return True
    #     else:
    #         raise except_orm(_('Error!'), _("No debe sobrepasar los 8 caracteres"))


class hr_judiciales(models.Model):
    @api.multi
    def ir_al_empleado_4(self):
        id = self.pool.get('ir.ui.view').search(self.env.cr, self.env.uid,
                                                [('model', '=', 'hr.employee'),
                                                 ('type', '=', 'form')])

        existeEspecifica = self.pool.get('hr.employee').search(self.env.cr, self.env.uid,
                                                               [('id', '=', self.employee_id.id)])
        # raise  Warning(id)
        course_form = self.pool.get('ir.ui.view').browse(self.env.cr, self.env.uid, id[0], context=None)

        ctx = dict(
            default_employee_id=self.employee_id.id,
        )
        return {
            'name': 'Empleado',
            'type': 'ir.actions.act_window',
            'res_model': 'hr.employee',
            'res_id': existeEspecifica[0],
            'view_type': 'form',
            'view_mode': 'form',
            # 'target': 'current',
            # 'views': [(course_form.id, 'form')],
            # 'view_id': course_form.id,
            # 'flags': {'action_buttons': True},
            'context': ctx,
        }
    _name = 'hr.judiciales'
    _rec_name = 'employee_id'
    # _description = 'New Description'

    employee_id = fields.Many2one('hr.employee', 'Empleado', ondelete='cascade', required=True)
    tipo_demanda = fields.Selection(string="Tipo",
                                    selection=[('demandado', 'Demandado'), ('demandante', 'Demandante'), ],
                                    required=False, default='demandado')
    memo = fields.Char('Memo')
    tipo_documento = fields.Selection(string="Tipo Documento",
                                      selection=[('audienciaunica', 'Audiencia Unica'), ('oficio', 'Oficio'),
                                                 ('resolucion', 'Resolucion'), ('sentencia', 'Sentencia')],
                                      required=False, )
    nro_documento = fields.Char(string="N° Documento")
    tipo_demanda_documento = fields.Selection(string="Tipo",
                                              selection=[('demandado', 'Demandado'), ('demandante', 'Demandante'), ],
                                              required=False, default='demandante')
    demandante = fields.Char(string="Demandante")
    documento_identidad = fields.Char(string="Documento Identidad")
    materia = fields.Char(string="Materia")
    tipo_descuento = fields.Selection(string="Tipo Descuento", selection=[('sinefecto', 'Deje sin Efecto'),
                                                                          ('liquidacion', 'Descuento Liquidacion'),
                                                                          ('mensual', 'Descuento Mensual')],
                                      required=False)
    concepto = fields.Selection(string="Concepto",
                                selection=[('401', '401'), ('405', '405'), ('406', '406'), ('duda', 'Duda')],
                                required=False)
    desc_concepto = fields.Text(string="Desc. Concepto")
    forma_pago = fields.Selection(string="Forma de Pago",
                                  selection=[('chequecajamarca', 'Cheque Cajamarca'), ('chequelima', 'Cheque Lima'),
                                             ('consignacionjudicial', 'Consignacion Judicial'),
                                             ('depositobcp', 'Deposito al BCP'),
                                             ('depositoscotiabank', 'Deposito al Scotiabank'),
                                             ('depositobn', 'Deposito al Banco de la Nacion'),
                                             ('noindica', 'No indica')])
    cuenta = fields.Char(string="Cuenta")
    tipo_importe_descuento = fields.Selection([('amount', 'Monto'), ('percent', 'Porcentaje')],
                                            string="Tipo de descuento")
    importe_descontar = fields.Float(string="Importe de Descuento",
                                   default=0.00,
                                   help='Ingrese un monto a descontar (Ejemplo: para 50% solo coloque 50.0)', required=True)

    tipo_moneda = fields.Selection(string="Tipo de moneda",
                                   selection=[('nacional', 'Moneda Nacional'), ('extranjera', 'Moneda Extranjera')],
                                   default='nacional')
    nro_proceso = fields.Char(string="N° de Proceso")
    juzgado = fields.Char(string="Juzgado")
    provincia = fields.Char(string="Provincia")
    inicio_vigencia = fields.Date(string='Inicio de Vigencia', required=True)
    fin_vigencia = fields.Date(string='Fin de Vigencia', required=True)
    fecha_creacion = fields.Date(string='Fecha de Creacion', required=True)


    # @api.one
    # @api.depends('importe_descontar', 'tipo_importe_descuento')
    # def _compute_descuento(self):
    #     if self.global_discount > 0 and self.global_discount_type:
    #         _logger.info("Entre descontar")
    #         descuento = self.importe_descontar
    #
    #         if self.tipo_importe_descuento in ['amount']:
    #             self.amount_untaxed_global_discount = discount or 0.0
    #             self.monto_condescuento = (self.amount_total - discount) or 0.0
    #             # self.monto_condescuento += self.percepcion
    #             _logger.info('>>>monto>>>' + str(self.amount_untaxed_global_discount))
    #
    #         elif self.tipo_importe_descuento in ['percent']:
    #             self.amount_untaxed_global_discount = self.amount_total * ((discount / 100.0) or 0.0)
    #             self.monto_condescuento = self.amount_total * (1 - ((discount / 100.0) or 0.0))
    #             # self.monto_condescuento += self.percepcion
    #             _logger.info('>>>poncentaje>>>' + str(self.amount_untaxed_global_discount))


class hr_contract_periodos(models.Model):
    def default_fecha_contract(self):
        return fecha_row_contrato

    _name = 'hr.contract.periodos'
    # _rec_name = 'name'
    # _description = 'New Description'

    categoria = fields.Selection(string="Categoría",
                                 selection=[('1', 'Trabajador'), ('2', 'Pensionista'), ('4', 'Personal de Terceros'),
                                            ('5', 'Personal en Formación-modalidad formativa laboral'), ],
                                 required=False, default='1')
    tipo_registro = fields.Selection(string="Tipo de registro",
                                     selection=[('1', 'Período'), ('2', 'Tipo de trabajador'),
                                                ('3', 'Régimen de Aseguramiento de Salud'),
                                                ('4', 'Régimen pensionario'), ('5', ' SCTR Salud'), ], required=False,
                                     default='1')
    fecha_inicio = fields.Date(string="Fecha de Inicio o Reinicio", required=False, default=default_fecha_contract)
    fecha_fin = fields.Date(string="Fecha de Fin", required=False, )
    indicador_motivo_fin = fields.Many2one('catalogo.motivo.baja.registro.17', 'Motivo Fin de Período')
    indicador_tipo_trabajador = fields.Many2one('catalogo.tipo.trabajador.8', 'Tipo de trabajador')
    indicador_regimen_aseguramiento = fields.Many2one('catalogo.regimen.aseguramiento.32', 'Régimen Aseg. de Salud')
    indicador_regimen_pensionario = fields.Many2one('catalogo.regimen.pensionario.11', 'Régimen Pensionario')
    indicador_sctr_salud = fields.Selection(string="SCTR Salud", selection=[('1', 'EsSalud'), ('2', 'EPS')],
                                            required=False, )
    eps_servicio_propio = fields.Many2one('catalogo.entidades.prestadoras.salud.14', 'EPS/Servicios Propios')

    periodo_id = fields.Many2one('hr.contract', 'Contrato', ondelete='cascade')


class hr_contract_salarios(models.Model):
    _name = 'hr.contract.salarios'

    _order = 'fecha_inicio desc'


    @api.model
    def create(self, vals):
        new_id = super(hr_contract_salarios, self).create(vals)
        new_object = self.env['hr.contract.salarios'].browse(new_id.id)
        contract_object = self.env['hr.contract'].browse(new_id.salarios_id.id)
        self._cr.execute('SELECT salario_basico, tipo_pago FROM hr_contract_salarios WHERE salarios_id = %s ORDER BY id desc LIMIT 1', [contract_object.id])
        if self._cr.rowcount > 0:
            datos = self._cr.fetchone()
            contract_object.write({'wage': datos[0], 'tipo_pago': datos[1]})
        return new_id

    @api.multi
    def write(self, vals):
        print (vals)
        contract_object = self.env['hr.contract'].browse(self.salarios_id.id)
        print (contract_object)
        if 'tipo_pago' in vals:
            contract_object.write({'tipo_pago': vals['tipo_pago']})
        elif 'salario_basico' in vals:
            contract_object.write({'wage': vals['salario_basico']})
        else:
            pass
        # if self._cr.rowcount > 0:
        #     print ('dddd')
        #     datos = self._cr.fetchone()
        #     contract_object.write({'wage': datos[0], 'tipo_pago': datos[1]})
        return super(hr_contract_salarios, self).write(vals)


    fecha_inicio = fields.Date(string="Fecha de Inicio", required=True, default=lambda *a: dt.now().strftime('%Y-%m-%d'))
    fecha_fin = fields.Date(string="Fecha de Fin", required=True, default=lambda *a: dt.now().strftime('9999-12-12'))
    tipo_pago = fields.Selection(string='Tipo de Pago', selection=[('1', 'EFECTIVO'),
                                                                   ('2', 'DEPOSITO EN CUENTA'),
                                                                   ('3', 'OTROS')], required=True)
    salario_basico = fields.Float('Salario Basico', digits=dp.get_precision('Account'), required=True)
    salarios_id = fields.Many2one('hr.contract', 'Contrato', ondelete='cascade')

    @api.onchange('fecha_inicio')
    def onchange_fecha_inicio(self):
        fecha_menos_uno = date(int(self.fecha_inicio[0:4]), int(self.fecha_inicio[5:7]),int(self.fecha_inicio[-2:])) - timedelta(days=1)
        salarios = self.search([['salarios_id','=',id_contrato]], order='id desc', limit=1)
        if salarios:
            print (fecha_menos_uno)
            print (salarios)
            salarios.write({'fecha_fin':str(fecha_menos_uno)})

class hr_salary_rule(models.Model):
    _inherit = 'hr.salary.rule'
    _description = 'Salary Rule'
    afectacion_quinta = fields.Boolean('Afectación a 5ta Cat.', help='Marque si desea que esto sume para calcular quinta')
    afectacion_afp = fields.Boolean('Afectación a AFP.', help='Marque si desea que esto se utilice para calcular AFP')


class account_fiscalyear(models.Model):
    # _name = 'new_module.new_module'
    _inherit = 'account.fiscalyear'

    # code = fields.Integer([(num, str(num)) for num in range(1980, (datetime.datetime.now().year) + 15)],required=True)
    code = fields.Integer(help='Colocar el numero de año',required=True)


class hr_documentos_empleado(models.Model):
    _name = 'hr.documentos.empleado'
    # _inherit = 'res.partner.bank'

    employee_id = fields.Many2one('hr.employee', 'Empleado', ondelete='cascade')
    nombre_documento = fields.Char('Nombre', required=True)
    descripcion = fields.Text('Descripcion')
    quien_hizo = fields.Char('Responsable', compute='_quien_hizo', store=True)
    documentos = fields.Many2many('ir.attachment', 'documento_empleado_ir_attachments_rel', 'documento_empleado_id', 'attachment_id', 'Documento')

    @api.one
    @api.depends('write_uid')
    def _quien_hizo(self):
        nombre_create = self.env['res.users'].search([['id', '=', self.write_uid.id]])
        self.quien_hizo = str(nombre_create.partner_id.name)


class hr_payslip_run(models.Model):
    # _name = 'new_module.new_module'
    _inherit = 'hr.payslip.run'

    @api.multi
    def generar_pdfs_empelados(self):
        mes_start = self.date_start[5:-3]
        anio_start = self.date_start[:4]

        fecha_desde = self.date_start
        fecha_hasta = self.date_end

        empleados = []
        ids_employees = self.env['hr.payslip'].search([['payslip_run_id','=', self.id]])
        for emp in ids_employees:
            empleados.append(emp.employee_id.id)

        data = {'slip': self.id,'mes': mes_start, 'anio': anio_start, 'empleados': empleados, 'desde': fecha_desde, 'hasta': fecha_hasta}
        res = self.env['report'].get_action(self, 'horario_empleados.report_nominas_empleados_pdf', data=data)
        return res


class hr_liquidacion_empresa_anterior(models.Model):
    _name = 'hr.liquidacion.empresa.anterior'

    def _anio_get_fnc(self):
        today = datetime.datetime.now()
        return today.year

    employee_id = fields.Many2one('hr.employee', 'Empleado', ondelete='cascade')
    empresa_anterior = fields.Char('Empresa Anterior')
    monto_total_liquidacion = fields.Float('Monto total Liquidación')
    monto_descuento_quinta = fields.Float('Monto desc. Quinta')

    liquidacion_anterior = fields.Boolean('¿Pagado?')

    code = fields.Selection([(num, str(num)) for num in range(1900, (datetime.datetime.now().year) + 200)], 'Año de ingreso', required=True, default=_anio_get_fnc)


class hr_payslip(models.Model):
    # _name = 'new_module.new_module'
    _inherit = 'hr.payslip'

    generar_liquidacion = fields.Boolean('¿Es Liquidación?')

    @api.multi
    def generar_pdfs_empelado_solo(self):
        mes_start = self.date_from[5:-3]
        anio_start = self.date_from[:4]

        fecha_desde = self.date_from
        fecha_hasta = self.date_to
        #
        # empleados = []
        # ids_employees = self.env['hr.payslip'].search([['payslip_run_id','=', self.id]])
        # for emp in ids_employees:
        #     empleados.append(emp.employee_id.id)
        contrato = self.env['hr.contract'].search([['employee_id', '=', 1]], order='id desc', limit=1)

        data = {'slip': self.id, 'mes': mes_start, 'anio': anio_start, 'empleados': [self.employee_id.id], 'desde': fecha_desde, 'hasta': fecha_hasta, 'basico': contrato.wage, 'id_emp': contrato.employee_id.id}
        res = self.env['report'].get_action(self, 'horario_empleados.report_nominas_empleados_pdf', data=data)
        return res

    @api.multi
    def generar_pdfs_liquidacion(self):
        mes_start = self.date_from[5:-3]
        anio_start = self.date_from[:4]

        fecha_desde = self.date_from
        fecha_hasta = self.date_to
        #
        # empleados = []
        # ids_employees = self.env['hr.payslip'].search([['payslip_run_id','=', self.id]])
        # for emp in ids_employees:
        #     empleados.append(emp.employee_id.id)
        contrato = self.env['hr.contract'].search([['employee_id', '=', self.employee_id.id]], order='id desc', limit=1)

        data = {'slip': self.id, 'mes': mes_start, 'anio': anio_start, 'empleado': self.employee_id.name_related, 'cargo': self.employee_id.job_id.name, 'departamento': self.employee_id.department_id.name, 'id_emp': self.employee_id.id, 'documento': self.employee_id.identification_id, 'desde': fecha_desde, 'hasta': fecha_hasta, 'contrato': contrato.date_start, 'basico': contrato.wage, 'cese': contrato.date_end}
        res = self.env['report'].get_action(self, 'horario_empleados.report_liquidacion_empleado_pdf', data=data)
        print(res)
        return res


class res_partner_bank(models.Model):
    # _name = 'new_module.new_module'
    _inherit = 'res.partner.bank'

    # name = fields.Char()
    propietario_el_mismo = fields.Boolean(string="Mismo Empleado",)


# para guardar el historial de los calculos de quinta como (gratificacion meses anteriores)
class hr_history_quinta(models.Model):
    _name = 'hr.history.quinta'
    # _rec_name = 'name'
    # _description = 'New Description'

    anio = fields.Integer(string="Año", required=False, )
    mes = fields.Integer(string="Mes", required=False, )
    contract_id = fields.Many2one(comodel_name="hr.contract", string="Contrato", required=False, )
    employee_id = fields.Many2one(comodel_name="hr.employee", string="Empleado", required=False, )
    concepto = fields.Char(string="Concepto", required=False, )
    monto = fields.Float(string="Concepto", required=False, )
    nomina_id = fields.Many2one(comodel_name='hr.payslip', string="Concepto", ondelete='cascade')


class hr_payslip(models.Model):
    _inherit = 'hr.payslip'

    nomina_ids = fields.One2many(comodel_name="hr.history.quinta", inverse_name="nomina_id", string="nomina_id")
