# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import print_function
import dateutil.parser
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
import datetime
import calendar
# from datetime import date,timedelta
from datetime import date, timedelta
import time
import pytz
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from openerp.exceptions import except_orm, ValidationError
from dateutil.relativedelta import relativedelta
from openerp import http

ids_tramo_general = ''

globvar = ''
globArea = ''
globCliente = ''
costo_varios_clientes = ''
conductor = ''
unidad_rt = ''
str_km_fin = ''
str_tipo_unidad = ''
str_placa = ''
str_empresa = ''
str_anio = ''
str_capacidad = ''
str_motor = ''
str_conductores = ''
str_placas = ''
fecha_inicio = ''
fecha_fin = ''
str_horario_unidad = ''
str_horario_ruta = ''
str_kilometraje_unidad = ''
str_kilometraje_ruta = ''
str_especifico_unidad = ''
str_especifico_ruta = ''
int_default = ''

codigo_pant_esp_default = 0


class modulo_valorizaciones_unidad(models.Model):
    _name = 'modulo_valorizaciones.unidad'
    _inherit = 'fleet.vehicle'
    costo_asiento = fields.Float('Costo por Asiento', required=True)
    precio = fields.Float('Precio Unitario')
    alquilado_propio = fields.Boolean('¿Alquilado?')
    proveedor = fields.Many2one('res.partner', string='Proveedor')
    tipo_unidad = fields.Many2one('modulo_valorizaciones.tipo_unidad', 'Tipo Unidad', required=True)
    activo = fields.Boolean('Inactivo')
    anio = fields.Char('Año')
    horsepower = fields.Char('Motor')


class fleet_vehicle(models.Model):
    _inherit = 'fleet.vehicle'
    costo_asiento = fields.Float('Costo por Asiento', required=True)
    precio = fields.Float('Precio Unitario')
    alquilado_propio = fields.Boolean('¿Alquilado?')
    proveedor = fields.Many2one('res.partner', string='Proveedor')
    activo = fields.Boolean('Inactivo')
    anio = fields.Char('Año')
    horsepower = fields.Char('Motor')
    parent_documento_ids = fields.One2many('fleet.documento.vehiculo', 'documento_id', 'Documentos de Vehiculo')


fleet_vehicle()


class fleet_documento_vehiculo(models.Model):
    def fields_view_get(self, cr, uid, view_id=None, view_type='form',
                        context=None, toolbar=False, submenu=False):
        if context is None:
            context = {}
        res = super(fleet_documento_vehiculo, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type,
                                                                    context=context, toolbar=toolbar, submenu=False)
        cr.execute("""SELECT * FROM fleet_documento_vehiculo""")
        re = cr.dictfetchall()
        for r in re:
            cur_date = datetime.datetime.now().date()
            new_date = dateutil.parser.parse(r['fecha_vencimiento']).date() - datetime.timedelta(
                days=r['nro_dias_antes_alerta'])
            if cur_date >= new_date:
                # print ('consulta update True')
                cr.execute("""UPDATE fleet_documento_vehiculo SET check_date = %s WHERE fecha_vencimiento=%s""",
                           (True, r['fecha_vencimiento']))
            else:
                cr.execute("""UPDATE fleet_documento_vehiculo SET check_date = %s WHERE fecha_vencimiento=%s""",
                           (False, r['fecha_vencimiento']))
                # print('consulta update Falso')
                # for rec in r:
                #     print(rec)
                #     order_date = dateutil.parser.parse(rec.fecha_vencimiento).date()
                #     print(order_date)
                #     if order_date > new_date:
                #         rec.check_date = True

        return res

    @api.model
    def _cron_notificaciones_vehiculos(self):
        self.enviar_not_doc_vehiculos()

    @api.multi
    def enviar_not_doc_vehiculos(self):
        # Find the e-mail template
        template = self.env.ref('modulo_valorizaciones.docs_vehi_email_template')
        # You can also find the e-mail template like this:
        # template = self.env['ir.model.data'].get_object('mail_template_demo', 'example_email_template')
        if template:
            template_obj = self.env['email.template'].browse(template.id)
        body = template_obj.body_html
        body_old = body
        count = 0

        documentos = self.env['fleet.documento.vehiculo'].search([['check_date', '=', True]])
        _trs = []

        for d in documentos:
            _trs.append("<tr>"
                        "<td>" + d.documento_id.name + "</td>"
                        "<td>" + d.tipo_documento.name + "</td>"
                        "<td>" + d.fecha_vencimiento + "</td>"
                       "</tr>")
        a_str = "\n\r".join(_trs)
        # print(body)

        body += "<style>span.oe_mail_footer_access {display:block; text-align:center;color:grey;}</style>" \
                "<div style='border-radius: 2px; max-width: 1200px; height: auto;margin-left: auto;margin-right: auto;background-color:#f9f9f9;'>" \
                "<div style='height: auto;margin-left:12px;margin-top:30px;'>" \
                    "<p>Estimado, ${(object.name)},<br>" \
                    "<br>" \
                    "Se esta enviando los documentos de los vehiculos que estan a punto de vencerce.<br>" \
                    "Aquí el detalle:</p>" \
                    "<div>" \
                    "<table class='table table-bordered table-responsive'>" \
                    "    <tbody>" \
                    "        <tr>" \
                    "           <td style='text-align: center;'><strong><span style='background-color:#FFFFFF;'>Vehiculo</span></strong></td>" \
                    "           <td style='text-align: center;'><strong><span style=''background-color:#FFFFFF;'>Tipo de Documento</span></strong></td>" \
                    "           <td style='text-align: center;'><strong><span style=''background-color:#FFFFFF;'>Fecha de Vencimiento</span></strong></td>" \
                    "        </tr>" \
                    "%s" \
                    "    </tbody>" \
                    "</table>" \
                    "<p>Saludos,<br>" \
                    "${(object.company_id.name)}</p>" \
                    "</div>" \
                "</div> " % a_str

        template.write({'body_html': body})
        # values = {}
        # values.update({'body_html': body})

        # Send out the e-mail template to the user
        ids_docu = self.env['enviar.mails.documentos'].search([], order='id desc', limit=1)
        for id_emp in ids_docu.employee_ids:
            p = self.env['hr.employee'].search([['id', '=', id_emp.id]], limit=1)
            print(template.id)
            print(p.id)
            self.env['email.template'].browse(template.id).send_mail(p.id, force_send=True)
        template.write({'body_html': body_old})

    _name = 'fleet.documento.vehiculo'
    # _rec_name = 'name'
    # _description = 'New Description'
    _order = 'check_date desc'
    documento_id = fields.Many2one('fleet.vehicle', ondelete="cascade")
    tipo_documento = fields.Many2one('fleet.service.type', 'Tipo de Documento', required=True)
    fecha_vencimiento = fields.Date('Fecha Vencimiento', required=True)
    documentos = fields.Many2many('ir.attachment', 'class_vehiculo_ir_attachments_rel', 'class_id', 'attachment_id',
                                  'Documento')
    nro_dias_antes_alerta = fields.Integer('Alerta Nro Dias Antes', default=2, required=True)

    check_date = fields.Boolean()

    # @api.depends('fecha_vencimiento')
    # def _check_the_date(self):
    #


class fleet_vehicle_model(models.Model):
    _inherit = 'fleet.vehicle.model'
    tipo_unidad = fields.Many2one('modulo_valorizaciones.tipo_unidad', 'Tipo Unidad', required=True)


fleet_vehicle_model()


class modulo_valorizaciones_tipo_unidad(models.Model):
    _name = 'modulo_valorizaciones.tipo_unidad'
    name = fields.Char('Tipo', required=True)


class modulo_valorizaciones_ruta(models.Model):
    _name = 'modulo_valorizaciones.ruta'
    p_partida = fields.Many2one('modulo_valorizaciones.lugar', 'Punto de Partida', required=True)
    p_llegada = fields.Many2one('modulo_valorizaciones.lugar', 'Punto de Llegada', required=True)
    # distancia = fields.Integer('Distancia', required=True)
    # kilometros = fields.Char('Kilometros Recorridos', required=True)
    name = fields.Char('Nombre Ruta', required=True)
    # precio_unidad = fields.Float('Precio Unidad', required=True)
    estado = fields.Boolean('Activa')
    observaciones = fields.Text('Observaciones')


class modulo_valorizaciones_revision_vehiculo(models.Model):
    def _name_get_date(self):
        return time.strftime("%Y-%m-%d")

    def get_emp_det(self, cr, uid, ids, unidad, context=None):
        global unidad_rt
        global str_tipo_unidad
        global str_placa
        global str_empresa
        global str_anio
        global str_capacidad
        global str_motor
        unidad_rt = unidad
        v = {}
        if unidad:
            fac = self.pool.get('fleet.vehicle').browse(cr, uid, unidad, context=context)
            if fac.model_id.tipo_unidad.name:
                v['tipo'] = fac.model_id.tipo_unidad.id
                v['placa'] = fac.license_plate
                v['modelo'] = fac.model_id.tipo_unidad.name
                v['km_inicio'] = fac.odometer
                str_tipo_unidad = fac.model_id.tipo_unidad.id
                str_placa = fac.license_plate
                if fac.proveedor.id:
                    str_empresa = fac.proveedor.id
                    v['empresa'] = fac.proveedor
                else:
                    company = self.pool.get('res.company').browse(cr, uid, uid, context=context)
                    empresa = self.pool.get('res.partner').browse(cr, uid, company.id, context=context)
                    str_empresa = empresa.id
                    v['empresa'] = empresa
                str_anio = fac.anio
                str_capacidad = fac.seats
                str_motor = fac.horsepower
        return {'value': v}

    _name = 'modulo_valorizaciones.revision_vehiculo'
    _inherits = {'modulo_valorizaciones.revision_vehiculo_detalle': 'revision_tecnica_detalle_id',
                 'modulo_valorizaciones.proximo_mantenimiento': 'proximo_mantenimiento_id'}
    conductor = fields.Many2one('hr.employee', 'Conductor')
    unidad = fields.Many2one('fleet.vehicle', 'Vehículo', required=True)
    fecha = fields.Date('Fecha Registro', required=True, default=_name_get_date)
    km_inicio = fields.Float('Kilometraje Inicio')
    km_fin = fields.Float('Kilometraje Fin')
    km_total = fields.Float('Kilometraje Total')
    tipo = fields.Many2one('modulo_valorizaciones.tipo_unidad', 'Tipo Unidad')
    tanqueo_inicio = fields.Boolean('Tanqueo de Inicio')
    tanqueo_fin = fields.Boolean('Tanqueo de Fin')
    tanqueo_fin_total = fields.Char('Combustible')
    placa = fields.Char('Placa')
    modelo = fields.Char('Modelo')
    empresa = fields.Many2one('res.partner', 'Empresa')
    _rec_name = 'unidad'
    observaciones = fields.Text('Observaciones')

    @api.onchange('km_fin')
    def check_change_fin(self):
        global str_km_fin
        if self.km_fin - self.km_inicio > 0:
            self.km_total = self.km_fin - self.km_inicio
            str_km_fin = self.km_fin

    @api.onchange('km_inicio')
    def check_change_inicio(self):
        if self.km_fin - self.km_inicio > 0:
            self.km_total = self.km_fin - self.km_inicio

    @api.onchange('conductor')
    def check_change_conductor(self):
        global conductor
        conductor = self.conductor

    @api.model
    def create(self, vals):
        if float(vals['km_fin']) > 0:
            valores = \
                {'vehicle_id': vals['unidad']
                    , 'value': vals['km_fin']
                    , 'date': vals['fecha']
                 }

            self.env['fleet.vehicle.odometer'].create(valores)
        # self._cr.execute(""" INSERT INTO fleet_vehicle_odometer SET value=%s WHERE vehicle_id=%s""",
        #                  (vals['km_fin'], vals['unidad']))
        return super(modulo_valorizaciones_revision_vehiculo, self).create(vals)

    @api.multi
    def write(self, vals):
        unidad = self.unidad.id
        fecha = self.fecha
        km_fin = self.km_fin
        for item in vals.keys():
            if item == 'unidad':
                unidad = vals['unidad']
            elif item == 'fecha':
                fecha = vals['fecha']
            elif item == 'km_fin':
                km_fin = vals['km_fin']

        valores = \
            {'vehicle_id': unidad
                , 'value': km_fin
                , 'date': fecha
             }
        self.env['fleet.vehicle.odometer'].create(valores)
        res = super(modulo_valorizaciones_revision_vehiculo, self).write(vals)
        # self._cr.execute(""" INSERT INTO fleet_vehicle_odometer SET value=%s WHERE vehicle_id=%s""",
        #                  (self.km_fin, self.unidad.id))
        return res

    @api.multi
    def imprimir(self):
        """ Print the invoice and mark it as sent, so that we can see more
            easily the next step of the workflow
        """
        assert len(self) == 1, 'This option should only be used for a single id at a time.'
        return self.env['report'].get_action(self, 'modulo_valorizaciones.report_check_list')


class modulo_valorizaciones_revision_vehiculo_detalle(models.Model):
    _name = 'modulo_valorizaciones.revision_vehiculo_detalle'
    hora_inicio = fields.Float('Hora Inicio (24 Hrs)')
    hora_fin = fields.Float('Hora Fin (24 Hrs)')
    descripcion = fields.Char('Descripción')
    parent_detalle_id = fields.Many2one('modulo_valorizaciones.revision_vehiculo_detalle', 'Parent',
                                        help='Parent cost to this current cost')
    revision_tecnica_detalle_ids = fields.One2many('modulo_valorizaciones.revision_vehiculo_detalle',
                                                   'parent_detalle_id', 'Included Services')


class modulo_valorizaciones_proximo_mantenimiento(models.Model):
    _name = 'modulo_valorizaciones.proximo_mantenimiento'
    _inherits = {'modulo_valorizaciones.revision_tecnica': 'r_t_id'}
    fecha = fields.Date('Fecha')
    hora = fields.Float('Hora')
    tipo_revision = fields.Many2one('fleet.service.type', 'Tipo de Servicio')
    descripcion = fields.Char('Descripción')
    parent_proximo_id = fields.Many2one('modulo_valorizaciones.proximo_mantenimiento', 'Parent',
                                        help='Parent cost to this current cost')
    proximo_mantenimiento_ids = fields.One2many('modulo_valorizaciones.proximo_mantenimiento', 'parent_proximo_id',
                                                'Included Services')

    @api.onchange('fecha')
    def check_change_fecha(self):
        self.fecha_revisada = self.fecha

    @api.onchange('descripcion')
    def check_change_descripcion(self):
        self.observaciones = self.descripcion

    @api.onchange('tipo_revision')
    def check_change_tipo_revision(self):
        unidad = self.pool.get('fleet.vehicle').browse(self.env.cr, self.env.uid, self._context.get('unidad'),
                                                       context=None)
        self.unidad = unidad.id
        self.conductor = self._context.get('conductor')
        self.km_fin_revision_tecnica = unidad.odometer
        self.tipo_vehiculo_revision_tecnica = unidad.model_id.tipo_unidad.id
        self.placa_revision_tecnica = unidad.license_plate
        if self.unidad.proveedor:
            self.empresa_revision_tecnica = self.unidad.proveedor
        else:
            self.empresa_revision_tecnica = 1
        self.tipo_revision_tecnica = self.tipo_revision
        self.anio = unidad.anio
        self.capacidad = unidad.seats
        self.motor = unidad.horsepower


class modulo_valorizaciones_revision_tecnica(models.Model):
    def _name_get_fnc(self):
        return conductor

    def _name_get_unidad(self):
        return unidad_rt

    def _name_get_km_fin(self):
        return str_km_fin

    def _name_get_tipo_unida(self):
        return str_tipo_unidad

    def _name_get_placa(self):
        return str_placa

    def _name_get_empresa(self):
        return str_empresa

    def _name_get_anio(self):
        return str_anio

    def _name_get_capacidad(self):
        return str_capacidad

    def _name_get_motor(self):
        return str_motor

    def get_emp_det(self, cr, uid, ids, unidad, context=None):
        global unidad_rt
        unidad_rt = unidad
        v = {}
        print(unidad)
        if unidad:
            fac = self.pool.get('fleet.vehicle').browse(cr, uid, unidad, context=context)
            print(fac)
            if fac.tipo_unidad.name:
                v['tipo_vehiculo_revision_tecnica'] = fac.model_id.tipo_unidad.id
                v['placa_revision_tecnica'] = fac.license_plate
                v['empresa_revision_tecnica'] = fac.proveedor
                v['anio'] = fac.anio
                v['capacidad'] = fac.seats
                v['motor'] = fac.horsepower

        return {'value': v}

    _name = 'modulo_valorizaciones.revision_tecnica'

    conductor = fields.Many2one('hr.employee', 'Conductor', default=_name_get_fnc)
    unidad = fields.Many2one('fleet.vehicle', 'Vehículo', default=_name_get_unidad)
    fecha_revisada = fields.Date('Fecha Revisión')
    fecha_proxima_revision = fields.Date('Fecha Próxima Revisión')
    tipo_revision_tecnica = fields.Many2one('fleet.service.type', 'Tipo de Servicio')
    costo = fields.Float('Costo Total')
    estado = fields.Selection(
        [('Pendiente', 'Pendiente'), ('Programado', 'Programado'), ('Realizado', 'Realizado'), ('Pagado', 'Pagado')],
        'Estado', default='Programado')
    observaciones = fields.Text('Observaciones')
    proveedor = fields.Many2one('res.partner', 'Proveedor')
    n_factura = fields.Many2one('account.invoice', 'N° Factura del proveedor')
    km_fin_revision_tecnica = fields.Float('KM Fin', default=_name_get_km_fin)
    tipo_vehiculo_revision_tecnica = fields.Many2one('modulo_valorizaciones.tipo_unidad', 'Tipo Unidad',
                                                     default=_name_get_tipo_unida)
    placa_revision_tecnica = fields.Char('Placa', default=_name_get_placa)
    empresa_revision_tecnica = fields.Many2one('res.partner', 'Empresa', default=_name_get_empresa)
    anio = fields.Char('Año', default=_name_get_anio)
    capacidad = fields.Integer('Capacidad', default=_name_get_capacidad)
    motor = fields.Char('Número de Motor', default=_name_get_motor)
    _rec_name = 'unidad'
    _order = 'create_date desc'

    @api.model
    def create(self, vals):
        print(self._context.get('unidad'))
        self._cr.execute(""" UPDATE fleet_vehicle_odometer SET value=%s WHERE vehicle_id=%s""",
                         (vals['km_fin_revision_tecnica'], vals['unidad']))
        return super(modulo_valorizaciones_revision_tecnica, self).create(vals)

    @api.multi
    def write(self, vals):
        res = super(modulo_valorizaciones_revision_tecnica, self).write(vals)
        self._cr.execute(""" UPDATE fleet_vehicle_odometer SET value=%s WHERE vehicle_id=%s""",
                         (self.km_fin_revision_tecnica, self.unidad.id))
        return res

    @api.onchange('unidad')
    def check_change_unidad(self):
        self.tipo_vehiculo_revision_tecnica = self.unidad.model_id.tipo_unidad.id
        self.placa_revision_tecnica = self.unidad.license_plate
        if self.unidad.proveedor:
            self.empresa_revision_tecnica = self.unidad.proveedor
        else:
            self.empresa_revision_tecnica = 1
        self.anio = self.unidad.anio
        self.capacidad = self.unidad.seats
        self.motor = self.unidad.horsepower


class modulo_valorizaciones_tipo_revision(models.Model):
    _name = 'modulo_valorizaciones.tipo_revision'
    name = fields.Char('Tipo de Revisión')


class modulo_valorizaciones_conductor(models.Model):
    _name = 'modulo_valorizaciones.conductor'
    conductor = fields.Char('Conductor', required=True)
    tipo_conductor = fields.Char('Tipo de Conductor', required=True)
    estado = fields.Boolean('Estado', required=True)
    observaciones = fields.Text('Observaciones')


class modulo_valorizaciones_lugar(models.Model):
    _name = 'modulo_valorizaciones.lugar'
    name = fields.Char('Nombre Lugar', required=True)
    referencia = fields.Char('Referencia', required=True)
    country_id = fields.Many2one('res.country', 'Pais', required=True, default=175)
    state_id = fields.Many2one('res.country.state', 'Departamento')
    province_id = fields.Many2one('res.country.state', 'Provincia')
    district_id = fields.Many2one('res.country.state', 'Distrito')

    @api.multi
    def onchange_state(self, state_id):
        if state_id:
            state = self.env['res.country.state'].browse(state_id)
            return {'value': {'country_id': state.country_id.id}}
        return {}

    @api.multi
    def onchange_district(self, district_id):
        if district_id:
            state = self.env['res.country.state'].browse(district_id)
            return {'value': {'zip': state.code}}
        return {}

    def _display_address(self, cr, uid, address, without_company=False, context=None):

        '''
        The purpose of this function is to build and return an address formatted accordingly to the
        standards of the country where it belongs.

        :param address: browse record of the res.partner to format
        :returns: the address formatted in a display that fit its country habits (or the default ones
            if not country is specified)
        :rtype: string
        '''

        # get the information that will be injected into the display format
        # get the address format
        address_format = address.country_id.address_format or \
                         "%(street)s\n%(street2)s\n%(state_name)s-%(province_name)s-%(district_code)s %(zip)s\n%(country_name)s"
        args = {
            'district_code': address.district_id.code or '',
            'district_name': address.district_id.name or '',
            'province_code': address.province_id.code or '',
            'province_name': address.province_id.name or '',
            'state_code': address.state_id.code or '',
            'state_name': address.state_id.name or '',
            'country_code': address.country_id.code or '',
            'country_name': address.country_id.name or '',
            'company_name': address.parent_name or '',
        }
        for field in self._address_fields(cr, uid, context=context):
            args[field] = getattr(address, field) or ''
        if without_company:
            args['company_name'] = ''
        elif address.parent_id:
            address_format = '%(company_name)s\n' + address_format
        return address_format % args


class modulo_valorizaciones_mantenimiento(models.Model):
    _name = 'modulo_valorizaciones.mantenimiento'
    unidad = fields.Many2one('fleet.vehicle', 'Vehículo')
    precio = fields.Float('Precio Final', required=True)
    fecha = fields.Date('Fecha', required=True)


class modulo_valorizaciones_adicionales(models.Model):
    _name = 'modulo_valorizaciones.adicionales'
    nombre = fields.Char('Nombre', required=True)
    descripcion = fields.Text('Descripcion', required=True)
    tipo = fields.Char('Tipo', required=True)
    precio_unitario = fields.Float('Precio Unitario', required=True)
    tanqueado = fields.Float('Tanqueado', required=True)


class modulo_valorizaciones_tipo_valorizacion(models.Model):
    _name = 'modulo_valorizaciones.tipo_valorizacion'
    name = fields.Char('Nombre', required=True)
    adicional_id = fields.Many2many('modulo_valorizaciones.adicionales', 'modulo_valorizaciones_adicionales_rel',
                                    'adicional_tipo_valorizacion_id', 'adicional_id', 'Incluye', copy=False)


class modulo_valorizaciones_venta_servicio(models.Model):
    _name = 'modulo_valorizaciones.venta_servicio'
    cliente_id = fields.Many2one('res.partner', 'Cliente')


class modulo_valorizaciones_area(models.Model):
    _name = 'modulo_valorizaciones.area'
    name = fields.Char('Nombre Area', required=True)
    descripcion = fields.Char('Descripción', required=True)
    contacto = fields.Char('Contacto', required=True)


class fleet_vehicle_log_contract(models.Model):
    _name = 'modulo_valorizaciones.contrato_vehiculo'
    _inherit = 'fleet.vehicle.log.contract'
    # _inherits = {'modulo_valorizaciones.vehiculo_contrato_detalle': 'contrato_detalle_id'}
    # vehicle_id = fields.Many2one('fleet.vehicle')

    name = fields.Char('Nro', required=True)
    currency_id = fields.Integer('currency_id')
    cost_frequency = fields.Selection(required=False)
    costo_fijo = fields.Boolean('Costo Fijo')
    costo_variable = fields.Boolean('Costo Variable')
    costo_adicional = fields.Boolean('Costo Adicionales')
    # contrato_id = fields.Many2one('modulo_valorizaciones.vehiculo_contrato_detalle', 'Cost', ondelete='cascade')
    fechaInicio = fields.Date('Fecha Inicio', required=True)
    fechaFin = fields.Date('Fecha Fin')
    fechaFacturacion = fields.Date('Fecha Facturación', required=True)
    periodo_desde = fields.Date('del')
    periodo_hasta = fields.Date('al')
    id_factura = fields.Integer('Factura')
    num_dias = fields.Integer('Num Dias')
    nota = fields.Text('Nota')
    tipo_valorizacion_id = fields.Many2one('modulo_valorizaciones.tipo_valorizacion', 'Tipo Valorizacion',
                                           required=False)
    cliente = fields.Many2one('res.partner', 'Cliente')

    contrato_ids = fields.One2many('modulo_valorizaciones.vehiculo_contrato_detalle', 'parent_id', 'Included Services')

    @api.onchange('name')
    def check_change(self):
        global globvar
        globvar = self.name


class fleet_vehicle_log_contract(models.Model):
    """OBTNER DIA ACTUAL"""

    def _hoy_get_fnc(self):
        today = datetime.datetime.now()
        return today

    """FECHA ACTUAL MAS UN AÑO"""

    def _ultimoDia_get_fnc(self):
        today = datetime.datetime.now()
        if today.month < 10:
            mes = "0" + str(today.month)
        else:
            mes = today.month
        if today.day < 10:
            dia = "0" + str(today.day)
        else:
            dia = today.day
        dateMonthEnd = "%s-%s-%s" % (today.year + 1, mes, dia)
        return dateMonthEnd

    _inherit = 'fleet.vehicle.log.contract'
    # _inherits = {'modulo_valorizaciones.vehiculo_contrato_detalle': 'contrato_detalle_id'}
    name = fields.Char('Nro', required=True)
    currency_id = fields.Integer('currency_id')
    cost_frequency = fields.Selection(required=False)
    costo_fijo = fields.Boolean('Costo Fijo')
    costo_variable = fields.Boolean('Costo Variable')
    costo_adicional = fields.Boolean('Costo Adicionales')
    # contrato_id = fields.Many2one('modulo_valorizaciones.vehiculo_contrato_detalle', 'Cost', ondelete='cascade')
    fechaFacturacion = fields.Date('Fecha Facturación', required=True)
    fechaInicio = fields.Date('Fecha Inicio Contrato', required=True, default=_hoy_get_fnc)
    fechaFin = fields.Date('Fecha Expiración Contrato', required=True, default=_ultimoDia_get_fnc)
    periodo_desde = fields.Date('del')
    periodo_hasta = fields.Date('al')
    id_factura = fields.Integer('Factura')
    num_dias = fields.Integer('Num Dias')
    cliente = fields.Many2one('res.partner', 'Cliente')
    contratista = fields.Many2one('res.partner', 'Contratista', default=1)
    costo_varios_clientes = fields.Boolean('Varios Clientes')

    tipo_moneda = fields.Many2one('res.currency', 'Tipo Moneda', required=True)

    contrato_ids = fields.One2many('modulo_valorizaciones.vehiculo_contrato_detalle', 'parent_id', 'Included Services')

    modelo_valorizacion = fields.Selection(string="Modelo de Valorizacion", selection=[('yanacocha', 'Modelo Yanacocha'), ('varios', 'Modelo Varios'), ], required=True, )
    date_month = fields.Char(string='Date Month',compute='_get_date_month',store=True,readonly=True)

    cambio_estatico = fields.Boolean('¿Personalizar tipo de cambio?')

    @api.one
    @api.depends('fechaFacturacion')
    def _get_date_month(self):
        self.date_month = datetime.datetime.strptime(self.fechaFacturacion,'%Y-%m-%d').strftime('%m')

    # if cur_date >= new_date:
    #     # print ('consulta update True')
    #     cr.execute("""UPDATE fleet_documento_vehiculo SET check_date = %s where fecha_vencimiento=%s""",
    #                (True, r['fecha_vencimiento']))

    @api.onchange('costo_varios_clientes')
    def check_costo_varios_clientes_change(self):
        global costo_varios_clientes
        costo_varios_clientes = self.costo_varios_clientes
        if self.costo_varios_clientes:
            self.costo_variable = True
        else:
            self.costo_variable = False

    """ASIGNAR EL NAME ACTUAL SELECCIONADO QUE SE ASIGNARA POR DEFECTO AL DETALLE DEL CONTRATO"""

    @api.onchange('name')
    def check_change(self):
        global globvar
        globvar = self.name

    """ASIGNAR EL CLIENTE ACTUAL SELECCIONADO QUE SE ASIGNARA POR DEFECTO AL DETALLE DEL CONTRATO"""

    @api.onchange('cliente')
    def change_cliente(self):
        global globArea
        global globCliente
        globCliente = self.cliente.id
        if self.cliente.category_id.name:
            for fac in self.cliente.category_id:
                globArea = fac.id

    @api.multi
    def write(self, vals):
        global globArea
        global globCliente
        global costo_varios_clientes
        costo_varios_clientes = self.costo_varios_clientes
        # for contrato_ids in self.contrato_ids:
        #     if self.costo_varios_clientes:
        #         contrato_ids.write({'costo_varios_clientes': True})
        #     else:
        #         contrato_ids.write({'costo_varios_clientes': False})

        globCliente = self.cliente.id
        if self.cliente.category_id.name:
            for fac in self.cliente.category_id:
                globArea = fac.id
        return super(fleet_vehicle_log_contract, self).write(vals)

    @api.multi
    def name_get(self):

        # 'state': fields.selection([('open', 'En proceso'), ('toclose', 'Para cerrar'), ('closed', 'Finalizado')],
        TYPES = {
            'open': 'En proceso',
            'toclose': 'Para cerrar',
            'closed': 'Finalizado',
        }
        res = super(fleet_vehicle_log_contract, self).name_get()
        data = []
        for contrato in self:
            # raise Warning(contrato)
            fi = datetime.datetime.strptime(contrato.fechaInicio, '%Y-%m-%d')
            ff = datetime.datetime.strptime(contrato.fechaFin, '%Y-%m-%d')
            fi = fi.strftime('%d/%m/%Y')
            ff = ff.strftime('%d/%m/%Y')
            # print(fi)
            # print(ff)
            display_value = ''
            display_value += contrato.name or ""
            display_value += ' - '
            display_value += contrato.cliente.name or ""
            # display_value += ' ,'
            # display_value += fi or ""
            # display_value += ' ,'
            # display_value += ff or ""
            # display_value += ' ,'
            # display_value += TYPES[contrato.state] or ""
            data.append((contrato.id, display_value))
        return data

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        # res = super(fleet_vehicle_log_contract, self).name_search()
        args = args or []
        print (name)
        recs = self.browse()
        if name:
            recs = self.search([('name', operator, name)] + args, limit=limit)
        if not recs:
            recs = self.search([('cliente.name', operator, name)] + args, limit=limit)
        return recs.name_get()


fleet_vehicle_log_contract()


class modulo_valorizaciones_vehiculo_contrato_detalle(models.Model):
    def _name_get_fnc(self):
        return globvar

    def _area_get_fnc(self):
        return globArea

    def _cliente_get_fnc(self):
        # print (self._context.get('cliente'))
        if globCliente:
            pass
        else:
            global globCliente
            globCliente = self._context.get('cliente')
        print (globCliente)
        return globCliente

    def _costo_varios_clientes_get_fnc(self):
        return costo_varios_clientes

    _name = 'modulo_valorizaciones.vehiculo_contrato_detalle'
    ruta_id = fields.Many2one('modulo_valorizaciones.ruta', 'Ruta', required=True)
    unidad_id = fields.Many2one('fleet.vehicle', 'Vehiculo', required=True)
    area_id = fields.Many2one('res.partner.category', 'Area', default=_area_get_fnc)
    descripcion_rutas = fields.Char('Descripcion de Rutas')
    descripcion_fijo = fields.Char('Descripcion costo fijo')
    descripcion_variable = fields.Char('Descripcion costo variable')
    descripcion_adicional = fields.Char('Descripcion costoadicional')
    descripcion_proveedor = fields.Char('Descripcion proveedor')
    descripcion_proveedor_km = fields.Char('Descripcion proveedor km')
    horario_id = fields.Char('Dias x Semana')
    # parent_id = fields.Many2one('modulo_valorizaciones.vehiculo_contrato_detalle', 'Parent', help='Parent cost to this current cost')
    parent_id = fields.Many2one('fleet.vehicle.log.contract', 'Parent', help='Parent cost to this current cost',
                                ondelete='cascade')
    # contrato_ids = fields.One2many('modulo_valorizaciones.vehiculo_contrato_detalle', 'parent_id', 'Included Services')
    name = fields.Char(default=_name_get_fnc)
    tot_dias_fijo = fields.Float('Total Días', default=0)
    tot_dias_variable = fields.Float('Total Días', default=0)
    tot_dias_adicional = fields.Float('Total Días', default=0)
    tarifa_costo_fijo = fields.Float('Tarifa Costo', default=0)
    tarifa_costo_variable = fields.Float('Tarifa Costo', default=0)
    tarifa_costo_adicional = fields.Float('Tarifa Costo', default=0)
    importe_fijo = fields.Float('Importe', default=0)
    importe_variable = fields.Float('Importe', default=0)
    importe_adicional = fields.Float('Importe', default=0)
    km_fijo = fields.Float('Km Fijo', default=0)
    km_proveedor = fields.Float('Km Proveedor', default=0)
    importe_proveedor = fields.Float('Importe Proveedor', default=0)
    # cliente = fields.Many2one('res.partner', string='Cliente',
    #     related='parent_id.cliente')
    cliente = fields.Many2one('res.partner', 'Cliente', default=_cliente_get_fnc)
    codigo_proveedor = fields.Many2one('res.partner', 'Proveedor')


    costo_varios_clientes = fields.Boolean('costo_varios_clientes', default=_costo_varios_clientes_get_fnc)

    estado_detalle = fields.Char(string="Estado Detalle", required=False, default='nuevo')

    @api.model
    def create(self, vals):
        res = super(modulo_valorizaciones_vehiculo_contrato_detalle, self).create(vals)
        new_object = self.env['modulo_valorizaciones.vehiculo_contrato_detalle'].browse(res.id)
        print(new_object.create_date)

        return res


class modulo_valorizacion_tareo_mensual(models.Model):
    @api.one
    def _compute_iframe(self):
        url_path_browser = http.request.env['ir.config_parameter'].get_param('web.base.url')
        h = url_path_browser.split(':')
        # print ('******************************')  # BASE URL
        # print (http.request.env['ir.config_parameter'].get_param('web.base.url'))  # BASE URL
        # print (http.request.httprequest)
        # print (http.request.httprequest.full_path)
        # print('******************************')  # BASE URL
        if self.id:
            self.iframe = '<iframe marginheight="0" id="frameValorizaciones" marginwidth="0" frameborder = "0" src="http:'+h[1]+':81/valorizaciones/home/index/c/' + str(
                self.id) + '" width="100%" height="1000"/>'
        else:
            self.iframe = '<iframe marginheight="0" id="frameValorizaciones" marginwidth="0" frameborder = "0" src="http:'+h[1]+':81/valorizaciones/home/index/c/0" width="100%" height="1000"/>'

    @api.multi
    def _compute_creado(self):
        self.creado = True

    @api.multi
    def _compute_total(self):
        for fac in self:
            fac.costo_total_igv = fac.costo_total + fac.costo_total * 0.18

    def _default_iframe_create(self):
        url_path_browser = http.request.env['ir.config_parameter'].get_param('web.base.url')
        h = url_path_browser.split(':')
        abc = '<iframe marginheight="0" id="frameValorizaciones" marginwidth="0" frameborder = "0" src="http:'+h[1]+':81/valorizaciones/home/index/c/0" width="100%" height="1000"/>'
        return abc

    _name = 'modulo_valorizaciones.tareo_mensual'
    cliente_id = fields.Many2one('res.partner', 'Cliente')
    contrato = fields.Many2one('fleet.vehicle.log.contract', 'Contrato')
    fechaInicio = fields.Date('Fecha Inicio')
    fechaFin = fields.Date('Fecha Fin')
    fechaFacturacion = fields.Date('Fecha Facturación')
    tipo_moneda = fields.Many2one('res.currency', 'Tipo Moneda')
    costo_fijo = fields.Float('Costo Fijo')
    costo_variable = fields.Float('Costo Variable')
    costo_adicional = fields.Float('Costo Adicionales')
    costo_total = fields.Float('Total sin IGV')
    costo_total_igv = fields.Float('Total con IGV', compute='_compute_total')
    n_factura = fields.Many2one('account.invoice', 'N° Factura')
    estado = fields.Selection([('Pendiente', 'Pendiente'), ('Facturado', 'Facturado')], 'Estado', default='Pendiente')
    nota = fields.Text('Nota')
    _rec_name = 'cliente_id'
    creado = fields.Boolean('creado', default=False, compute='_compute_creado')
    iframe = fields.Html('Embedded Webpage', compute='_compute_iframe', sanitize=False, strip_style=False)
    iframe_create = fields.Html('Embedded Webpage', default=_default_iframe_create,
                                sanitize=False, strip_style=False, readonly=True)
    _order = 'fechaFacturacion desc'

    existe_fijo = fields.Char('existe_fijo')
    existe_variable = fields.Char('existe_variable')
    existe_adicional = fields.Char('existe_adicional')
    existe_varios_clientes = fields.Char('existe_varios_clientes')

    ver_nota_pdf = fields.Boolean('Ver Nota')
    unir_tareo_pdf = fields.Boolean('unir_tareo_pdf')
    dividir_tareo_pdf = fields.Boolean('dividir_tareo_pdf')

    tipo_cambio = fields.Float('Tipo de Cambio')

    date_month = fields.Char(string='Date Month',compute='_get_date_month',store=True,readonly=True)

    cambiar_descripciones = fields.Boolean('Cambiar descripciones')

    num_dias = fields.Integer('Num Dias')

    @api.one
    @api.depends('fechaFacturacion')
    def _get_date_month(self):
        self.date_month = datetime.datetime.strptime(self.fechaFacturacion,'%Y-%m-%d').strftime('%m')

    @api.multi
    def go_invoice(self):
        mod_obj = self.pool.get('ir.model.data')
        res = mod_obj.get_object_reference(self._cr, self._uid, 'account', 'invoice_form')
        res_id = res and res[1] or False,
        return {
            'name': 'Factura Cliente',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': [res_id],
            'res_model': 'account.invoice',
            'target': 'new',
            'res_id': self.n_factura.id,
            'type': 'ir.actions.act_window',
            'context': "{'type':'out_invoice'}",
        }

    @api.model
    def create(self):
        # new_id = super(modulo_valorizacion_tareo_mensual, self).create(vals)
        # self.method_redirect()
        return self.method_redirect()

    @api.multi
    def method_redirect(self):
        return {
            'view_type': 'tree',
            'view_mode': 'tree',
            'res_model': 'modulo_valorizaciones.tareo_mensual',
            'target': 'current',
            # 'res_id': the_resource_id,
            'type': 'ir.actions.act_window'
        }

    @api.multi
    def unlink(self):
        for dd in self:
            print(dd.contrato.id)
            self._cr.execute(
                """SELECT * FROM "fleet_vehicle_log_contract" JOIN "modulo_valorizaciones_vehiculo_contrato_detalle" ON "fleet_vehicle_log_contract"."id" = "modulo_valorizaciones_vehiculo_contrato_detalle"."parent_id" WHERE "fleet_vehicle_log_contract"."id" = %s""",
                [dd.contrato.id])
            r = self._cr.dictfetchall()

            for resultado in r:
                self._cr.execute(
                    """DELETE FROM modulo_valorizaciones_tareo WHERE fecha >= %s AND fecha <= %s AND idruta= %s AND idunidad = %s AND iddetalle_contrato = %s""",
                    (dd.fechaInicio, dd.fechaFin, resultado['ruta_id'], resultado['unidad_id'], resultado['id']))

                query = 'DELETE FROM modulo_valorizaciones_cambio_usuario WHERE modulo_valorizaciones_cambio_usuario."fechaInicio" = %s AND modulo_valorizaciones_cambio_usuario."fechaFin" = %s AND modulo_valorizaciones_cambio_usuario.contrato_detalle_id = %s'

                self._cr.execute(query, (dd.fechaInicio, dd.fechaFin, resultado['id']))

            self._cr.execute(
                """DELETE FROM modulo_valorizaciones_cambios_guardia WHERE fecha >= %s AND fecha <= %s AND iddetalle_contrato = %s""",
                (dd.fechaInicio, dd.fechaFin, dd.contrato.id))

        return super(modulo_valorizacion_tareo_mensual, self).unlink()

        # _inherit = 'hr_timesheet_sheet.sheet'
        # contrato_id = fields.Many2one('modulo_valorizaciones.contrato_vehiculo', 'Contrado')

        # def onchange_contrato_id(self, cr, uid, ids, contrato_id, context=None):
        #    department_id = False
        #    user_id = False

        #    if contrato_id:
        #        contr_id = self.pool.get('modulo_valorizaciones.vehiculo_contrato_detalle').browse(cr, uid, contrato_id, context=context)
        #        for detalle in contr_id.contrato_ids:
        #            print detalle.unidad_id.name
        #            print detalle.ruta_id.name
        #            print detalle.descripcion_rutas
        #    return {'value': {'department_id': department_id, 'user_id': user_id,}}

    @api.model
    def default_get(self, fields):
        if self._context is None:
            self._context = {}

        res = super(modulo_valorizacion_tareo_mensual, self).default_get(fields)
        ahora = datetime.datetime.now()
        res.update({'anio_actual': ahora.year, 'mes_actual': ahora.month})
        return res

class modulo_valorizaciones_tareo(models.Model):
    _name = 'modulo.valorizaciones.tareo'
    # _rec_name = 'name'
    # _description = 'New Description'

    idruta = fields.Integer()
    idunidad = fields.Integer()
    iddetalle_contrato = fields.Integer()
    monto = fields.Float()
    fecha = fields.Date()
    tipo = fields.Char()
    cambio = fields.Boolean()


class modulo_valorizaciones_sam(models.Model):
    def _conductores_get_fnc(self):
        return str_conductores

    def _name_placas_unidad(self):
        return str_placas

    @api.one
    @api.depends('sam_ids.total_detalle')
    def _compute_amount(self):
        self.amount_untaxed = sum(line.total_detalle for line in self.sam_ids)
        self.amount_tax = self.amount_untaxed * 0.18
        self.amount_total = self.amount_tax + self.amount_untaxed

    _name = 'modulo_valorizaciones.sam'
    _inherit = ['mail.thread']
    # _inherits = {'modulo_valorizaciones.sam_detalle': 'sam_detalle_id'}
    cliente_id = fields.Many2one('res.partner', 'Cliente')
    contact_id = fields.Many2one('res.partner', 'Contacto')
    tipo_moneda = fields.Many2one('res.currency', 'Tipo Moneda', default=165)
    fechaInicio = fields.Date('Fecha Inicio')
    fechaFin = fields.Date('Fecha Fin')
    fechaFacturacion = fields.Date('Fecha Facturación')
    facturado = fields.Boolean('Facturado', default=False)
    total = fields.Float('Total sin IGV')
    conductores = fields.Char('Conductor')
    placa = fields.Char('Placa')
    # sam_id = fields.Many2one('modulo_valorizaciones.sam_detalle', 'Cost', ondelete='cascade')
    amount_untaxed = fields.Float(string='Subtotal', store=True, readonly=True, compute='_compute_amount',
                                  track_visibility='always')
    amount_tax = fields.Float(string='Tax', store=True, readonly=True, compute='_compute_amount')
    amount_total = fields.Float(string='Importe', store=True, readonly=True, compute='_compute_amount')
    tipo_servicio = fields.Many2one('fleet.service.type', 'Tipo de Servicio')

    sam_ids = fields.One2many('modulo_valorizaciones.sam_detalle', 'parent_id', 'Included Services')

    enviado = fields.Boolean('Proforma enviada', default=False)

    _rec_name = 'cliente_id'

    state = fields.Selection(string="Estado", selection=[('preproforma', 'Pre-Proforma'),('proforma', 'Proforma Enviada'), ('prefactudado', 'Pre-Facturado'), ], required=False, default='preproforma')

    @api.multi
    def invoice_print(self):
        """ Print the invoice and mark it as sent, so that we can see more
            easily the next step of the workflow
        """
        assert len(self) == 1, 'This option should only be used for a single id at a time.'
        # self.sent = True
        return self.env['report'].get_action(self, 'modulo_valorizaciones.report_proforma')

    @api.multi
    def enviarproforma(self):
        """ Open a window to compose an email, with the edi invoice template
            message loaded by default
        """
        assert len(self) == 1, 'This option should only be used for a single id at a time.'
        # template = self.env.ref('account.email_template_edi_invoice')

        template = self.env.ref('modulo_valorizaciones.email_proforma_valorizacion_h',False)  # obtener el id del template a copiar
        # id_copia = template.copy()  # copiamos el template esto genera el mismo nombre y le agrega al final (copia)
        # id_copia.write({'name': str(
        #     self.numeracion) + '-credito'})  # ACTUALIZAMOS AL NOMBRE QUE QUERAMOS PARA PODER BUSCARLO A LA HORA DE ENVIAR EL EMAIL
        #
        # template = self.env['email.template'].search([['name', '=', str(self.numeracion) + '-credito']], limit=1)
        # print (template)
        if not template:
            raise Warning('Aviso!', 'La plantilla no existe!')

        compose_form = self.env.ref('mail.email_compose_message_wizard_form')

        par = self

        ctx = dict(
            default_model='modulo_valorizaciones.sam',
            default_res_id=par.id,
            default_use_template=bool(template),
            default_new_template_id=template.id,
            default_composition_mode='comment',
            mark_invoice_as_sent=False,
            # default_bank_line_id = self.id,
        )
        print(ctx)
        self.write({'state': 'proforma', 'enviado': True})
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }


    """CREAR FACTURA AL DAR CLICK EN EL BOTON FACTURAR"""

    @api.multi
    def facturar_tasks(self, context=None):
        self.write({'facturado': True})
        self.write({'prefactudado': True})
        for fac in self:

            journal_id = self.pool.get('account.journal').search(self.env.cr, self.env.uid, [('code', '=', '01')])
            account_id = self.pool.get('account.account').search(self.env.cr, self.env.uid, [('code', '=', '121100')])

            """VALIDAR SI EL CLIENTE ES CONTACTO DE UNA EMPRESA"""
            if fac.cliente_id.parent_id:
                vals = \
                    {'date_invoice': fac.fechaFacturacion
                        , 'partner_id': fac.cliente_id.id
                        , 'ruc': fac.cliente_id.parent_id.doc_number
                        , 'commercial_partner_id': fac.cliente_id.id
                        , 'journal_id': journal_id[0]
                        , 'account_id': account_id[0]
                        , 'amount_total': fac.amount_total
                        , 'amount_tax': fac.amount_tax
                        , 'amount_untaxed': fac.amount_untaxed
                        , 'residual': 0.00
                        , 'check_total': 0.00
                        , 'currency_id': fac.tipo_moneda.id
                     }
            else:
                vals = \
                    {'date_invoice': fac.fechaFacturacion
                        , 'partner_id': fac.cliente_id.id
                        , 'ruc': fac.cliente_id.doc_number
                        , 'commercial_partner_id': fac.cliente_id.id
                        , 'journal_id': journal_id[0]
                        , 'account_id': account_id[0]
                        , 'amount_total': fac.amount_total
                        , 'amount_tax': fac.amount_tax
                        , 'amount_untaxed': fac.amount_untaxed
                        , 'residual': 0.00
                        , 'check_total': 0.00
                        , 'currency_id': fac.tipo_moneda.id
                     }

            res = self.env['account.invoice'].create(vals)

            concepto_id = self.pool.get('einvoice.catalog.20').search(self.env.cr, self.env.uid,
                                                                      [('code', '=', '1001')])
            valsConcepto = \
                {'conceptos_tributarios': concepto_id[0]
                    , 'invoice_id': res.id
                    , 'monto_total': fac.amount_untaxed
                 }
            self.env['account.invoice.conceptos'].create(valsConcepto)

            account_detalle_id = self.pool.get('account.account').search(self.env.cr, self.env.uid,
                                                                         [('code', '=', '7041')])

            valsTax = \
                {'date_invoice': fac.fechaFacturacion
                    , 'account_id': account_detalle_id[0]
                    , 'sequence': 1
                    , 'company_id': 1
                    , 'invoice_id': res.id
                    , 'manual': False
                    , 'base_amount': fac.amount_untaxed
                    , 'base': fac.amount_untaxed
                    , 'tax_code_id': 17
                    , 'amount': fac.amount_tax
                    , 'tax_amount': fac.amount_tax
                    , 'base_code_id': 4
                    , 'afectacion_igv': 1
                    , 'name': 'IGV 18% Venta'
                 }

            self.env['account.invoice.tax'].create(valsTax)

            for line in fac.sam_ids:
                if line.km_recorrido > 0:
                    valsLine = \
                        {'invoice_id': res.id
                            , 'partner_id': fac.cliente_id.id
                            , 'name': line.descripcion
                            , 'quantity': line.km_recorrido
                            , 'product_id': 1
                            , 'price_unit': line.tarifa
                            , 'price_subtotal': line.total_detalle
                            , 'discount': line.descuento
                         }
                elif line.tot_dias > 0:
                    valsLine = \
                        {'invoice_id': res.id
                            , 'partner_id': fac.cliente_id.id
                            , 'name': line.descripcion
                            , 'quantity': line.tot_dias
                            , 'product_id': 1
                            , 'price_unit': line.tarifa
                            , 'price_subtotal': line.total_detalle
                            , 'discount': line.descuento
                         }
                resLine = self.env['account.invoice.line'].create(valsLine)

                self._cr.execute(""" INSERT INTO account_invoice_line_tax(invoice_line_id, tax_id) VALUES (%s, %s)""",
                                 (resLine.id, 1))

    @api.onchange('fechaInicio')
    def check_change_fechaInicio(self):
        global fecha_inicio
        fecha_inicio = self.fechaInicio

    @api.onchange('fechaFin')
    def check_change_fechaFin(self):
        global fecha_fin
        fecha_fin = self.fechaFin

    @api.onchange('sam_ids')
    def check_change_sam_ids(self):
        my_list_conductores = []
        my_list_placas = []
        global str_conductores
        global str_placas

        for sam_ids in self.sam_ids:
            if sam_ids.conductor:
                if self.buscarElemento(my_list_conductores, sam_ids.conductor.name) is None:
                    my_list_conductores.append(sam_ids.conductor.name)

        str_conductores = ''
        for i in range(0, len(my_list_conductores)):
            str_conductores += str(my_list_conductores[i]) + ', '
        self.conductores = str_conductores.rstrip(', ')

        for sam_ids in self.sam_ids:
            if sam_ids.unidad:
                if self.buscarElemento(my_list_placas, sam_ids.unidad.name) is None:
                    my_list_placas.append(sam_ids.unidad.name)

        str_placas = ''
        for i in range(0, len(my_list_placas)):
            str_placas += str(my_list_placas[i]) + ', '
        self.placa = str_placas.rstrip(', ')

    def buscarElemento(self, lista, elemento):
        for i in range(0, len(lista)):
            if lista[i] == elemento:
                return i

    @api.multi
    def button_act_imp(self):
        return self.write({'sam_ids': []})

    def numero_to_letras(self, numero):
        indicador = [("", ""), ("MIL", "MIL"), ("MILLON", "MILLONES"), ("MIL", "MIL"), ("BILLON", "BILLONES")]
        entero = int(numero)
        decimal = int(round((numero - entero) * 100))
        # print 'decimal : ',decimal
        contador = 0
        numero_letras = ""
        while entero > 0:
            a = entero % 1000
            if contador == 0:
                en_letras = self.convierte_cifra(a, 1).strip()
            else:
                en_letras = self.convierte_cifra(a, 0).strip()
            if a == 0:
                numero_letras = en_letras + " " + numero_letras
            elif a == 1:
                if contador in (1, 3):
                    numero_letras = indicador[contador][0] + " " + numero_letras
                else:
                    numero_letras = en_letras + " " + indicador[contador][0] + " " + numero_letras
            else:
                numero_letras = en_letras + " " + indicador[contador][1] + " " + numero_letras
            numero_letras = numero_letras.strip()
            contador = contador + 1
            entero = int(entero / 1000)
        numero_letras = numero_letras + " con " + str(decimal) + "/100"
        # print 'numero: ', numero
        return numero_letras

    def convierte_cifra(self, numero, sw):
        lista_centana = ["", ("CIEN", "CIENTO"), "DOSCIENTOS", "TRESCIENTOS", "CUATROCIENTOS", "QUINIENTOS",
                         "SEISCIENTOS",
                         "SETECIENTOS", "OCHOCIENTOS", "NOVECIENTOS"]
        lista_decena = ["", (
            "DIEZ", "ONCE", "DOCE", "TRECE", "CATORCE", "QUINCE", "DIECISEIS", "DIECISIETE", "DIECIOCHO", "DIECINUEVE"),
                        ("VEINTE", "VEINTI"), ("TREINTA", "TREINTA Y "), ("CUARENTA", "CUARENTA Y "),
                        ("CINCUENTA", "CINCUENTA Y "), ("SESENTA", "SESENTA Y "),
                        ("SETENTA", "SETENTA Y "), ("OCHENTA", "OCHENTA Y "),
                        ("NOVENTA", "NOVENTA Y ")
                        ]
        lista_unidad = ["CERO", ("UN", "UNO"), "DOS", "TRES", "CUATRO", "CINCO", "SEIS", "SIETE", "OCHO", "NUEVE"]
        centena = int(numero / 100)
        decena = int((numero - (centena * 100)) / 10)
        unidad = int(numero - (centena * 100 + decena * 10))
        # print "centena: ",centena, "decena: ",decena,'unidad: ',unidad

        texto_centena = ""
        texto_decena = ""
        texto_unidad = ""

        # Validad las centenas
        texto_centena = lista_centana[centena]
        if centena == 1:
            if (decena + unidad) != 0:
                texto_centena = texto_centena[1]
            else:
                texto_centena = texto_centena[0]

        # Valida las decenas
        texto_decena = lista_decena[decena]
        if decena == 1:
            texto_decena = texto_decena[unidad]
        elif decena > 1:
            if unidad != 0:
                texto_decena = texto_decena[1]
            else:
                texto_decena = texto_decena[0]
        # Validar las unidades
        # print "texto_unidad: ",texto_unidad
        if decena != 1:
            texto_unidad = lista_unidad[unidad]
            if unidad == 1:
                texto_unidad = texto_unidad[sw]

        return "%s %s %s" % (texto_centena, texto_decena, texto_unidad)


class modulo_valorizaciones_sam_detalle(models.Model):
    @api.onchange('fecha')
    def check_change_fecha(self):
        if not self.parent_id.fechaInicio:
            raise except_orm(('Error!'), ('Seleccion fecha inicio'))
        elif not self.parent_id.fechaFin:
            raise except_orm(('Error!'), ('Seleccion fecha fin'))
        if self.fecha:
            v = {}
            if str(self.fecha) < str(self.parent_id.fechaInicio):
                # self.fecha = fecha_inicio
                v['fecha'] = self.parent_id.fechaInicio
                return {'value': v,
                        'warning': {'title': 'Error', 'message': 'Fecha Seleccionada menor a fecha de inicio'}}
                # raise except_orm(('Error!'), ('Fecha Seleccionada menor a fecha de inicio'))
            elif str(self.fecha) > str(self.parent_id.fechaFin):
                # self.fecha = fecha_fin
                v['fecha'] = self.parent_id.fechaFin
                return {'value': v,
                        'warning': {'title': 'Error', 'message': 'Fecha Seleccionada mayor a fecha fin'}}
                # raise except_orm(('Error!'), ('Fecha Seleccionada mayor a fecha fin'))

    _name = 'modulo_valorizaciones.sam_detalle'
    fecha = fields.Date('Fecha')
    conductor = fields.Many2one('hr.employee', 'Conductor')
    unidad = fields.Many2one('fleet.vehicle', 'Placa')
    hora_partida = fields.Float('Hora Partida (24 Hrs)')
    hora_llegada = fields.Float('Hora Llegada (24 Hrs)')
    total_detalle = fields.Float('Total')
    tarifa = fields.Float('Tarifa')
    km_recorrido = fields.Float('KM Recorrido')
    tot_dias = fields.Float('Total días')
    servicio = fields.Float('Servicio')
    descuento = fields.Float('Descuento (%)')
    descripcion = fields.Text('Descripción')
    observaciones = fields.Text('Observaciones')
    parent_id = fields.Many2one('modulo_valorizaciones.sam', 'Parent', ondelete='cascade')

    @api.onchange('km_recorrido')
    def check_change_fin(self):
        self.total_detalle = self.km_recorrido * self.tarifa

    @api.onchange('descuento')
    def check_change_descuento(self):
        self.calcularDescuento()

    @api.onchange('tot_dias')
    def check_change_tot_dias(self):
        self.total_detalle = self.tot_dias * self.tarifa
        self.calcularDescuento()

    @api.onchange('tarifa')
    def check_change_inicio(self):
        self.total_detalle = self.km_recorrido * self.tarifa + self.tot_dias * self.tarifa
        self.calcularDescuento()

    def calcularDescuento(self):
        self.total_detalle = self.total_detalle - (self.total_detalle * self.descuento / 100)


class fleet_vehicle_log_fuel(models.Model):
    _inherit = 'fleet.vehicle.log.fuel'

    # @api.multi
    # def hora_default(self):
    #     from datetime import datetime
    #     # date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    #     # print (date_now)
    #     # # start = datetime.strptime(date_now, "%Y-%m-%d %H:%M:%S") + timedelta(hours=5)
    #     # start = datetime.strptime(date_now, "%Y-%m-%d %H:%M:%S")
    #     # print(start)
    #     # tz_date = start.strftime("%Y-%m-%d %H:%M:%S")
    #     # print(tz_date)
    #     # return tz_date
    #     date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    #     start = datetime.strptime(date_now, "%Y-%m-%d %H:%M:%S") + timedelta(hours=5)
    #     tz = pytz.timezone('America/Bogota')
    #     start2 = tz.localize(start)
    #     tz_date = start2.strftime("%Y-%m-%d %H:%M:%S")
    #     ### tz_date es la fecha correcta con la zona hroaria
    #     return tz_date

    proveedor = fields.Many2one('res.partner', string='Proveedor')
    monto_dinero = fields.Float('Dinero disponible')
    monto_galones = fields.Float('Galón(es) disponibles')
    encargado_aprobar = fields.Many2one('hr.employee', 'Encargado Aprobar Salida')
    encargado_ejecutar = fields.Many2one('hr.employee', 'Encargado Ejecutar Salida')
    estado = fields.Selection([('Creado', 'Creado'), ('Cancelado', 'Cancelado'), ('Facturado', 'Facturado')], 'Estado',
                              default='Creado')

    ultimo_odometro_vehiculo = fields.Float('Último odómetro', readonly=True)
    kilometro_recorrido = fields.Float('Kilómetros Recorridos', compute='_compute_kilometros_recorridos', store=True)
    rendimiento = fields.Float('Rendimiento', compute='_compute_kilometros_recorridos', store=True)

    date = fields.Date('Fecha', default=lambda *a: datetime.datetime.now().strftime('%Y-%m-%d'))
    hora = fields.Float('Hora (HH:MM)')
    liter = fields.Float('Galón(es)')

    @api.one
    @api.depends('ultimo_odometro_vehiculo', 'odometer', 'kilometro_recorrido', 'liter')
    def _compute_kilometros_recorridos(self):
        if self.ultimo_odometro_vehiculo == 0:
            self.kilometro_recorrido = 0.0
        else:
            if self.odometer > 0:
                self.kilometro_recorrido = abs(self.ultimo_odometro_vehiculo - self.odometer) or 0.0

        if self.kilometro_recorrido > 0 and self.liter > 0:
            self.rendimiento = (self.kilometro_recorrido / self.liter) or 0.0

    @api.onchange('proveedor')
    def check_change_proveedor(self):
        self.monto_dinero = self.proveedor.monto
        self.monto_galones = self.proveedor.combustible

    @api.onchange('price_per_liter')
    def check_change_price_per_liter(self):
        self.amount = (self.price_per_liter * self.liter) or 0.0

    # @api.onchange('vehicle_id')
    # def check_change_vehicle(self):
    #     self.ultimo_odometro_vehiculo = self.vehicle_id.odometer
    #     # self.odometer = self.vehicle_id.odometer

    @api.model
    def create(self, vals):
        vehicle = self.env['fleet.vehicle'].browse(vals['vehicle_id'])
        vals.update({'ultimo_odometro_vehiculo': vehicle.odometer})

        # if 'date' in vals:
        #     from datetime import datetime
        #     start = datetime.strptime(vals['date'], "%Y-%m-%d %H:%M:%S")
        #     tz = pytz.timezone('America/Bogota')
        #     start2 = tz.localize(start)
        #     tz_date = start2.strftime("%Y-%m-%d %H:%M:%S")
        #     vals['date'] = tz_date
        res = super(fleet_vehicle_log_fuel, self).create(vals)
        new_object = self.env['fleet.vehicle.log.fuel'].browse(res.id)
        print(new_object.create_date)

        if 'vehicle_id' in vals and 'odometer' in vals:
            self._cr.execute(""" UPDATE fleet_vehicle_odometer SET value=%s WHERE vehicle_id=%s AND create_date = %s""",
                             (vals['odometer'], vals['vehicle_id'], new_object.create_date))

        if 'proveedor' in vals and 'monto_dinero' in vals and 'monto_galones' in vals and 'amount' in vals:
            if vals['monto_dinero'] > 0 and vals['monto_galones'] > 0:
                self._cr.execute(""" UPDATE res_partner SET monto=%s, combustible=%s WHERE id=%s""",
                                 (vals['monto_dinero'] - vals['amount'], vals['monto_galones'] - vals['liter'],
                                  vals['proveedor']))
            else:
                self._cr.execute(""" UPDATE res_partner SET monto=%s, combustible=%s WHERE id=%s""",
                                 (0, 0, vals['proveedor']))

        return res

    @api.multi
    def write(self, vals):
        if 'vehicle_id' in vals:
            id_v = vals['vehicle_id']
        else:
            id_v = self.vehicle_id.id

        # if 'date' in vals:
        #     from datetime import datetime
        #     start = datetime.strptime(vals['date'], "%Y-%m-%d %H:%M:%S") - timedelta(hours=5)
        #     tz = pytz.timezone('America/Bogota')
        #     start2 = tz.localize(start)
        #     tz_date = start2.strftime("%Y-%m-%d %H:%M:%S")
        #     vals['date'] = tz_date
        # else:
        #     tz_date = self.date

        if 'ultimo_odometro_vehiculo' in vals:
            vehicle = self.env['fleet.vehicle'].browse(id_v)
            vals.update({'ultimo_odometro_vehiculo': vehicle.odometer})

        self._cr.execute(""" UPDATE fleet_vehicle_odometer SET value=%s WHERE vehicle_id=%s AND create_date = %s""",
                         (self.odometer, self.vehicle_id.id, self.create_date))

        res = super(fleet_vehicle_log_fuel, self).write(vals)

        # if 'monto_dinero' in vals and 'monto_galones' in vals:
        if self.monto_dinero > 0 and self.monto_galones > 0:
            self._cr.execute(""" UPDATE res_partner SET monto=%s, combustible=%s WHERE id=%s""",
                             (self.monto_dinero - self.amount, self.monto_galones - self.liter, self.proveedor.id))
        else:
            self._cr.execute(""" UPDATE res_partner SET monto=%s, combustible=%s WHERE id=%s""",
                             (0, 0, self.proveedor.id))
        return res

    @api.multi
    def imprimir(self):
        """ Print the invoice and mark it as sent, so that we can see more
            easily the next step of the workflow
        """
        assert len(self) == 1, 'This option should only be used for a single id at a time.'
        return self.env['report'].get_action(self, 'modulo_valorizaciones.report_linea_credito')

    def on_change_liter(self, cr, uid, ids, liter, price_per_liter, amount, monto_galones, monto_dinero, context=None):
        if liter:
            v = {}

            if monto_galones > 0:
                if liter > monto_galones:
                    v['liter'] = monto_galones
                    v['amount'] = round((monto_dinero * monto_galones) / monto_galones, 2)
                    return {'value': v,
                            'warning': {'title': 'Error', 'message': 'No tiene disponible la cantidad solicitada'}}
                else:
                    return {'value': {'amount': round((monto_dinero * liter) / monto_galones, 2), }}
            else:
                v['amount'] = (price_per_liter * liter) or 0.0

    """HEREDAR Y SOBREESCRIBIR EL METODO DEL PADRE PARA PODER REEMPLAZAR EL VALOR KILOMETERS POR KILOMETROS"""

    def on_change_vehicle(self, cr, uid, ids, vehicle_id, context=None):
        if not vehicle_id:
            return {}
        vehicle = self.pool.get('fleet.vehicle').browse(cr, uid, vehicle_id, context=context)
        if str(vehicle.odometer_unit) == 'kilometers':
            odometer_unit = 'Kilómetros'
        else:
            odometer_unit = vehicle.odometer_unit
        odometer = vehicle.odometer
        driver = vehicle.driver_id.id
        return {
            'value': {
                'odometer_unit': odometer_unit,
                'purchaser_id': None,
                'ultimo_odometro_vehiculo': odometer,
            }
        }


fleet_vehicle_log_fuel()


class modulo_valorizaciones_linea_credito(models.Model):
    _name = 'modulo_valorizaciones.linea_credito'
    fecha = fields.Date('Fecha de Salida')
    encargado_aprobar = fields.Many2one('hr.employee', 'Encargado Aprobar Salida')
    encargado_ejecutar = fields.Many2one('hr.employee', 'Encargado Ejecutar Salida')
    litros = fields.Float('Litros de Salida')
    proveedor = fields.Many2one('res.partner', string='Proveedor')
    monto_dinero = fields.Float('Dinero disponible')
    monto_galones = fields.Float('Litros disponibles')
    estado = fields.Selection(
        [('Cancelado', 'Cancelado'), ('Facturado', 'Facturado')], 'Estado', default='Cancelado')
    total_pagar = fields.Float('Total a pagar', required=True)
    usuario_delete = fields.Many2one('res.partner', string='Proveedor')
    eliminado = fields.Boolean('Eliminado', dafult=False)

    @api.multi
    def unlink(self):
        for linea in self:
            # raise Warning(_('You cannot delete an invoice which is not draft or cancelled. You should refund it instead.'))
            raise except_orm(('Error!'), ('Seleccion fecha inicio'))
        return super(modulo_valorizaciones_linea_credito, self).unlink()

    @api.multi
    def imprimir(self):
        """ Print the invoice and mark it as sent, so that we can see more
            easily the next step of the workflow
        """
        assert len(self) == 1, 'This option should only be used for a single id at a time.'
        return self.env['report'].get_action(self, 'modulo_valorizaciones.report_linea_credito')

    @api.onchange('proveedor')
    def check_change_proveedor(self):
        self.monto_dinero = self.proveedor.monto
        self.monto_galones = self.proveedor.combustible

    @api.onchange('litros')
    def check_change_litros(self):
        self.monto_galones = self.monto_galones - self.litros
        if self.proveedor.id:
            self._cr.execute(""" UPDATE res_partner SET combustible=%s WHERE id=%s""",
                             (self.monto_galones, self.proveedor.id))
            self._cr.execute(""" UPDATE modulo_valorizaciones_linea_credito SET monto_galones=%s
                                                       WHERE proveedor=%s""",
                             (self.monto_galones, self.proveedor.id))
            self.total_pagar = (self.monto_dinero * self.litros) / self.monto_galones


class modulo_valorizaciones_linea_credito_confirm(models.Model):
    _name = "modulo_valorizaciones.linea_credito_confirm"
    _description = "Confirm the selected invoices"

    def linea_credito_confirm(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        active_ids = context.get('active_ids', []) or []
        proxy = self.pool['modulo_valorizaciones.linea_credito']
        for record in proxy.browse(cr, uid, active_ids, context=context):
            record.write({'eliminado': True})
            record.write({'usuario_delete': uid})

        return {'type': 'ir.actions.act_window_close'}


class modulo_valorizaciones_pantalla_especifica(models.Model):
    @api.onchange('unidad')
    def check_change_unidad(self):
        global str_especifico_unidad
        str_especifico_unidad = self.unidad.id

    @api.onchange('ruta_id')
    def check_change_ruta_id(self):
        global str_especifico_ruta
        str_especifico_ruta = self.ruta_id.id

    def _get_unidad2(self):
        pantalla_especifica = self.env['modulo_valorizaciones.pantalla_general'].search(
            [('id', '=', ids_tramo_general)])
        return pantalla_especifica.unidad.id

    def _get_ruta2(self):
        pantalla_especifica = self.env['modulo_valorizaciones.pantalla_general'].search(
            [('id', '=', ids_tramo_general)])
        return pantalla_especifica.ruta_id.id

    _name = 'modulo_valorizaciones.pantalla_especifica'
    _rec_name = 'ruta_id'
    # _inherits = {'modulo_valorizaciones.cambios_especifica': 'c_e_id'}
    unidad = fields.Many2one('fleet.vehicle', 'Vehiculo', default=_get_unidad2)
    ruta_id = fields.Many2one('modulo_valorizaciones.ruta', 'Ruta', default=_get_ruta2)
    fecha_inicio = fields.Date('Fecha Inicio')
    fecha_fin = fields.Date('Fecha Fin')
    cambios_especifica_ids = fields.One2many('modulo_valorizaciones.cambios_especifica',
                                             'parent_cambios_id', 'Included Services')
    parent_pant_espec_id = fields.Many2one('modulo_valorizaciones.pantalla_general', 'Tramo General',
                                           ondelete="cascade")


class modulo_valorizaciones_cambios_especifica(models.Model):
    def _get_unidad(self):
        return str_especifico_unidad

    def _get_ruta(self):
        return str_especifico_ruta

    def _get_unidad2(self):
        pantalla_especifica = self.env['modulo_valorizaciones.pantalla_general'].search(
            [('id', '=', ids_tramo_general)])
        return pantalla_especifica.unidad.id

    def _get_ruta2(self):
        pantalla_especifica = self.env['modulo_valorizaciones.pantalla_general'].search(
            [('id', '=', ids_tramo_general)])
        return pantalla_especifica.ruta_id.id

    _name = 'modulo_valorizaciones.cambios_especifica'
    unidad = fields.Many2one('fleet.vehicle', 'Vehiculo', default=_get_unidad2)
    ruta_id = fields.Many2one('modulo_valorizaciones.ruta', 'Ruta', default=_get_ruta2)
    dia_inicio = fields.Selection(
        [(1, 'Lunes'), (2, 'Martes'), (3, 'Miercoles'), (4, 'Jueves'), (5, 'Viernes'), (6, 'Sábado'), (7, 'Domingo')],
        'Día Inicio', default=1)
    dia_fin = fields.Selection(
        [(1, 'Lunes'), (2, 'Martes'), (3, 'Miercoles'), (4, 'Jueves'), (5, 'Viernes'), (6, 'Sábado'), (7, 'Domingo')],
        'Día Fin', default=1)
    vuelta_subida = fields.Integer('N° Vuelta (subida)')
    vuelta_bajada = fields.Integer('N° Vuelta (bajada)')
    dia_normal = fields.Integer('Día Normal')
    parent_cambios_id = fields.Many2one('modulo_valorizaciones.pantalla_especifica', 'Parent',
                                        help='Parent cost to this current cost', ondelete="cascade")
    # parent_cambios_id = fields.Many2one('modulo_valorizaciones.cambios_especifica', 'Parent',
    #                                     help='Parent cost to this current cost')
    # cambios_especifica_ids = fields.One2many('modulo_valorizaciones.cambios_especifica',
    #                                       'parent_cambios_id', 'Included Services')


class modulo_valorizaciones_pantalla_general(models.Model):
    _name = 'modulo_valorizaciones.pantalla_general'
    _rec_name = 'ruta_id'
    # _inherits = {'modulo_valorizaciones.horario_general': 'horario_general_id',
    #              'modulo_valorizaciones.kilometraje_general': 'kilometraje_general_id'}
    unidad = fields.Many2one('fleet.vehicle', 'Vehìculo', required=True)
    ruta_id = fields.Many2one('modulo_valorizaciones.ruta', 'Ruta', required=True)
    descripcion = fields.Text('Descripción')
    costo_fijo = fields.Float('Costo Fijo')
    kilometraje = fields.Char('Kilometraje')
    formula_bajada = fields.Char('Fórmula Bajada')
    formula_subida = fields.Char('Fórmula Subida')
    valor_bajada = fields.Float('Valor bajada')
    valor_subida = fields.Float('Valor subida')
    tipo_moneda = fields.Many2one('res.currency', 'Tipo Moneda')
    fecha_inicio = fields.Date('Fecha Inicio', required=True)
    fecha_fin = fields.Date('Fecha Fin', required=True)
    personalizado = fields.Boolean('Personalizado')
    horario_general_ids = fields.One2many('modulo_valorizaciones.horario_general', 'parent_horario_id',
                                          'Included Services', copy=True)
    kilometraje_general_ids = fields.One2many('modulo_valorizaciones.kilometraje_general', 'parent_kilometraje_id',
                                              'Included Services', copy=True)
    pan_espec_ids = fields.One2many('modulo_valorizaciones.pantalla_especifica', 'parent_pant_espec_id', copy=True)

    ids_calendario = fields.One2many('modulo_valorizaciones.calendario',
                                     'id_calendario', copy=True)

    @api.multi
    def read(self, fields=None, load='_classic_read'):
        global ids_tramo_general
        id = 0
        for record in self:
            ids_tramo_general = record.id
        print(ids_tramo_general)
        res = super(modulo_valorizaciones_pantalla_general, self).read(fields=fields, load=load)
        return res

    # @api.multi
    # def write(self, vals):
    #
    #     if vals.has_key('unidad'):
    #         actunidad = vals['unidad']
    #     else:
    #         actunidad = self.unidad.id
    #     if vals.has_key('ruta_id'):
    #         actruta_id = vals['ruta_id']
    #     else:
    #         actruta_id = self.ruta_id.id
    #
    #     # s1 = self.horario_general_ids[-1]
    #     ss = self.horario_general_ids[0]
    #
    #     today = datetime.datetime.now()
    #     dateMonthEnd = "%s-%s-%s" % (today.year, 12, calendar.monthrange(today.year, today.month)[1])
    #     # dateMonthEnd = "%s-%s-%s" % (today.year, 12, calendar.monthrange(today.year - 1, today.month - 1)[1])
    #     # if vals.has_key('fecha_cambio'):
    #     # d1 = date(int(self.fecha_cambio[0:4]), int(self.fecha_cambio[5:7]), int(self.fecha_cambio[-2:]))
    #     d1 = date(int(ss.fecha_cambio[0:4]), int(ss.fecha_cambio[5:7]), int(ss.fecha_cambio[-2:]))
    #     d2 = date(int(dateMonthEnd[0:4]), int(dateMonthEnd[5:7]), int(dateMonthEnd[-2:]))
    #     diff = d2 - d1
    #     # if secuencia:
    #     dt = int(ss.secuencia)
    #     dd = 0
    #
    #     if ss.horario or actunidad or actruta_id:
    #         if int(ss.secuencia) - int(ss.horario.dias_trabajo) > 0:
    #             dd = (int(ss.secuencia) - int(ss.horario.dias_trabajo)) - 1
    #
    #         for j in range(0, (int(str(diff).split(' ', 1)[0]) + 1), 1):
    #             diasDelete = timedelta(days=j)
    #             fechaDelete = d1 + diasDelete
    #             self._cr.execute(
    #                 """ DELETE FROM modulo_valorizaciones_calendario WHERE unidad=%s AND ruta_id=%s AND fecha_cambio=%s""",
    #                 (self.unidad.id, self.ruta_id.id, fechaDelete))
    #
    #         for i in range(0, (int(str(diff).split(' ', 1)[0]) + 1), 1):
    #             dias = timedelta(days=i)
    #             fecha = d1 + dias
    #             if ss.horario.dias_descanso == 0:
    #                 valores = \
    #                     {'unidad': actunidad
    #                         , 'ruta_id': actruta_id
    #                         , 'fecha_cambio': fecha
    #                         , 'indicador': 'T'
    #                         , 'id_calendario': ss.parent_horario_id.id
    #                      }
    #             else:
    #                 if dt <= ss.horario.dias_trabajo:
    #                     valores = \
    #                         {'unidad': actunidad
    #                             , 'ruta_id': actruta_id
    #                             , 'fecha_cambio': fecha
    #                             , 'indicador': 'T'
    #                             , 'id_calendario': ss.parent_horario_id.id
    #                          }
    #                     dt = dt + 1
    #                 else:
    #                     if ss.horario.dias_descanso > 0:
    #                         dt = dt + 1
    #                         dd = dd + 1
    #                         valores = \
    #                             {'unidad': actunidad
    #                                 , 'ruta_id': actruta_id
    #                                 , 'fecha_cambio': fecha
    #                                 , 'indicador': 'D'
    #                                 , 'id_calendario': ss.parent_horario_id.id
    #                              }
    #                         if dd == ss.horario.dias_descanso:
    #                             dt = 1
    #                             dd = 0
    #                     else:
    #                         dt = 1
    #
    #             self.env['modulo_valorizaciones.calendario'].create(valores)
    #
    #     return super(modulo_valorizaciones_pantalla_general, self).write(vals)

    @api.multi
    def load_pantalla_especifica(self):
        # course_form = self.env.ref('modulo_valorizaciones.pantalla_especifica', False)
        id = self.pool.get('ir.ui.view').search(self.env.cr, self.env.uid,
                                                [('model', '=', 'modulo_valorizaciones.pantalla_especifica'),
                                                 ('type', '=', 'form')])

        existeEspecifica = self.pool.get('modulo_valorizaciones.pantalla_especifica').search(self.env.cr, self.env.uid,
                                                                                             [('unidad', '=',
                                                                                               self.unidad.id),
                                                                                              ('ruta_id', '=',
                                                                                               self.ruta_id.id),
                                                                                              ('parent_pant_espec_id',
                                                                                               '=', self.id)])

        course_form = self.pool.get('ir.ui.view').browse(self.env.cr, self.env.uid, id[0], context=None)

        ctx = dict(
            default_unidad=self.unidad.id,
            default_ruta_id=self.ruta_id.id,
            default_parent_pant_espec_id=self.id,
        )
        print(ctx)

        if existeEspecifica:
            return {
                'name': 'Tramo Específico',
                'type': 'ir.actions.act_window',
                'res_model': 'modulo_valorizaciones.pantalla_especifica',
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
                'name': 'Tramo Específico',
                'type': 'ir.actions.act_window',
                'res_model': 'modulo_valorizaciones.pantalla_especifica',
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'views': [(course_form.id, 'form')],
                'view_id': course_form.id,
                'flags': {'action_buttons': True},
                'context': ctx,
            }

    # @api.multi
    # def unlink(self):
    #     self._cr.execute(
    #         """ DELETE FROM modulo_valorizaciones_calendario WHERE id_calendario = %s""", [self.pan_espec_ids.id])
    #     return super(modulo_valorizaciones_pantalla_general, self).unlink()

    @api.onchange('formula_bajada')
    def check_change_formula_bajada(self):
        if self.formula_bajada:
            self.calcular_formulas()
        else:
            resultado = 0.00
            self.valor_bajada = resultado

    @api.onchange('formula_subida')
    def check_change_formula_subida(self):
        print(self.kilometraje_general_ids)
        if self.formula_subida:
            self.calcular_formulas()
        else:
            resultado = 0.00
            self.valor_subida = resultado

    @api.onchange('unidad')
    def check_change_unidad(self):
        global str_horario_unidad
        global str_kilometraje_unidad
        str_horario_unidad = self.unidad.id
        str_kilometraje_unidad = self.unidad.id

    @api.onchange('ruta_id')
    def check_change_ruta_id(self):
        global str_horario_ruta
        global str_kilometraje_ruta
        str_horario_ruta = self.ruta_id.id
        str_kilometraje_ruta = self.ruta_id.id
        global codigo_pant_esp_default
        codigo_pant_esp_default = self.id

    @api.onchange('kilometraje_general_ids')
    def check_change_kilometraje_general_ids(self):
        self.calcular_formulas()

    def calcular_formulas(self):
        valores = []
        signo = ''
        if self.formula_bajada:
            for i in range(0, len(self.formula_bajada), 1):
                if i % 2 == 0:
                    for km_ids in self.kilometraje_general_ids:
                        if km_ids.letra:
                            if km_ids.default:
                                if km_ids.letra == self.formula_bajada[i]:
                                    valores.append(str(int(km_ids.kilometraje) * int(km_ids.n_vueltas)))
                            else:
                                if km_ids.letra == self.formula_bajada[i]:
                                    valores.append(km_ids.kilometraje)
                else:
                    signo = self.formula_bajada[i]
        else:
            resultado = 0.00
            self.valor_bajada = resultado
        if signo == '+':
            resultado = 0
            for i in range(0, len(valores)):
                resultado = resultado + int(valores[i])
                self.valor_bajada = resultado
        if signo == '-':
            resultado = 0
            for i in range(0, len(valores)):
                resultado = resultado - int(valores[i])
                self.valor_bajada = resultado
        if signo == '*':
            resultado = 0
            for i in range(0, len(valores)):
                resultado = resultado * int(valores[i])
                self.valor_bajada = resultado
        if signo == '/':
            resultado = 0
            for i in range(0, len(valores)):
                resultado = resultado / int(valores[i])
                self.valor_bajada = resultado
        elif signo == '':
            if self.formula_bajada:
                resultado = valores[0]
                self.valor_bajada = resultado
            else:
                resultado = 0.00
                self.valor_bajada = resultado

        valores = []
        signo = ''
        if self.formula_subida:
            for i in range(0, len(self.formula_subida), 1):
                if i % 2 == 0:
                    for km_ids in self.kilometraje_general_ids:
                        if km_ids.letra:
                            if km_ids.default:
                                if km_ids.letra == self.formula_subida[i]:
                                    valores.append(str(int(km_ids.kilometraje) * int(km_ids.n_vueltas)))
                            else:
                                if km_ids.letra == self.formula_subida[i]:
                                    valores.append(km_ids.kilometraje)
                else:
                    signo = self.formula_subida[i]
        else:
            resultado = 0.00
            self.valor_subida = resultado
        if signo == '+':
            resultado = 0
            for i in range(0, len(valores)):
                resultado = resultado + int(valores[i])
                self.valor_subida = resultado
        elif signo == '-':
            resultado = 0
            for i in range(0, len(valores)):
                resultado = resultado - int(valores[i])
                self.valor_subida = resultado
        elif signo == '*':
            resultado = 0
            for i in range(0, len(valores)):
                resultado = resultado * int(valores[i])
                self.valor_subida = resultado
        elif signo == '/':
            resultado = 0
            for i in range(0, len(valores)):
                resultado = resultado / int(valores[i])
                self.valor_subida = resultado
        elif signo == '':
            if self.formula_subida:
                resultado = valores[0]
                self.valor_subida = resultado
            else:
                resultado = 0.00
                self.valor_subida = resultado


class modulo_valorizaciones_horario_general(models.Model):
    def _get_unidad(self):
        return str_horario_unidad

    def _get_ruta(self):
        return str_horario_ruta

    _order = 'fecha_cambio desc'
    _name = 'modulo_valorizaciones.horario_general'
    horario = fields.Many2one('modulo_valorizaciones.horario', 'Régimen')
    fecha_cambio = fields.Date('Fecha Cambio')
    secuencia = fields.Char('Indicador día de trabajo')
    unidad = fields.Many2one('fleet.vehicle', 'Unidad', default=_get_unidad)
    ruta_id = fields.Many2one('modulo_valorizaciones.ruta', 'Ruta', default=_get_ruta)
    # parent_horario_id = fields.Many2one('modulo_valorizaciones.horario_general', 'Parent',
    #                                         help='Parent cost to this current cost')
    parent_horario_id = fields.Many2one('modulo_valorizaciones.pantalla_general', 'Parent',
                                        help='Parent cost to this current cost', ondelete="cascade")

    # horario_general_ids = fields.One2many('modulo_valorizaciones.horario_general',
    #                                           'parent_horario_id', 'Included Services')

    # @api.onchange('fecha_cambio')
    # def check_change_fecha_cambio(self):
    #     self.agregarCalendario()

    # @api.onchange('secuencia')
    # def check_change_secuencia(self):
    #     self.agregarCalendario()

    # @api.onchange('horario')
    # def check_change_horario(self):
    #     self.agregarCalendario()
    #
    # @api.onchange('unidad')
    # def check_change_unidad(self):
    #     self.agregarCalendario()
    #
    # @api.onchange('ruta_id')
    # def check_change_ruta_id(self):
    #     self.agregarCalendario()

    @api.model
    def create(self, vals, context=None):
        # print (vals)
        new_id = super(modulo_valorizaciones_horario_general, self).create(vals)
        new_object = self.env['modulo_valorizaciones.horario_general'].browse(new_id.id)

        self._cr.execute("""SELECT unidad, ruta_id FROM modulo_valorizaciones_pantalla_general WHERE id = %s""",
                         [vals['parent_horario_id']])
        resultado2 = self._cr.fetchone()
        unidad = resultado2[0]
        ruta_id = resultado2[1]
        print('>>>>>>>>', str(unidad), str(ruta_id))
        if vals['fecha_cambio']:
            today = datetime.datetime.now()
            dateMonthEnd = "%s-%s-%s" % (today.year, 12, calendar.monthrange(today.year, today.month)[1])
            # dateMonthEnd = "%s-%s-%s" % (today.year, 12, calendar.monthrange(today.year - 1, today.month - 1)[1])

            d1 = date(int(vals['fecha_cambio'][0:4]), int(vals['fecha_cambio'][5:7]), int(vals['fecha_cambio'][-2:]))
            d2 = date(int(dateMonthEnd[0:4]), int(dateMonthEnd[5:7]), int(dateMonthEnd[-2:]))
            diff = d2 - d1
            # print(vals['secuencia'],vals['horario'], unidad, ruta_id)
            if vals['secuencia']:
                dt = int(vals['secuencia'])
                dd = 0
                if vals['horario'] and unidad and ruta_id:
                    self._cr.execute(
                        """SELECT dias_descanso, dias_trabajo FROM modulo_valorizaciones_horario WHERE id = %s""",
                        [vals['horario']])
                    resultado = self._cr.fetchone()
                    dias_descanso = resultado[0]
                    dias_trabajo = resultado[1]
                    if int(vals['secuencia']) - int(dias_trabajo) > 0:
                        dd = (int(vals['secuencia']) - int(dias_trabajo)) - 1

                    for j in range(0, (int(str(diff).split(' ', 1)[0]) + 1), 1):
                        diasDelete = timedelta(days=j)
                        fechaDelete = d1 + diasDelete
                        self._cr.execute(
                            """ DELETE FROM modulo_valorizaciones_calendario WHERE unidad=%s AND ruta_id=%s AND fecha_cambio=%s""",
                            (unidad, ruta_id, fechaDelete))

                    for i in range(0, (int(str(diff).split(' ', 1)[0]) + 1), 1):
                        dias = timedelta(days=i)
                        fecha = d1 + dias
                        if dias_descanso == 0:
                            valores = \
                                {'unidad': unidad
                                    , 'ruta_id': ruta_id
                                    , 'fecha_cambio': fecha
                                    , 'indicador': 'T'
                                    , 'id_calendario': vals['parent_horario_id']
                                 }
                        else:
                            if dt <= dias_trabajo:
                                valores = \
                                    {'unidad': unidad
                                        , 'ruta_id': ruta_id
                                        , 'fecha_cambio': fecha
                                        , 'indicador': 'T'
                                        , 'id_calendario': vals['parent_horario_id']
                                     }
                                dt = dt + 1
                            else:
                                if dias_descanso > 0:
                                    dt = dt + 1
                                    dd = dd + 1
                                    valores = \
                                        {'unidad': unidad
                                            , 'ruta_id': ruta_id
                                            , 'fecha_cambio': fecha
                                            , 'indicador': 'D'
                                            , 'id_calendario': vals['parent_horario_id']
                                         }
                                    if dd == dias_descanso:
                                        dt = 1
                                        dd = 0
                                else:
                                    dt = 1

                        self.env['modulo_valorizaciones.calendario'].create(valores)
        return new_id

    @api.multi
    def write(self, vals):

        self._cr.execute("""SELECT unidad, ruta_id FROM modulo_valorizaciones_pantalla_general WHERE id = %s""",
                         [self.parent_horario_id.id])
        resultado2 = self._cr.fetchone()
        unidad = resultado2[0]
        ruta_id = resultado2[1]

        if vals.has_key('fecha_cambio'):
            fecha_cambio = vals['fecha_cambio']
        else:
            fecha_cambio = self.fecha_cambio
        if vals.has_key('secuencia'):
            secuencia = vals['secuencia']
        else:
            secuencia = self.secuencia

        today = datetime.datetime.now()
        dateMonthEnd = "%s-%s-%s" % (today.year, 12, calendar.monthrange(today.year, today.month)[1])
        # dateMonthEnd = "%s-%s-%s" % (today.year, 12, calendar.monthrange(today.year - 1, today.month - 1)[1])
        # if vals.has_key('fecha_cambio'):
        # d1 = date(int(self.fecha_cambio[0:4]), int(self.fecha_cambio[5:7]), int(self.fecha_cambio[-2:]))
        d1 = date(int(fecha_cambio[0:4]), int(fecha_cambio[5:7]), int(fecha_cambio[-2:]))
        d2 = date(int(dateMonthEnd[0:4]), int(dateMonthEnd[5:7]), int(dateMonthEnd[-2:]))
        diff = d2 - d1
        if secuencia:
            dt = int(secuencia)
            dd = 0
            if self.horario and unidad and ruta_id:
                if int(secuencia) - int(self.horario.dias_trabajo) > 0:
                    dd = (int(secuencia) - int(self.horario.dias_trabajo)) - 1

                for j in range(0, (int(str(diff).split(' ', 1)[0]) + 1), 1):
                    diasDelete = timedelta(days=j)
                    fechaDelete = d1 + diasDelete
                    self._cr.execute(
                        """ DELETE FROM modulo_valorizaciones_calendario WHERE unidad=%s AND ruta_id=%s AND fecha_cambio=%s""",
                        (unidad, ruta_id, fechaDelete))

                for i in range(0, (int(str(diff).split(' ', 1)[0]) + 1), 1):
                    dias = timedelta(days=i)
                    fecha = d1 + dias
                    if self.horario.dias_descanso == 0:
                        valores = \
                            {'unidad': unidad
                                , 'ruta_id': ruta_id
                                , 'fecha_cambio': fecha
                                , 'indicador': 'T'
                                , 'id_calendario': self.parent_horario_id.id
                             }
                    else:
                        if dt <= self.horario.dias_trabajo:
                            valores = \
                                {'unidad': unidad
                                    , 'ruta_id': ruta_id
                                    , 'fecha_cambio': fecha
                                    , 'indicador': 'T'
                                    , 'id_calendario': self.parent_horario_id.id
                                 }
                            dt = dt + 1
                        else:
                            if self.horario.dias_descanso > 0:
                                dt = dt + 1
                                dd = dd + 1
                                valores = \
                                    {'unidad': unidad
                                        , 'ruta_id': ruta_id
                                        , 'fecha_cambio': fecha
                                        , 'indicador': 'D'
                                        , 'id_calendario': self.parent_horario_id.id
                                     }
                                if dd == self.horario.dias_descanso:
                                    dt = 1
                                    dd = 0
                            else:
                                dt = 1

                    self.env['modulo_valorizaciones.calendario'].create(valores)

        return super(modulo_valorizaciones_horario_general, self).write(vals)

    @api.multi
    def unlink(self):
        super(modulo_valorizaciones_horario_general, self).unlink()
        sortBy = "fecha_cambio desc"
        # self._cr.execute("""DELETE FROM modulo_valorizaciones_horario_general where id = %s""", [self.id])
        # self._cr.execute("""SELECT fecha_cambio FROM modulo_valorizaciones_horario_general where parent_horario_id = %s ORDER BY fecha_cambio desc LIMIT 1""",
        #                  [self.parent_horario_id.id])
        # resultado2 = self._cr.fetchone()[0]
        # print ('>>>>>>>>',str(resultado2))
        horario_general = self.env['modulo_valorizaciones.horario_general'].search(
            [('parent_horario_id', '=', ids_tramo_general)], limit=1, order=sortBy)
        print('>>>>>>>>', str(horario_general.fecha_cambio))
        if horario_general:
            self._cr.execute("""SELECT unidad, ruta_id FROM modulo_valorizaciones_pantalla_general WHERE id = %s""",
                             [horario_general.parent_horario_id.id])
            resultado2 = self._cr.fetchone()
            unidad = resultado2[0]
            ruta_id = resultado2[1]
            print('>>>>>>>>>>>>><')
            if horario_general.fecha_cambio:
                print('<<<<<<<<<<<<<<<<<<<')
                today = datetime.datetime.now()
                dateMonthEnd = "%s-%s-%s" % (today.year, 12, calendar.monthrange(today.year, today.month)[1])
                # dateMonthEnd = "%s-%s-%s" % (today.year, 12, calendar.monthrange(today.year - 1, today.month - 1)[1])
                # if vals.has_key('fecha_cambio'):
                # d1 = date(int(self.fecha_cambio[0:4]), int(self.fecha_cambio[5:7]), int(self.fecha_cambio[-2:]))
                d1 = date(int(horario_general.fecha_cambio[0:4]), int(horario_general.fecha_cambio[5:7]),
                          int(horario_general.fecha_cambio[-2:]))
                d2 = date(int(dateMonthEnd[0:4]), int(dateMonthEnd[5:7]), int(dateMonthEnd[-2:]))
                diff = d2 - d1
                if horario_general.secuencia:
                    print('<<<<<<<<sssssssssssssss<<<<<<<<<<<')
                    dt = int(horario_general.secuencia)
                    dd = 0
                    if horario_general.horario and unidad and ruta_id:
                        print('<<<<<<<<hhhhhhhhhhhhhhhhhhhhh<<<<<<<<<<<')
                        if int(horario_general.secuencia) - int(horario_general.horario.dias_trabajo) > 0:
                            dd = (int(horario_general.secuencia) - int(horario_general.horario.dias_trabajo)) - 1

                        for j in range(0, (int(str(diff).split(' ', 1)[0]) + 1), 1):
                            diasDelete = timedelta(days=j)
                            fechaDelete = d1 + diasDelete
                            self._cr.execute(
                                """ DELETE FROM modulo_valorizaciones_calendario WHERE unidad=%s AND ruta_id=%s AND fecha_cambio=%s""",
                                (unidad, ruta_id, fechaDelete))

                        for i in range(0, (int(str(diff).split(' ', 1)[0]) + 1), 1):
                            dias = timedelta(days=i)
                            fecha = d1 + dias
                            if horario_general.horario.dias_descanso == 0:
                                valores = \
                                    {'unidad': unidad
                                        , 'ruta_id': ruta_id
                                        , 'fecha_cambio': fecha
                                        , 'indicador': 'T'
                                        , 'id_calendario': horario_general.parent_horario_id.id
                                     }
                            else:
                                if dt <= horario_general.horario.dias_trabajo:
                                    valores = \
                                        {'unidad': unidad
                                            , 'ruta_id': ruta_id
                                            , 'fecha_cambio': fecha
                                            , 'indicador': 'T'
                                            , 'id_calendario': horario_general.parent_horario_id.id
                                         }
                                    dt = dt + 1
                                else:
                                    if horario_general.horario.dias_descanso > 0:
                                        dt = dt + 1
                                        dd = dd + 1
                                        valores = \
                                            {'unidad': unidad
                                                , 'ruta_id': ruta_id
                                                , 'fecha_cambio': fecha
                                                , 'indicador': 'D'
                                                , 'id_calendario': horario_general.parent_horario_id.id
                                             }
                                        if dd == horario_general.horario.dias_descanso:
                                            dt = 1
                                            dd = 0
                                    else:
                                        dt = 1

                            self.env['modulo_valorizaciones.calendario'].create(valores)
            else:
                self._cr.execute(
                    """ DELETE FROM modulo_valorizaciones_calendario WHERE unidad=%s AND ruta_id=%s""",
                    (unidad, ruta_id))
        return True

        # def agregarCalendario(self):


class modulo_valorizaciones_kilometraje_general(models.Model):
    def _get_unidad(self):
        return str_kilometraje_unidad

    def _get_ruta(self):
        return str_kilometraje_ruta

    _name = 'modulo_valorizaciones.kilometraje_general'
    name = fields.Char('Nombre')
    kilometraje = fields.Char('Valor')
    unidad = fields.Many2one('fleet.vehicle', 'Unidad', default=_get_unidad)
    ruta_id = fields.Many2one('modulo_valorizaciones.ruta', 'Ruta', default=_get_ruta)
    default = fields.Boolean('Por defecto')
    letra = fields.Char('Letra Fórmula')
    n_vueltas = fields.Char('N° de Vueltas', default='1')
    parent_kilometraje_id = fields.Many2one('modulo_valorizaciones.pantalla_general', 'Parent',
                                            help='Parent cost to this current cost', ondelete="cascade")

    # parent_kilometraje_id = fields.Many2one('modulo_valorizaciones.kilometraje_general', 'Parent',
    #                                     help='Parent cost to this current cost')
    # kilometraje_general_ids = fields.One2many('modulo_valorizaciones.kilometraje_general',
    #                                                'parent_kilometraje_id', 'Included Services')

    @api.onchange('default')
    def check_change_default(self):
        global int_default
        int_default = self.letra

    @api.onchange('kilometraje_general_ids')
    def check_change_kilometraje_general_ids(self):
        print('aaaaa')


class modulo_valorizaciones_horario(models.Model):
    _name = 'modulo_valorizaciones.horario'
    name = fields.Char('Nombre del horario', required=True)
    dias_trabajo = fields.Integer('Cuantos días trabaja', required=True)
    dias_descanso = fields.Integer('Cuantos días descansa', required=True)
    dias_total = fields.Integer('Total días', required=True)

    @api.onchange('name')
    def check_change_name(self):
        if self.name:
            self.name = self.name.replace(' ', '')
            self.name = self.name.replace('*', 'x')
            self.name = self.name.replace('X', 'x')
            self.name = self.name.replace('por', 'x')
            self.name = self.name.replace('POR', 'x')
            self.name = self.name.replace('Por', 'x')
            if len(self.name.split('x', 1)) > 1:
                if self.name.split('x', 1)[0].isdigit():
                    self.dias_trabajo = self.name.split('x', 1)[0]
                if self.name.split('x', 1)[1].isdigit():
                    self.dias_descanso = self.name.split('x', 1)[1]
            else:
                if self.name.split('x', 1)[0].isdigit():
                    self.dias_trabajo = self.name.split('x', 1)[0]

    @api.onchange('dias_trabajo')
    def check_change_dias_trabajo(self):
        self.dias_total = self.dias_trabajo + self.dias_descanso

    @api.onchange('dias_descanso')
    def check_change_dias_descanso(self):
        self.dias_total = self.dias_trabajo + self.dias_descanso


class modulo_valorizaciones_calendario(models.Model):
    _name = 'modulo_valorizaciones.calendario'
    unidad = fields.Many2one('fleet.vehicle', 'Unidad')
    ruta_id = fields.Many2one('modulo_valorizaciones.ruta', 'Ruta')
    fecha_cambio = fields.Date('Fecha Cambio')
    indicador = fields.Char('Trabajo Descanso')
    id_calendario = fields.Many2one('modulo_valorizaciones.pantalla_general', 'Horario General', ondelete="cascade")


class modulo_valorizaciones_proveedor(models.Model):
    @api.multi
    def _compute_iframe(self):
        url_path_browser = http.request.env['ir.config_parameter'].get_param('web.base.url')
        h = url_path_browser.split(':')
        if self.id:
            self.iframe = '<iframe marginheight="0" id="frameValorizaciones" marginwidth="0" frameborder = "0" src="http:'+h[1]+':81/valorizaciones/home/index/p/' + str(
                self.id) + '" width="100%" height="1000"/>'
        else:
            self.iframe = '<iframe marginheight="0" id="frameValorizaciones" marginwidth="0" frameborder = "0" src="http:'+h[1]+':81/valorizaciones/home/index/p/0" width="100%" height="1000"/>'
        self.iframe_create = '0'

    @api.multi
    def _compute_creado(self):
        self.creado = True

    def _default_iframe_create(self):
        url_path_browser = http.request.env['ir.config_parameter'].get_param('web.base.url')
        h = url_path_browser.split(':')
        abc = '<iframe marginheight="0" id="frameValorizaciones" marginwidth="0" frameborder = "0" src="http:'+h[1]+':81/valorizaciones/home/index/p/0" width="100%" height="1000"/>'
        return abc

    _name = 'modulo_valorizaciones.proveedor'
    proveedor = fields.Many2one('res.partner', 'Proveedor')
    fecha_inicio = fields.Date('Fecha Inicio')
    fecha_fin = fields.Date('Fecha Fin')
    tipo_moneda = fields.Many2one('res.currency', 'Tipo Moneda')
    monto_sin_igv = fields.Float('Total sin IGV')
    monto_con_igv = fields.Float('Total con IGV')
    cliente_id = fields.Float('Cliente')
    n_factura = fields.Many2one('account.invoice', 'N° Factura')
    nota = fields.Text('Nota')
    estado = fields.Selection(
        [('No creado', 'No creado'), ('Pagado', 'Pagado'), ('Facturado', 'Facturado'), ('No Emitido', 'No Emitido'),
         ('Cancelado', 'Cancelado'),
         ('Borrador', 'Borrador')], 'Estado', default='No creado')
    _rec_name = 'proveedor'
    creado = fields.Boolean('creado', default=False, compute='_compute_creado')
    iframe = fields.Html('iframe', compute='_compute_iframe',
                         sanitize=False, strip_style=False)
    iframe_create = fields.Html('iframe Create', default=_default_iframe_create, sanitize=False, strip_style=False, readonly=True)

    ver_nota_pdf = fields.Boolean('Ver Nota')

    fechaFacturacion = fields.Date('Fecha Facturación')
    date_month = fields.Char(string='Date Month', compute='_get_date_month', store=True, readonly=True)

    @api.one
    @api.depends('fechaFacturacion')
    def _get_date_month(self):
        self.date_month = datetime.datetime.strptime(self.fechaFacturacion, '%Y-%m-%d').strftime('%m')

    @api.model
    def default_get(self, fields):
        if self._context is None:
            self._context = {}

        res = super(modulo_valorizaciones_proveedor, self).default_get(fields)
        ahora = datetime.datetime.now()
        res.update({'anio_actual': ahora.year, 'mes_actual': ahora.month})
        return res
    # @api.multi
    # def read(self, fields=None, load='_classic_read'):
    #    id = 0
    #    for record in self:
    #        id = record.id
    #    print id
    #    res = super(modulo_valorizaciones_proveedor, self).read(fields=fields, load=load)
    #    return res


class modulo_valorizaciones_feriados(models.Model):
    _name = 'modulo_valorizaciones.feriados'
    name = fields.Char('Nombre')
    fecha = fields.Date('Fecha')
    country_id = fields.Many2one('res.country', 'Pais', required=True, default=175)
    state_id = fields.Many2one('res.country.state', 'Departamento')
    province_id = fields.Many2one('res.country.state', 'Provincia')
    district_id = fields.Many2one('res.country.state', 'Distrito')
    descripcion = fields.Text('Descripción')

    @api.multi
    def onchange_state(self, state_id):
        if state_id:
            state = self.env['res.country.state'].browse(state_id)
            return {'value': {'country_id': state.country_id.id}}
        return {}

    @api.multi
    def onchange_district(self, district_id):
        if district_id:
            state = self.env['res.country.state'].browse(district_id)
            return {'value': {'zip': state.code}}
        return {}

    def _display_address(self, cr, uid, address, without_company=False, context=None):

        '''
        The purpose of this function is to build and return an address formatted accordingly to the
        standards of the country where it belongs.

        :param address: browse record of the res.partner to format
        :returns: the address formatted in a display that fit its country habits (or the default ones
            if not country is specified)
        :rtype: string
        '''

        # get the information that will be injected into the display format
        # get the address format
        address_format = address.country_id.address_format or \
                         "%(street)s\n%(street2)s\n%(state_name)s-%(province_name)s-%(district_code)s %(zip)s\n%(country_name)s"
        args = {
            'district_code': address.district_id.code or '',
            'district_name': address.district_id.name or '',
            'province_code': address.province_id.code or '',
            'province_name': address.province_id.name or '',
            'state_code': address.state_id.code or '',
            'state_name': address.state_id.name or '',
            'country_code': address.country_id.code or '',
            'country_name': address.country_id.name or '',
            'company_name': address.parent_name or '',
        }
        for field in self._address_fields(cr, uid, context=context):
            args[field] = getattr(address, field) or ''
        if without_company:
            args['company_name'] = ''
        elif address.parent_id:
            address_format = '%(company_name)s\n' + address_format
        return address_format % args


class val_fleet_service_type(models.Model):
    _inherit = 'fleet.service.type'
    _description = "Informations du Candidats"

    category = fields.Selection(
        [('contract', 'Contract'), ('service', 'Service'), ('both', 'Both'), ('documento', 'Documento'), ('compra', 'Compra')], 'Category',
        required=True, help='Choose wheter the service refer to contracts, vehicle services or both')
    # def __init__(self, pool, cr):
    #     """Add a new state value"""
    #     super(val_fleet_service_type, self).STATE_SELECTION.append(('documento', 'Documento'))
    #     return super(val_fleet_service_type, self).__init__(pool, cr)


class modulo_valorizaciones_pdf_clientes(models.Model):
    _name = 'modulo.valorizaciones.pdf.clientes'
    # _rec_name = 'name'
    # _description = 'New Description'

    cliente = fields.Many2one('res.partner')
    fecha_inicio = fields.Date()
    fecha_fin = fields.Date()
    fecha_facturacion = fields.Date()
    contrato = fields.Many2one('fleet.vehicle.log.contract')
    tipo_moneda = fields.Many2one('res.currency', 'Tipo Moneda')
    url_pdf = fields.Char()
    detalle_contrato = fields.Many2one('modulo_valorizaciones.vehiculo_contrato_detalle', ondelete='cascade')
    display_name = fields.Char()
    correo = fields.Char()
    monto_total = fields.Float()
    id_factura = fields.Many2one('account.invoice', 'N Factura')

class modulo_valorizaciones_pdf_proveedores(models.Model):
    _name = 'modulo.valorizaciones.pdf.proveedores'
    # _rec_name = 'name'
    # _description = 'New Description'

    proveedor = fields.Char()
    fecha_inicio = fields.Date()
    fecha_fin = fields.Date()
    fecha_facturacion = fields.Date()
    tipo_moneda = fields.Char()
    url_pdf = fields.Char()
    id_valorizacion_proveedor = fields.Char()
    display_name = fields.Char()
    correo = fields.Char()
    monto_total = fields.Float()


class modulo_valorizaciones_cambio_usuario(models.Model):
    _name = 'modulo.valorizaciones.cambio_usuario'
    # _rec_name = 'name'
    # _description = 'New Description'

    cliente = fields.Many2one('res.partner')
    contrato_id = fields.Many2one('fleet.vehicle.log.contract')
    contrato_detalle_id = fields.Many2one('modulo_valorizaciones.vehiculo_contrato_detalle', ondelete='cascade')
    ruta_id = fields.Many2one('modulo_valorizaciones.ruta', 'Ruta')
    unidad_id = fields.Many2one('fleet.vehicle', 'Vehiculo')
    fechaFacturacion = fields.Date('Fecha Facturación')
    fechaInicio = fields.Date('Fecha Inicio Contrato')
    fechaFin = fields.Date('Fecha Expiración Contrato')
    tot_dias_fijo = fields.Float('Total Días', default=0)
    tot_dias_variable = fields.Float('Total Días', default=0)
    tot_dias_adicional = fields.Float('Total Días', default=0)
    tarifa_costo_fijo = fields.Float('Tarifa Costo', default=0)
    tarifa_costo_variable = fields.Float('Tarifa Costo', default=0)
    tarifa_costo_adicional = fields.Float('Tarifa Costo', default=0)
    importe_fijo = fields.Float('Importe', default=0)
    importe_variable = fields.Float('Importe', default=0)
    importe_adicional = fields.Float('Importe', default=0)
    id_tareo_mensual = fields.Integer('tareo_mensual')


class hr_employee(models.Model):
    # _name = 'new_module.new_module'
    _inherit = 'hr.employee'

    work_email = fields.Char(required=True)
    employee_group_ids = fields.Many2many('enviar.mails.documentos', 'hr_alerta_documentos_vehiculos_rel',
                                          'employee_ids', 'employee_group_ids',
                                          'Enviar alertas a')


class enviar_mails_documentos(models.Model):
    _name = 'enviar.mails.documentos'
    _rec_name = 'name'
    # _description = 'New Description'

    name = fields.Char('Nombre', default='Empleados a notificar')
    employee_ids = fields.Many2many('hr.employee', 'hr_alerta_documentos_vehiculos_rel', 'employee_group_ids',
                                    'employee_ids', 'Enviar alertas a', required=True)


class Partner(models.Model):
    _inherit = 'res.partner'

    contacto_pdf = fields.Boolean('Contacto para PDF')


class VehiculosContractSummary(models.Model):

    _name = 'vehiculo.contrato.summary'
    # _description = 'Room reservation summary'

    date_from = fields.Date('Fecha Inicio')
    date_to = fields.Date('Fecha Fin')
    contrato = fields.Many2one('fleet.vehicle.log.contract', required=True)

    fijo = fields.Boolean(string="Fijo", )
    summary_header = fields.Text('Cabecera de Fechas')
    room_summary = fields.Text('Vehiculos del Contrato')

    variable = fields.Boolean(string="Variable", )
    summary_header_var = fields.Text('Cabecera de Fechas')
    room_summary_var = fields.Text('Vehiculos del Contrato')

    adicional = fields.Boolean(string="Adicional", )
    summary_header_adi = fields.Text('Cabecera de Fechas')
    room_summary_adi = fields.Text('Vehiculos del Contrato')

    @api.model
    def default_get(self, fields):
        """
        To get default values for the object.
        @param self: The object pointer.
        @param fields: List of fields for which we want default values
        @return: A dictionary which of fields with values.
        """
        if self._context is None:
            self._context = {}
        print('---------')
        print(self._context.get('contrato'))
        print(self._context.get('fecha'))
        print('---------')
        res = super(VehiculosContractSummary, self).default_get(fields)
        contrato = False

        if 'contrato' in self._context:
            contrato = self._context.get('contrato')

        if 'fecha' in self._context:
            from_dt = datetime.datetime.strptime(str(self._context.get('fecha')), DEFAULT_SERVER_DATE_FORMAT)
            dt_from = date(from_dt.year, from_dt.month, 1)
            to_dt = dt_from + relativedelta(months=1)
            to_dt = to_dt - relativedelta(days=1)
            dt_to = date(to_dt.year, to_dt.month, to_dt.day)
            start_date = dt_from.strftime(DEFAULT_SERVER_DATE_FORMAT)
            end_date = dt_to.strftime(DEFAULT_SERVER_DATE_FORMAT)
        else:
            # Added default datetime as today and date to as today + 30.
            from_dt = datetime.datetime.today()
            dt_from = date(from_dt.year, from_dt.month, 1)
            to_dt = dt_from + relativedelta(months=1)
            to_dt = to_dt - relativedelta(days=1)
            dt_to = date(to_dt.year, to_dt.month, to_dt.day)
            start_date = dt_from.strftime(DEFAULT_SERVER_DATE_FORMAT)
            end_date = dt_to.strftime(DEFAULT_SERVER_DATE_FORMAT)

        res.update({'date_from': start_date, 'date_to': end_date, 'contrato': contrato})
        return res

    @api.onchange('date_from', 'date_to', 'contrato')
    def get_room_summary(self):
        if self.contrato.costo_fijo:
            self.fijo = True
        else:
            self.fijo = False

        if self.contrato.costo_variable:
            self.variable = True
        else:
            self.variable = False

        if self.contrato.costo_adicional:
            self.adicional = True
        else:
            self.adicional = False

        '''
        @param self: object pointer
        COSTOS FIJOS
         '''
        res = {}
        all_detail = []
        room_obj = self.env['modulo_valorizaciones.vehiculo_contrato_detalle']
        # reservation_line_obj = self.env['hotel.room.reservation.line']
        # folio_room_line_obj = self.env['folio.room.line']
        date_range_list = []
        main_header = []
        if self.contrato.costo_varios_clientes:
            summary_header_list = [u'Clientes', u'Vehículos']
        else:
            summary_header_list = [u'Vehículos']
        # raise Warning(summary_header_list)
        if self.date_from and self.date_to:
            if self.date_from > self.date_to:
                raise except_orm(_('User Error!'),
                                 _('Please Check Time period Date \
                                 From can\'t be greater than Date To !'))
            d_frm_obj = (datetime.datetime.strptime
                         (self.date_from, DEFAULT_SERVER_DATE_FORMAT))

            d_to_obj = (datetime.datetime.strptime
                        (self.date_to, DEFAULT_SERVER_DATE_FORMAT))

            temp_date = d_frm_obj

            while temp_date <= d_to_obj:
                val = ''
                val = (str(temp_date.strftime("%a")) + ' ' +
                       str(temp_date.strftime("%b")) + ' ' +
                       str(temp_date.strftime("%d")))
                summary_header_list.append(val)
                date_range_list.append(temp_date.strftime
                                       (DEFAULT_SERVER_DATE_FORMAT))
                temp_date = temp_date + datetime.timedelta(days=1)
            all_detail.append(summary_header_list)
            room_ids = room_obj.search([['parent_id', '=', self.contrato.id]])
            # raise Warning(room_ids)
            all_room_detail = []
            all_room_detail_var = []
            all_room_detail_adi = []
            for room in room_ids:
                room_detail = {}
                room_detail_var = {}
                room_detail_adi = {}
                room_list_stats = []
                room_list_stats_var = []
                room_list_stats_adi = []
                if self.contrato.costo_varios_clientes:
                    room_detail.update({'name': room.unidad_id.name or '', 'cliente': room.cliente.name or ''})
                    room_detail_var.update({'name': room.unidad_id.name or '', 'cliente': room.cliente.name or ''})
                    room_detail_adi.update({'name': room.unidad_id.name or '', 'cliente': room.cliente.name or ''})
                else:
                    room_detail.update({'name': room.unidad_id.name or ''})
                    room_detail_var.update({'name': room.unidad_id.name or ''})
                    room_detail_adi.update({'name': room.unidad_id.name or ''})

                for chk_date in date_range_list:
                    """COSTOS FIJOS"""
                    valor_tareo = self.env['modulo.valorizaciones.tareo'].search(
                        [['tipo', '=', 'f'], ['idunidad', '=', room.unidad_id.id],
                         ['idunidad', '=', room.unidad_id.id], ['idruta', '=', room.ruta_id.id],
                         ['fecha', '=', chk_date], ['iddetalle_contrato', '=', room.id]], limit=1)

                    if valor_tareo:
                        room_list_stats.append({'valor': int(valor_tareo.monto) if valor_tareo else 1,
                                                'state': 'ConValor',
                                                'date': chk_date,
                                                'room_id': room.id})
                    else:
                        room_list_stats.append({'valor': 1,
                                                'state': 'Sinvalor',
                                                'date': chk_date,
                                                'room_id': room.id})
                    """COSTOS VARIABLES"""
                    valor_tareo_var = self.env['modulo.valorizaciones.tareo'].search(
                        [['tipo', '=', 'v'], ['idunidad', '=', room.unidad_id.id],
                         ['idunidad', '=', room.unidad_id.id], ['idruta', '=', room.ruta_id.id],
                         ['fecha', '=', chk_date], ['iddetalle_contrato', '=', room.id]], limit=1)

                    if valor_tareo_var:
                        room_list_stats_var.append({'valor': int(valor_tareo_var.monto) if valor_tareo_var else 0,
                                                'state': 'ConValor',
                                                'date': chk_date,
                                                'room_id': room.id})
                    else:
                        room_list_stats_var.append({'valor': 0,
                                                'state': 'Sinvalor',
                                                'date': chk_date,
                                                'room_id': room.id})
                    """COSTOS ADICIONALES"""
                    valor_tareo_adi = self.env['modulo.valorizaciones.tareo'].search(
                        [['tipo', '=', 'a'], ['idunidad', '=', room.unidad_id.id],
                         ['idunidad', '=', room.unidad_id.id], ['idruta', '=', room.ruta_id.id],
                         ['fecha', '=', chk_date], ['iddetalle_contrato', '=', room.id]], limit=1)

                    if valor_tareo_adi:
                        room_list_stats_adi.append({'valor': int(valor_tareo_adi.monto) if valor_tareo_adi else 0,
                                                'state': 'ConValor',
                                                'date': chk_date,
                                                'room_id': room.id})
                    else:
                        room_list_stats_adi.append({'valor': 0,
                                                'state': 'Sinvalor',
                                                'date': chk_date,
                                                'room_id': room.id})

                room_detail.update({'value': room_list_stats})
                room_detail_var.update({'value': room_list_stats_var})
                room_detail_adi.update({'value': room_list_stats_adi})

                all_room_detail.append(room_detail)
                all_room_detail_var.append(room_detail_var)
                all_room_detail_adi.append(room_detail_adi)

            main_header.append({'header': summary_header_list})
            """COSTOS FIJOS"""
            self.summary_header = str(main_header)
            self.room_summary = str(all_room_detail)
            """COSTOS variables"""
            self.summary_header_var = str(main_header)
            self.room_summary_var = str(all_room_detail_var)
            """COSTOS adicionales"""
            self.summary_header_adi = str(main_header)
            self.room_summary_adi = str(all_room_detail_adi)
        return res


class modulo_valorizacion_descripciones(models.Model):
    _name = 'modulo.valorizacion.descripciones'
    # _rec_name = 'name'
    # _description = 'New Description'
    unificado_varios_clientes = fields.Boolean(string="Varios")
    fijo = fields.Boolean(string="Fijo", )
    variable = fields.Boolean(string="Variable", )
    adicional = fields.Boolean(string="Adicional", )

    cliente = fields.Many2one('res.partner', 'Cliente')
    vehiculo_id = fields.Many2one('fleet.vehicle', 'Vehículo')
    ruta_id = fields.Many2one('modulo_valorizaciones.ruta', 'Ruta')
    valor = fields.Integer(string="valor")
    nota_detalle_contrato = fields.Char('Descripción')
    descripcion_detalle_tareo = fields.Char('Descripción')
    # descripcion_detalle_tareo_variable = fields.Char('Descripción')
    # descripcion_detalle_tareo_adicional = fields.Char('Descripción')
    contrato_id = fields.Many2one(comodel_name="fleet.vehicle.log.contract", string="Vehiculos")
    contrato_detalle_id = fields.Many2one('modulo_valorizaciones.vehiculo_contrato_detalle', ondelete='cascade')
    fecha_tareo = fields.Date(string="Fecha Tareo")


class modulo_valorizaciones_facturas_contrato(models.Model):
    _name = 'modulo.valorizaciones.facturas.contrato'
    # _rec_name = 'name'
    # _description = 'New Description'

    id_contrato = fields.Integer()
    id_factura = fields.Integer()
    fecha_facturacion = fields.Date()
    cliente = fields.Integer()
    detalle_contrato = fields.Integer()