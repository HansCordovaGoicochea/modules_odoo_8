# -*- coding: utf-8 -*-

import calendar
# from datetime import date,timedelta
from datetime import date, timedelta
import time
from openerp import models, fields, api, _

import dateutil.parser
from openerp.exceptions import except_orm, Warning, RedirectWarning
import datetime
import pytz
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from openerp.exceptions import except_orm, ValidationError
from dateutil.relativedelta import relativedelta


class m_valorizaciones_tareo_wizard(models.TransientModel):
    _name = 'm.valorizacion.tareo.wizard'

    contrato = fields.Many2one('fleet.vehicle.log.contract', required=True)
    fecha_tareo = fields.Date(string="Fecha Tareo", required=True, default=datetime.datetime.now())
    contrato_ids = fields.One2many(comodel_name="m.valorizacion.tareo.wizard.det", inverse_name="contrato_id",
                                   string="Vehiculos", required=True, )
    contrato_ids_var = fields.One2many(comodel_name="m.valorizacion.tareo.wizard.det.var", inverse_name="contrato_id",
                                       string="Vehiculos variable", required=True, )

    contrato_ids_adi = fields.One2many(comodel_name="m.valorizacion.tareo.wizard.det.adi", inverse_name="contrato_id",
                                       string="Vehiculos adicional", required=True, )

    unificado_varios_clientes = fields.Boolean(string="Varios", )

    fijo = fields.Boolean(string="Fijo", )
    summary_header = fields.Text('Cabecera de Fechas')
    room_summary = fields.Text('Vehiculos del Contrato')

    variable = fields.Boolean(string="Variable", )
    summary_header_var = fields.Text('Cabecera de Fechas')
    room_summary_var = fields.Text('Vehiculos del Contrato')

    adicional = fields.Boolean(string="Adicional", )
    summary_header_adi = fields.Text('Cabecera de Fechas')
    room_summary_adi = fields.Text('Vehiculos del Contrato')

    #traer datos para el cuadro de colores del fondo
    @api.onchange('fecha_tareo', 'contrato')
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

        from_dt = datetime.datetime.strptime(str(self.fecha_tareo), DEFAULT_SERVER_DATE_FORMAT)
        dt_from = date(from_dt.year, from_dt.month, 1)
        to_dt = dt_from + relativedelta(months=1)
        to_dt = to_dt - relativedelta(days=1)
        dt_to = date(to_dt.year, to_dt.month, to_dt.day)
        self.date_from = dt_from.strftime(DEFAULT_SERVER_DATE_FORMAT)
        self.date_to = dt_to.strftime(DEFAULT_SERVER_DATE_FORMAT)

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
                    room_detail.update({'cliente': room.cliente.name or '', 'name': room.unidad_id.name or ''})
                    room_detail_var.update({'cliente': room.cliente.name or '', 'name': room.unidad_id.name or ''})
                    room_detail_adi.update({'cliente': room.cliente.name or '', 'name': room.unidad_id.name or ''})
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

    # traer los vehiculos al detalle al cambiar el contrato
    @api.onchange('contrato', 'fecha_tareo')
    def onchange_method(self):

        self.contrato_ids = [(5, [x.id for x in self.contrato_ids])]
        self.contrato_ids_var = [(5, [x.id for x in self.contrato_ids_var])]
        self.contrato_ids_adi = [(5, [x.id for x in self.contrato_ids_adi])]

        print('---------------y-------------')
        print(self.id)
        print(self.contrato)
        print(self.fecha_tareo)
        print(self.contrato_ids)
        print(self.contrato_ids_var)
        print(self.contrato_ids_adi)
        print('-------------yy---------------')

        obj_valorizacion_descripciones = self.env['modulo.valorizacion.descripciones']

        esquemadetalle_ids = []
        esquemadetalle_ids_var = []
        esquemadetalle_ids_adi = []
        res = {}
        if self.contrato.costo_varios_clientes:
            arrayDetalle = self.env['modulo_valorizaciones.vehiculo_contrato_detalle'].search(
                [['parent_id', '=', self.contrato.id], ['costo_varios_clientes', '=', True]])
            # raise Warning(arrayDetalle)
            self.unificado_varios_clientes = True
            if self.contrato.costo_fijo:
                self.fijo = True
                for detalle in arrayDetalle:
                    id_valorizacion_descripcion = obj_valorizacion_descripciones.search(
                        [
                            ['contrato_id', '=', self.contrato.id],
                            ['unificado_varios_clientes', '=', True],
                            ['fijo', '=', True],
                            ['vehiculo_id', '=', detalle.unidad_id.id],
                            ['cliente', '=', detalle.cliente.id],
                            ['fecha_tareo', '=', self.fecha_tareo],
                            ['ruta_id', '=', detalle.ruta_id.id],
                            ['contrato_detalle_id', '=', detalle.id],
                        ])

                    valor_tareo = self.env['modulo.valorizaciones.tareo'].search(
                        [['tipo', '=', 'f'], ['idunidad', '=', detalle.unidad_id.id],
                         ['idunidad', '=', detalle.unidad_id.id], ['idruta', '=', detalle.ruta_id.id],
                         ['fecha', '=', self.fecha_tareo], ['iddetalle_contrato', '=', detalle.id]], limit=1)

                    esquemadetalle_ids.append((0, 0, {
                        'cliente': detalle.cliente.id,
                        'vehiculo_id': detalle.unidad_id.id,
                        'ruta_id': detalle.ruta_id.id or '',
                        'valor': int(valor_tareo.monto) if valor_tareo else 1,
                        'descripcion': detalle.descripcion_rutas or '',
                        'descripcion_detalle_tareo': id_valorizacion_descripcion.descripcion_detalle_tareo or ''
                    }))
                self.contrato_ids = esquemadetalle_ids
            else:
                self.fijo = False
                self.contrato_ids = esquemadetalle_ids

            if self.contrato.costo_variable:
                self.variable = True
                for detalle in arrayDetalle:
                    # print('----------------')
                    # print(self.contrato.id)
                    # print(True)
                    # print(True)
                    # print(detalle.unidad_id.id)
                    # print(self.contrato.cliente.id)
                    # print(self.fecha_tareo)
                    # print(detalle.ruta_id.id)
                    # print(detalle.id)
                    # print('----------------')
                    id_valorizacion_descripcion = obj_valorizacion_descripciones.search(
                        [
                            ['contrato_id', '=', self.contrato.id],
                            ['unificado_varios_clientes', '=', True],
                            ['variable', '=', True],
                            ['vehiculo_id', '=', detalle.unidad_id.id],
                            ['cliente', '=', detalle.cliente.id],
                            ['fecha_tareo', '=', self.fecha_tareo],
                            ['ruta_id', '=', detalle.ruta_id.id],
                            ['contrato_detalle_id', '=', detalle.id],
                        ])

                    valor_tareo = self.env['modulo.valorizaciones.tareo'].search(
                        [['tipo', '=', 'v'], ['idunidad', '=', detalle.unidad_id.id],
                         ['idunidad', '=', detalle.unidad_id.id], ['idruta', '=', detalle.ruta_id.id],
                         ['fecha', '=', self.fecha_tareo], ['iddetalle_contrato', '=', detalle.id]], limit=1)

                    esquemadetalle_ids_var.append((0, 0, {
                        'cliente': detalle.cliente.id,
                        'vehiculo_id': detalle.unidad_id.id,
                        'ruta_id': detalle.ruta_id.id or '',
                        'valor': int(valor_tareo.monto) if valor_tareo else 0,
                        'descripcion': detalle.descripcion_rutas or '',
                        'descripcion_detalle_tareo': id_valorizacion_descripcion.descripcion_detalle_tareo or ''
                    }))
                self.contrato_ids_var = esquemadetalle_ids_var
            else:
                self.variable = False
                self.contrato_ids_var = esquemadetalle_ids_var

            if self.contrato.costo_adicional:
                self.adicional = True
                for detalle in arrayDetalle:
                    id_valorizacion_descripcion = obj_valorizacion_descripciones.search(
                        [
                            ['contrato_id', '=', self.contrato.id],
                            ['unificado_varios_clientes', '=', True],
                            ['adicional', '=', True],
                            ['vehiculo_id', '=', detalle.unidad_id.id],
                            ['cliente', '=', detalle.cliente.id],
                            ['fecha_tareo', '=', self.fecha_tareo],
                            ['ruta_id', '=', detalle.ruta_id.id],
                            ['contrato_detalle_id', '=', detalle.id],
                        ])

                    valor_tareo = self.env['modulo.valorizaciones.tareo'].search(
                        [['tipo', '=', 'a'], ['idunidad', '=', detalle.unidad_id.id],
                         ['idunidad', '=', detalle.unidad_id.id], ['idruta', '=', detalle.ruta_id.id],
                         ['fecha', '=', self.fecha_tareo], ['iddetalle_contrato', '=', detalle.id]], limit=1)
                    esquemadetalle_ids_adi.append((0, 0, {
                        'cliente': detalle.cliente.id,
                        'vehiculo_id': detalle.unidad_id.id,
                        'ruta_id': detalle.ruta_id.id or '',
                        'valor': int(valor_tareo.monto) if valor_tareo else 0,
                        'descripcion': detalle.descripcion_rutas or '',
                        'descripcion_detalle_tareo': id_valorizacion_descripcion.descripcion_detalle_tareo or ''
                    }))
                self.contrato_ids_adi = esquemadetalle_ids_adi
            else:
                self.adicional = False
                self.contrato_ids_adi = esquemadetalle_ids_adi
        else:
            arrayDetalle = self.env['modulo_valorizaciones.vehiculo_contrato_detalle'].search(
                [['parent_id', '=', self.contrato.id]])
            self.unificado_varios_clientes = False
            if self.contrato.costo_fijo:
                self.fijo = True
                for detalle in arrayDetalle:
                    id_valorizacion_descripcion = obj_valorizacion_descripciones.search(
                        [
                            ['contrato_id', '=', self.contrato.id],
                            ['unificado_varios_clientes', '=', False],
                            ['fijo', '=', True],
                            ['vehiculo_id', '=', detalle.unidad_id.id],
                            ['cliente', '=', self.contrato.cliente.id],
                            ['fecha_tareo', '=', self.fecha_tareo],
                            ['ruta_id', '=', detalle.ruta_id.id],
                            ['contrato_detalle_id', '=', detalle.id],
                        ])

                    valor_tareo = self.env['modulo.valorizaciones.tareo'].search(
                        [['tipo', '=', 'f'], ['idunidad', '=', detalle.unidad_id.id],
                         ['idunidad', '=', detalle.unidad_id.id], ['idruta', '=', detalle.ruta_id.id],
                         ['fecha', '=', self.fecha_tareo], ['iddetalle_contrato', '=', detalle.id]], limit=1)

                    esquemadetalle_ids.append((0, 0, {
                        'vehiculo_id': detalle.unidad_id.id,
                        'ruta_id': detalle.ruta_id.id or '',
                        'valor': int(valor_tareo.monto) if valor_tareo else 1,
                        'descripcion': detalle.descripcion_rutas or '',
                        'descripcion_detalle_tareo': id_valorizacion_descripcion.descripcion_detalle_tareo or ''
                    }))
                self.contrato_ids = esquemadetalle_ids
            else:
                self.fijo = False
                self.contrato_ids = esquemadetalle_ids

            if self.contrato.costo_variable:
                self.variable = True
                for detalle in arrayDetalle:
                    id_valorizacion_descripcion = obj_valorizacion_descripciones.search(
                        [
                            ['contrato_id', '=', self.contrato.id],
                            ['unificado_varios_clientes', '=', False],
                            ['variable', '=', True],
                            ['vehiculo_id', '=', detalle.unidad_id.id],
                            ['cliente', '=', self.contrato.cliente.id],
                            ['fecha_tareo', '=', self.fecha_tareo],
                            ['ruta_id', '=', detalle.ruta_id.id],
                            ['contrato_detalle_id', '=', detalle.id],
                        ])

                    valor_tareo = self.env['modulo.valorizaciones.tareo'].search(
                        [['tipo', '=', 'v'], ['idunidad', '=', detalle.unidad_id.id],
                         ['idunidad', '=', detalle.unidad_id.id], ['idruta', '=', detalle.ruta_id.id],
                         ['fecha', '=', self.fecha_tareo], ['iddetalle_contrato', '=', detalle.id]], limit=1)

                    esquemadetalle_ids_var.append((0, 0, {
                        'vehiculo_id': detalle.unidad_id.id,
                        'ruta_id': detalle.ruta_id.id or '',
                        'valor': int(valor_tareo.monto) if valor_tareo else 0,
                        'descripcion': detalle.descripcion_rutas or '',
                        'descripcion_detalle_tareo': id_valorizacion_descripcion.descripcion_detalle_tareo or ''
                    }))
                self.contrato_ids_var = esquemadetalle_ids_var
            else:
                self.variable = False
                self.contrato_ids_var = esquemadetalle_ids_var

            if self.contrato.costo_adicional:
                self.adicional = True
                for detalle in arrayDetalle:
                    id_valorizacion_descripcion = obj_valorizacion_descripciones.search(
                        [
                            ['contrato_id', '=', self.contrato.id],
                            ['unificado_varios_clientes', '=', False],
                            ['adicional', '=', True],
                            ['vehiculo_id', '=', detalle.unidad_id.id],
                            ['cliente', '=', self.contrato.cliente.id],
                            ['fecha_tareo', '=', self.fecha_tareo],
                            ['ruta_id', '=', detalle.ruta_id.id],
                            ['contrato_detalle_id', '=', detalle.id],
                        ])

                    valor_tareo = self.env['modulo.valorizaciones.tareo'].search(
                        [['tipo', '=', 'a'], ['idunidad', '=', detalle.unidad_id.id],
                         ['idunidad', '=', detalle.unidad_id.id], ['idruta', '=', detalle.ruta_id.id],
                         ['fecha', '=', self.fecha_tareo], ['iddetalle_contrato', '=', detalle.id]], limit=1)
                    esquemadetalle_ids_adi.append((0, 0, {
                        'vehiculo_id': detalle.unidad_id.id,
                        'ruta_id': detalle.ruta_id.id or '',
                        'valor': int(valor_tareo.monto) if valor_tareo else 0,
                        'descripcion': detalle.descripcion_rutas or '',
                        'descripcion_detalle_tareo': id_valorizacion_descripcion.descripcion_detalle_tareo or ''
                    }))
                self.contrato_ids_adi = esquemadetalle_ids_adi

            else:
                self.adicional = False
                self.contrato_ids_adi = esquemadetalle_ids_adi

    @api.multi
    def generate_file_data1(self):
        self.ensure_one()
        obj_valorizacion_descripciones = self.env['modulo.valorizacion.descripciones']

        obj_valorizacion_proveedor = self.env['modulo_valorizaciones.proveedor']
        obj_vehiculo_contrato_detalle = self.env['modulo_valorizaciones.vehiculo_contrato_detalle']
        obj_tareo = self.env['modulo.valorizaciones.tareo']
        obj_tareo_mensual = self.env['modulo_valorizaciones.tareo_mensual']
        notas = []
        if self.contrato.costo_varios_clientes:

            # costo fijo
            for line in self.contrato_ids:
                # juntamos todas las notas
                notas.append(line.descripcion)
                id_detalle_contrato_tareo = obj_vehiculo_contrato_detalle.search(
                    [['parent_id', '=', self.contrato.id], ['unidad_id', '=', line.vehiculo_id.id], ['ruta_id', '=', line.ruta_id.id], ['cliente', '=', line.cliente.id], ['costo_varios_clientes', '=', True]])
                if not id_detalle_contrato_tareo:
                    id_proveedor = ''
                    if line.vehiculo_id.alquilado_propio:
                        id_proveedor = line.vehiculo_id.proveedor.id
                    # si no existe el vehiculo en el contrato creamos el detalle
                    res = obj_vehiculo_contrato_detalle.create({
                        'area_id': '',
                        'descripcion_adicional': '',
                        'descripcion_proveedor': '',
                        'descripcion_rutas': '',
                        'horario_id': '',
                        'tot_dias_adicional': '',
                        'importe_adicional': '',
                        'tarifa_costo_adicional': '',
                        'parent_id': self.contrato.id,
                        'descripcion_variable': '',
                        'costo_varios_clientes': True,
                        'descripcion_fijo': '',
                        'km_fijo': '',
                        'descripcion_proveedor_km': '',
                        'unidad_id': line.vehiculo_id.id,
                        'km_proveedor': '',
                        'importe_variable': '',
                        'importe_fijo': '',
                        'tarifa_costo_fijo': '',
                        'name': self.contrato.name,
                        'tot_dias_variable': '',
                        'tot_dias_fijo': '',
                        'importe_proveedor': '',
                        'tarifa_costo_variable': '',
                        'ruta_id': line.ruta_id.id,
                        'cliente': line.cliente.id,
                        'estado_detalle': 'nuevo',
                        'codigo_proveedor': id_proveedor,
                    })
                    # creamos el tareo con un 1 en la fecha correspondiente
                    obj_tareo.create({
                        'tipo': 'f',
                        'idunidad': line.vehiculo_id.id,
                        'monto': line.valor,
                        'fecha': self.fecha_tareo,
                        'iddetalle_contrato': res.id,
                        'cambio': True,
                        'idruta': line.ruta_id.id,
                    })

                    # creamos las descripcion para fijo
                    obj_valorizacion_descripciones.create({
                        'unificado_varios_clientes': True,
                        'fijo': True,
                        'variable': False,
                        'adicional': False,
                        'nota_detalle_contrato': line.descripcion,
                        'contrato_id': self.contrato.id,
                        'vehiculo_id': line.vehiculo_id.id,
                        'cliente': line.cliente.id,
                        'fecha_tareo': self.fecha_tareo,
                        'valor': line.valor,
                        'ruta_id': line.ruta_id.id,
                        'descripcion_detalle_tareo': line.descripcion_detalle_tareo,
                        'contrato_detalle_id': res.id,
                    })
                else:
                    # si existe el detalle solo creamos el tareo
                    id_tareo = obj_tareo.search(
                        [['idunidad', '=', id_detalle_contrato_tareo.unidad_id.id], ['fecha', '=', self.fecha_tareo],
                         ['iddetalle_contrato', '=', id_detalle_contrato_tareo.id],
                         ['idruta', '=', id_detalle_contrato_tareo.ruta_id.id], ['tipo', '=', 'f']])
                    # si existe el tareo actualizamos el tareo con 1 pero si no existe lo creamos
                    if not id_tareo:
                        obj_tareo.create({
                            'tipo': 'f',
                            'idunidad': id_detalle_contrato_tareo.unidad_id.id,
                            'monto': line.valor,
                            'fecha': self.fecha_tareo,
                            'iddetalle_contrato': id_detalle_contrato_tareo.id,
                            'cambio': True,
                            'idruta': id_detalle_contrato_tareo.ruta_id.id or '',
                        })
                    else:
                        id_tareo.write({
                            'tipo': 'f',
                            'idunidad': id_detalle_contrato_tareo.unidad_id.id,
                            'monto': line.valor,
                            'fecha': self.fecha_tareo,
                            'iddetalle_contrato': id_detalle_contrato_tareo.id,
                            'cambio': True,
                            'idruta': id_detalle_contrato_tareo.ruta_id.id or '',
                        })

                    id_valorizacion_descripcion = obj_valorizacion_descripciones.search(
                        [
                            ['contrato_id', '=', self.contrato.id],
                            ['unificado_varios_clientes', '=', True],
                            ['fijo', '=', True],
                            ['vehiculo_id', '=', line.vehiculo_id.id],
                            ['cliente', '=', line.cliente.id],
                            ['fecha_tareo', '=', self.fecha_tareo],
                            ['ruta_id', '=', line.ruta_id.id],
                            ['contrato_detalle_id', '=', id_detalle_contrato_tareo.id],
                        ])

                    if not id_valorizacion_descripcion:
                        # creamos las descripcion para variable
                        obj_valorizacion_descripciones.create({
                            'unificado_varios_clientes': True,
                            'fijo': True,
                            'variable': False,
                            'adicional': False,
                            'nota_detalle_contrato': line.descripcion,
                            'contrato_id': self.contrato.id,
                            'vehiculo_id': line.vehiculo_id.id,
                            'cliente': line.cliente.id,
                            'fecha_tareo': self.fecha_tareo,
                            'valor': line.valor,
                            'ruta_id': line.ruta_id.id,
                            'descripcion_detalle_tareo': line.descripcion_detalle_tareo,
                            'contrato_detalle_id': id_detalle_contrato_tareo.id,
                        })
                    else:
                        # si existe actualizamos las descripcion para variable
                        id_valorizacion_descripcion.write({
                            'unificado_varios_clientes': True,
                            'fijo': True,
                            'variable': False,
                            'adicional': False,
                            'nota_detalle_contrato': line.descripcion,
                            'contrato_id': self.contrato.id,
                            'vehiculo_id': line.vehiculo_id.id,
                            'cliente': line.cliente.id,
                            'fecha_tareo': self.fecha_tareo,
                            'valor': line.valor,
                            'ruta_id': line.ruta_id.id,
                            'descripcion_detalle_tareo': line.descripcion_detalle_tareo,
                            'contrato_detalle_id': id_detalle_contrato_tareo.id,
                        })

            # costo variable
            for line in self.contrato_ids_var:
                # juntamos todas las notas
                notas.append(line.descripcion)
                id_detalle_contrato_tareo = obj_vehiculo_contrato_detalle.search(
                    [['parent_id', '=', self.contrato.id], ['unidad_id', '=', line.vehiculo_id.id], ['ruta_id', '=', line.ruta_id.id], ['cliente', '=', line.cliente.id], ['costo_varios_clientes', '=', True]])
                if not id_detalle_contrato_tareo:
                    id_proveedor = ''
                    if line.vehiculo_id.alquilado_propio:
                        id_proveedor = line.vehiculo_id.proveedor.id
                    # si no existe el vehiculo en el contrato creamos el detalle
                    res = obj_vehiculo_contrato_detalle.create({
                        'area_id': '',
                        'descripcion_adicional': '',
                        'descripcion_proveedor': '',
                        'descripcion_rutas': '',
                        'horario_id': '',
                        'tot_dias_adicional': '',
                        'importe_adicional': '',
                        'tarifa_costo_adicional': '',
                        'parent_id': self.contrato.id,
                        'descripcion_variable': '',
                        'costo_varios_clientes': True,
                        'descripcion_fijo': '',
                        'km_fijo': '',
                        'descripcion_proveedor_km': '',
                        'unidad_id': line.vehiculo_id.id,
                        'km_proveedor': '',
                        'importe_variable': '',
                        'importe_fijo': '',
                        'tarifa_costo_fijo': '',
                        'name': self.contrato.name,
                        'tot_dias_variable': '',
                        'tot_dias_fijo': '',
                        'importe_proveedor': '',
                        'tarifa_costo_variable': '',
                        'ruta_id': line.ruta_id.id,
                        'cliente': line.cliente.id,
                        'estado_detalle': 'nuevo',
                        'codigo_proveedor': id_proveedor,
                    })
                    # creamos el tareo con un 1 en la fecha correspondiente
                    obj_tareo.create({
                        'tipo': 'v',
                        'idunidad': line.vehiculo_id.id,
                        'monto': line.valor,
                        'fecha': self.fecha_tareo,
                        'iddetalle_contrato': res.id,
                        'cambio': True,
                        'idruta': line.ruta_id.id,
                    })

                    # creamos las descripcion para variable
                    obj_valorizacion_descripciones.create({
                        'unificado_varios_clientes': True,
                        'fijo': False,
                        'variable': True,
                        'adicional': False,
                        'nota_detalle_contrato': line.descripcion,
                        'contrato_id': self.contrato.id,
                        'vehiculo_id': line.vehiculo_id.id,
                        'cliente': line.cliente.id,
                        'fecha_tareo': self.fecha_tareo,
                        'valor': line.valor,
                        'ruta_id': line.ruta_id.id,
                        'descripcion_detalle_tareo': line.descripcion_detalle_tareo,
                        'contrato_detalle_id': res.id,
                    })
                else:
                    # si existe el detalle solo creamos el tareo
                    id_tareo = obj_tareo.search(
                        [['idunidad', '=', id_detalle_contrato_tareo.unidad_id.id], ['fecha', '=', self.fecha_tareo],
                         ['iddetalle_contrato', '=', id_detalle_contrato_tareo.id],
                         ['idruta', '=', id_detalle_contrato_tareo.ruta_id.id], ['tipo', '=', 'v']])
                    # si existe el tareo actualizamos el tareo con 1 pero si no existe lo creamos
                    if not id_tareo:
                        obj_tareo.create({
                            'tipo': 'v',
                            'idunidad': id_detalle_contrato_tareo.unidad_id.id,
                            'monto': line.valor,
                            'fecha': self.fecha_tareo,
                            'iddetalle_contrato': id_detalle_contrato_tareo.id,
                            'cambio': True,
                            'idruta': id_detalle_contrato_tareo.ruta_id.id or '',
                        })
                    else:
                        id_tareo.write({
                            'tipo': 'v',
                            'idunidad': id_detalle_contrato_tareo.unidad_id.id,
                            'monto': line.valor,
                            'fecha': self.fecha_tareo,
                            'iddetalle_contrato': id_detalle_contrato_tareo.id,
                            'cambio': True,
                            'idruta': id_detalle_contrato_tareo.ruta_id.id or '',
                        })

                    id_valorizacion_descripcion = obj_valorizacion_descripciones.search(
                        [
                            ['contrato_id', '=', self.contrato.id],
                            ['unificado_varios_clientes', '=', True],
                            ['variable', '=', True],
                            ['vehiculo_id', '=', line.vehiculo_id.id],
                            ['cliente', '=', line.cliente.id],
                            ['fecha_tareo', '=', self.fecha_tareo],
                            ['ruta_id', '=', line.ruta_id.id],
                            ['contrato_detalle_id', '=', id_detalle_contrato_tareo.id],
                        ])

                    if not id_valorizacion_descripcion:
                        # creamos las descripcion para variable
                        obj_valorizacion_descripciones.create({
                            'unificado_varios_clientes': True,
                            'fijo': False,
                            'variable': True,
                            'adicional': False,
                            'nota_detalle_contrato': line.descripcion,
                            'contrato_id': self.contrato.id,
                            'vehiculo_id': line.vehiculo_id.id,
                            'cliente': line.cliente.id,
                            'fecha_tareo': self.fecha_tareo,
                            'valor': line.valor,
                            'ruta_id': line.ruta_id.id,
                            'descripcion_detalle_tareo': line.descripcion_detalle_tareo,
                            'contrato_detalle_id': id_detalle_contrato_tareo.id,
                        })
                    else:
                        # si existe actualizamos las descripcion para variable
                        id_valorizacion_descripcion.write({
                            'unificado_varios_clientes': True,
                            'fijo': False,
                            'variable': True,
                            'adicional': False,
                            'nota_detalle_contrato': line.descripcion,
                            'contrato_id': self.contrato.id,
                            'vehiculo_id': line.vehiculo_id.id,
                            'cliente': line.cliente.id,
                            'fecha_tareo': self.fecha_tareo,
                            'valor': line.valor,
                            'ruta_id': line.ruta_id.id,
                            'descripcion_detalle_tareo': line.descripcion_detalle_tareo,
                            'contrato_detalle_id': id_detalle_contrato_tareo.id,
                        })

            # costo adicional
            for line in self.contrato_ids_adi:
                # juntamos todas las notas
                notas.append(line.descripcion)
                id_detalle_contrato_tareo = obj_vehiculo_contrato_detalle.search(
                    [['parent_id', '=', self.contrato.id], ['unidad_id', '=', line.vehiculo_id.id], ['ruta_id', '=', line.ruta_id.id], ['cliente', '=', line.cliente.id], ['costo_varios_clientes', '=', True]])
                if not id_detalle_contrato_tareo:
                    id_proveedor = ''
                    if line.vehiculo_id.alquilado_propio:
                        id_proveedor = line.vehiculo_id.proveedor.id
                    # si no existe el vehiculo en el contrato creamos el detalle
                    res = obj_vehiculo_contrato_detalle.create({
                        'area_id': '',
                        'descripcion_adicional': '',
                        'descripcion_proveedor': '',
                        'descripcion_rutas': '',
                        'horario_id': '',
                        'tot_dias_adicional': '',
                        'importe_adicional': '',
                        'tarifa_costo_adicional': '',
                        'parent_id': self.contrato.id,
                        'descripcion_variable': '',
                        'costo_varios_clientes': '',
                        'descripcion_fijo': '',
                        'km_fijo': '',
                        'descripcion_proveedor_km': '',
                        'unidad_id': line.vehiculo_id.id,
                        'km_proveedor': '',
                        'importe_variable': '',
                        'importe_fijo': '',
                        'tarifa_costo_fijo': '',
                        'name': self.contrato.name,
                        'tot_dias_variable': '',
                        'tot_dias_fijo': '',
                        'importe_proveedor': '',
                        'tarifa_costo_variable': '',
                        'ruta_id': line.ruta_id.id,
                        'cliente': line.cliente.id,
                        'estado_detalle': 'nuevo',
                        'codigo_proveedor': id_proveedor,
                    })
                    # creamos el tareo con un 1 en la fecha correspondiente
                    obj_tareo.create({
                        'tipo': 'a',
                        'idunidad': line.vehiculo_id.id,
                        'monto': line.valor,
                        'fecha': self.fecha_tareo,
                        'iddetalle_contrato': res.id,
                        'cambio': True,
                        'idruta': line.ruta_id.id,
                    })

                    # creamos las descripcion para variable
                    obj_valorizacion_descripciones.create({
                        'unificado_varios_clientes': True,
                        'fijo': False,
                        'variable': False,
                        'adicional': True,
                        'nota_detalle_contrato': line.descripcion,
                        'contrato_id': self.contrato.id,
                        'vehiculo_id': line.vehiculo_id.id,
                        'cliente': line.cliente.id,
                        'fecha_tareo': self.fecha_tareo,
                        'valor': line.valor,
                        'ruta_id': line.ruta_id.id,
                        'descripcion_detalle_tareo': line.descripcion_detalle_tareo,
                        'contrato_detalle_id': res.id,
                    })
                else:
                    # si existe el detalle solo creamos el tareo
                    id_tareo = obj_tareo.search(
                        [['idunidad', '=', id_detalle_contrato_tareo.unidad_id.id], ['fecha', '=', self.fecha_tareo],
                         ['iddetalle_contrato', '=', id_detalle_contrato_tareo.id],
                         ['idruta', '=', id_detalle_contrato_tareo.ruta_id.id], ['tipo', '=', 'a']])
                    # si existe el tareo actualizamos el tareo con 1 pero si no existe lo creamos
                    if not id_tareo:
                        obj_tareo.create({
                            'tipo': 'a',
                            'idunidad': id_detalle_contrato_tareo.unidad_id.id,
                            'monto': line.valor,
                            'fecha': self.fecha_tareo,
                            'iddetalle_contrato': id_detalle_contrato_tareo.id,
                            'cambio': True,
                            'idruta': id_detalle_contrato_tareo.ruta_id.id or '',
                        })
                    else:
                        id_tareo.write({
                            'tipo': 'a',
                            'idunidad': id_detalle_contrato_tareo.unidad_id.id,
                            'monto': line.valor,
                            'fecha': self.fecha_tareo,
                            'iddetalle_contrato': id_detalle_contrato_tareo.id,
                            'cambio': True,
                            'idruta': id_detalle_contrato_tareo.ruta_id.id or '',
                        })

                    id_valorizacion_descripcion = obj_valorizacion_descripciones.search(
                        [
                            ['contrato_id', '=', self.contrato.id],
                            ['unificado_varios_clientes', '=', True],
                            ['adicional', '=', True],
                            ['vehiculo_id', '=', line.vehiculo_id.id],
                            ['cliente', '=', line.cliente.id],
                            ['fecha_tareo', '=', self.fecha_tareo],
                            ['ruta_id', '=', line.ruta_id.id],
                            ['contrato_detalle_id', '=', id_detalle_contrato_tareo.id],
                        ])

                    if not id_valorizacion_descripcion:
                        # creamos las descripcion para variable
                        obj_valorizacion_descripciones.create({
                            'unificado_varios_clientes': True,
                            'fijo': False,
                            'variable': False,
                            'adicional': True,
                            'nota_detalle_contrato': line.descripcion,
                            'contrato_id': self.contrato.id,
                            'vehiculo_id': line.vehiculo_id.id,
                            'cliente': line.cliente.id,
                            'fecha_tareo': self.fecha_tareo,
                            'valor': line.valor,
                            'ruta_id': line.ruta_id.id,
                            'descripcion_detalle_tareo': line.descripcion_detalle_tareo,
                            'contrato_detalle_id': id_detalle_contrato_tareo.id,
                        })
                    else:
                        # si existe actualizamos las descripcion para variable
                        id_valorizacion_descripcion.write({
                            'unificado_varios_clientes': True,
                            'fijo': False,
                            'variable': False,
                            'adicional': True,
                            'nota_detalle_contrato': line.descripcion,
                            'contrato_id': self.contrato.id,
                            'vehiculo_id': line.vehiculo_id.id,
                            'cliente': line.cliente.id,
                            'fecha_tareo': self.fecha_tareo,
                            'valor': line.valor,
                            'ruta_id': line.ruta_id.id,
                            'descripcion_detalle_tareo': line.descripcion_detalle_tareo,
                            'contrato_detalle_id': id_detalle_contrato_tareo.id,
                        })
        else:
            # costo fijo
            for line in self.contrato_ids:
                # juntamos todas las notas
                notas.append(line.descripcion)
                id_detalle_contrato_tareo = obj_vehiculo_contrato_detalle.search(
                    [['parent_id', '=', self.contrato.id], ['unidad_id', '=', line.vehiculo_id.id],
                     ['ruta_id', '=', line.ruta_id.id]])
                if not id_detalle_contrato_tareo:
                    id_proveedor = ''
                    if line.vehiculo_id.alquilado_propio:
                        id_proveedor = line.vehiculo_id.proveedor.id
                    # si no existe el vehiculo en el contrato creamos el detalle
                    res = obj_vehiculo_contrato_detalle.create({
                        'area_id': '',
                        'descripcion_adicional': '',
                        'descripcion_proveedor': '',
                        'descripcion_rutas': '',
                        'horario_id': '',
                        'tot_dias_adicional': '',
                        'importe_adicional': '',
                        'tarifa_costo_adicional': '',
                        'parent_id': self.contrato.id,
                        'descripcion_variable': '',
                        'costo_varios_clientes': '',
                        'descripcion_fijo': '',
                        'km_fijo': '',
                        'descripcion_proveedor_km': '',
                        'unidad_id': line.vehiculo_id.id,
                        'km_proveedor': '',
                        'importe_variable': '',
                        'importe_fijo': '',
                        'tarifa_costo_fijo': '',
                        'name': self.contrato.name,
                        'tot_dias_variable': '',
                        'tot_dias_fijo': '',
                        'importe_proveedor': '',
                        'tarifa_costo_variable': '',
                        'ruta_id': line.ruta_id.id,
                        'cliente': self.contrato.cliente.id,
                        'estado_detalle': 'nuevo',
                        'codigo_proveedor': id_proveedor,
                    })
                    # creamos el tareo con un 1 en la fecha correspondiente
                    obj_tareo.create({
                        'tipo': 'f',
                        'idunidad': line.vehiculo_id.id,
                        'monto': line.valor,
                        'fecha': self.fecha_tareo,
                        'iddetalle_contrato': res.id,
                        'cambio': True,
                        'idruta': line.ruta_id.id,
                    })

                    # creamos las descripcion para fijo
                    obj_valorizacion_descripciones.create({
                        'unificado_varios_clientes': False,
                        'fijo': True,
                        'variable': False,
                        'adicional': False,
                        'nota_detalle_contrato': line.descripcion,
                        'contrato_id': self.contrato.id,
                        'vehiculo_id': line.vehiculo_id.id,
                        'cliente': self.contrato.cliente.id,
                        'fecha_tareo': self.fecha_tareo,
                        'valor': line.valor,
                        'ruta_id': line.ruta_id.id,
                        'descripcion_detalle_tareo': line.descripcion_detalle_tareo,
                        'contrato_detalle_id': res.id,
                    })

                else:
                    # si existe el detalle solo creamos el tareo
                    id_tareo = obj_tareo.search(
                        [['idunidad', '=', id_detalle_contrato_tareo.unidad_id.id], ['fecha', '=', self.fecha_tareo],
                         ['iddetalle_contrato', '=', id_detalle_contrato_tareo.id],
                         ['idruta', '=', id_detalle_contrato_tareo.ruta_id.id], ['tipo', '=', 'f']])
                    # si existe el tareo actualizamos el tareo con 1 pero si no existe lo creamos
                    if not id_tareo:
                        obj_tareo.create({
                            'tipo': 'f',
                            'idunidad': id_detalle_contrato_tareo.unidad_id.id,
                            'monto': line.valor,
                            'fecha': self.fecha_tareo,
                            'iddetalle_contrato': id_detalle_contrato_tareo.id,
                            'cambio': True,
                            'idruta': id_detalle_contrato_tareo.ruta_id.id or '',
                        })
                    else:
                        id_tareo.write({
                            'tipo': 'f',
                            'idunidad': id_detalle_contrato_tareo.unidad_id.id,
                            'monto': line.valor,
                            'fecha': self.fecha_tareo,
                            'iddetalle_contrato': id_detalle_contrato_tareo.id,
                            'cambio': True,
                            'idruta': id_detalle_contrato_tareo.ruta_id.id or '',
                        })

                    id_valorizacion_descripcion = obj_valorizacion_descripciones.search(
                        [
                            ['contrato_id', '=', self.contrato.id],
                            ['unificado_varios_clientes', '=', False],
                            ['fijo', '=', True],
                            ['vehiculo_id', '=', line.vehiculo_id.id],
                            ['cliente', '=', self.contrato.cliente.id],
                            ['fecha_tareo', '=', self.fecha_tareo],
                            ['ruta_id', '=', line.ruta_id.id],
                            ['contrato_detalle_id', '=', id_detalle_contrato_tareo.id],
                        ])

                    if not id_valorizacion_descripcion:
                        # creamos las descripcion para variable
                        obj_valorizacion_descripciones.create({
                            'unificado_varios_clientes': False,
                            'fijo': True,
                            'variable': False,
                            'adicional': False,
                            'nota_detalle_contrato': line.descripcion,
                            'contrato_id': self.contrato.id,
                            'vehiculo_id': line.vehiculo_id.id,
                            'cliente': self.contrato.cliente.id,
                            'fecha_tareo': self.fecha_tareo,
                            'valor': line.valor,
                            'ruta_id': line.ruta_id.id,
                            'descripcion_detalle_tareo': line.descripcion_detalle_tareo,
                            'contrato_detalle_id': id_detalle_contrato_tareo.id,
                        })
                    else:
                        # si existe actualizamos las descripcion para variable
                        id_valorizacion_descripcion.write({
                            'unificado_varios_clientes': False,
                            'fijo': True,
                            'variable': False,
                            'adicional': False,
                            'nota_detalle_contrato': line.descripcion,
                            'contrato_id': self.contrato.id,
                            'vehiculo_id': line.vehiculo_id.id,
                            'cliente': self.contrato.cliente.id,
                            'fecha_tareo': self.fecha_tareo,
                            'valor': line.valor,
                            'ruta_id': line.ruta_id.id,
                            'descripcion_detalle_tareo': line.descripcion_detalle_tareo,
                            'contrato_detalle_id': id_detalle_contrato_tareo.id,
                        })

            # costo variable
            for line in self.contrato_ids_var:
                # juntamos todas las notas
                notas.append(line.descripcion)
                id_detalle_contrato_tareo = obj_vehiculo_contrato_detalle.search(
                    [['parent_id', '=', self.contrato.id], ['unidad_id', '=', line.vehiculo_id.id],
                     ['ruta_id', '=', line.ruta_id.id]])
                if not id_detalle_contrato_tareo:
                    id_proveedor = ''
                    if line.vehiculo_id.alquilado_propio:
                        id_proveedor = line.vehiculo_id.proveedor.id
                    # si no existe el vehiculo en el contrato creamos el detalle
                    res = obj_vehiculo_contrato_detalle.create({
                        'area_id': '',
                        'descripcion_adicional': '',
                        'descripcion_proveedor': '',
                        'descripcion_rutas': '',
                        'horario_id': '',
                        'tot_dias_adicional': '',
                        'importe_adicional': '',
                        'tarifa_costo_adicional': '',
                        'parent_id': self.contrato.id,
                        'descripcion_variable': '',
                        'costo_varios_clientes': '',
                        'descripcion_fijo': '',
                        'km_fijo': '',
                        'descripcion_proveedor_km': '',
                        'unidad_id': line.vehiculo_id.id,
                        'km_proveedor': '',
                        'importe_variable': '',
                        'importe_fijo': '',
                        'tarifa_costo_fijo': '',
                        'name': self.contrato.name,
                        'tot_dias_variable': '',
                        'tot_dias_fijo': '',
                        'importe_proveedor': '',
                        'tarifa_costo_variable': '',
                        'ruta_id': line.ruta_id.id,
                        'cliente': self.contrato.cliente.id,
                        'estado_detalle': 'nuevo',
                        'codigo_proveedor': id_proveedor,
                    })
                    # creamos el tareo con un 1 en la fecha correspondiente
                    obj_tareo.create({
                        'tipo': 'v',
                        'idunidad': line.vehiculo_id.id,
                        'monto': line.valor,
                        'fecha': self.fecha_tareo,
                        'iddetalle_contrato': res.id,
                        'cambio': True,
                        'idruta': line.ruta_id.id,
                    })

                    # creamos las descripcion para variable
                    obj_valorizacion_descripciones.create({
                        'unificado_varios_clientes': False,
                        'fijo': False,
                        'variable': True,
                        'adicional': False,
                        'nota_detalle_contrato': line.descripcion,
                        'contrato_id': self.contrato.id,
                        'vehiculo_id': line.vehiculo_id.id,
                        'cliente': self.contrato.cliente.id,
                        'fecha_tareo': self.fecha_tareo,
                        'valor': line.valor,
                        'ruta_id': line.ruta_id.id,
                        'descripcion_detalle_tareo': line.descripcion_detalle_tareo,
                        'contrato_detalle_id': res.id,
                    })

                else:
                    # si existe el detalle solo creamos el tareo
                    id_tareo = obj_tareo.search(
                        [['idunidad', '=', id_detalle_contrato_tareo.unidad_id.id], ['fecha', '=', self.fecha_tareo],
                         ['iddetalle_contrato', '=', id_detalle_contrato_tareo.id],
                         ['idruta', '=', id_detalle_contrato_tareo.ruta_id.id], ['tipo', '=', 'v']])
                    # si existe el tareo actualizamos el tareo con 1 pero si no existe lo creamos
                    if not id_tareo:
                        obj_tareo.create({
                            'tipo': 'v',
                            'idunidad': id_detalle_contrato_tareo.unidad_id.id,
                            'monto': line.valor,
                            'fecha': self.fecha_tareo,
                            'iddetalle_contrato': id_detalle_contrato_tareo.id,
                            'cambio': True,
                            'idruta': id_detalle_contrato_tareo.ruta_id.id or '',
                        })
                    else:
                        id_tareo.write({
                            'tipo': 'v',
                            'idunidad': id_detalle_contrato_tareo.unidad_id.id,
                            'monto': line.valor,
                            'fecha': self.fecha_tareo,
                            'iddetalle_contrato': id_detalle_contrato_tareo.id,
                            'cambio': True,
                            'idruta': id_detalle_contrato_tareo.ruta_id.id or '',
                        })

                    id_valorizacion_descripcion = obj_valorizacion_descripciones.search(
                        [
                            ['contrato_id', '=', self.contrato.id],
                            ['unificado_varios_clientes', '=', False],
                            ['variable', '=', True],
                            ['vehiculo_id', '=', line.vehiculo_id.id],
                            ['cliente', '=', self.contrato.cliente.id],
                            ['fecha_tareo', '=', self.fecha_tareo],
                            ['ruta_id', '=', line.ruta_id.id],
                            ['contrato_detalle_id', '=', id_detalle_contrato_tareo.id],
                        ])

                    if not id_valorizacion_descripcion:
                        # creamos las descripcion para variable
                        obj_valorizacion_descripciones.create({
                            'unificado_varios_clientes': False,
                            'fijo': False,
                            'variable': True,
                            'adicional': False,
                            'nota_detalle_contrato': line.descripcion,
                            'contrato_id': self.contrato.id,
                            'vehiculo_id': line.vehiculo_id.id,
                            'cliente': self.contrato.cliente.id,
                            'fecha_tareo': self.fecha_tareo,
                            'valor': line.valor,
                            'ruta_id': line.ruta_id.id,
                            'descripcion_detalle_tareo': line.descripcion_detalle_tareo,
                            'contrato_detalle_id': id_detalle_contrato_tareo.id,
                        })
                    else:
                        # si existe actualizamos las descripcion para variable
                        id_valorizacion_descripcion.write({
                            'unificado_varios_clientes': False,
                            'fijo': False,
                            'variable': True,
                            'adicional': False,
                            'nota_detalle_contrato': line.descripcion,
                            'contrato_id': self.contrato.id,
                            'vehiculo_id': line.vehiculo_id.id,
                            'cliente': self.contrato.cliente.id,
                            'fecha_tareo': self.fecha_tareo,
                            'valor': line.valor,
                            'ruta_id': line.ruta_id.id,
                            'descripcion_detalle_tareo': line.descripcion_detalle_tareo,
                            'contrato_detalle_id': id_detalle_contrato_tareo.id,
                        })

            # costo adicional
            for line in self.contrato_ids_adi:
                # juntamos todas las notas
                notas.append(line.descripcion)
                id_detalle_contrato_tareo = obj_vehiculo_contrato_detalle.search(
                    [['parent_id', '=', self.contrato.id], ['unidad_id', '=', line.vehiculo_id.id],
                     ['ruta_id', '=', line.ruta_id.id]])
                if not id_detalle_contrato_tareo:
                    id_proveedor = ''
                    if line.vehiculo_id.alquilado_propio:
                        id_proveedor = line.vehiculo_id.proveedor.id
                    # si no existe el vehiculo en el contrato creamos el detalle
                    res = obj_vehiculo_contrato_detalle.create({
                        'area_id': '',
                        'descripcion_adicional': '',
                        'descripcion_proveedor': '',
                        'descripcion_rutas': '',
                        'horario_id': '',
                        'tot_dias_adicional': '',
                        'importe_adicional': '',
                        'tarifa_costo_adicional': '',
                        'parent_id': self.contrato.id,
                        'descripcion_variable': '',
                        'costo_varios_clientes': '',
                        'descripcion_fijo': '',
                        'km_fijo': '',
                        'descripcion_proveedor_km': '',
                        'unidad_id': line.vehiculo_id.id,
                        'km_proveedor': '',
                        'importe_variable': '',
                        'importe_fijo': '',
                        'tarifa_costo_fijo': '',
                        'name': self.contrato.name,
                        'tot_dias_variable': '',
                        'tot_dias_fijo': '',
                        'importe_proveedor': '',
                        'tarifa_costo_variable': '',
                        'ruta_id': line.ruta_id.id,
                        'cliente': self.contrato.cliente.id,
                        'estado_detalle': 'nuevo',
                        'codigo_proveedor': id_proveedor,
                    })
                    # creamos el tareo con un 1 en la fecha correspondiente
                    obj_tareo.create({
                        'tipo': 'a',
                        'idunidad': line.vehiculo_id.id,
                        'monto': line.valor,
                        'fecha': self.fecha_tareo,
                        'iddetalle_contrato': res.id,
                        'cambio': True,
                        'idruta': line.ruta_id.id,
                    })

                    # creamos las descripcion para variable
                    obj_valorizacion_descripciones.create({
                        'unificado_varios_clientes': False,
                        'fijo': False,
                        'variable': False,
                        'adicional': True,
                        'nota_detalle_contrato': line.descripcion,
                        'contrato_id': self.contrato.id,
                        'vehiculo_id': line.vehiculo_id.id,
                        'cliente': self.contrato.cliente.id,
                        'fecha_tareo': self.fecha_tareo,
                        'valor': line.valor,
                        'ruta_id': line.ruta_id.id,
                        'descripcion_detalle_tareo': line.descripcion_detalle_tareo,
                        'contrato_detalle_id': res.id,
                    })
                else:
                    # si existe el detalle solo creamos el tareo
                    id_tareo = obj_tareo.search(
                        [['idunidad', '=', id_detalle_contrato_tareo.unidad_id.id], ['fecha', '=', self.fecha_tareo],
                         ['iddetalle_contrato', '=', id_detalle_contrato_tareo.id],
                         ['idruta', '=', id_detalle_contrato_tareo.ruta_id.id], ['tipo', '=', 'a']])
                    # si existe el tareo actualizamos el tareo con 1 pero si no existe lo creamos
                    if not id_tareo:
                        obj_tareo.create({
                            'tipo': 'a',
                            'idunidad': id_detalle_contrato_tareo.unidad_id.id,
                            'monto': line.valor,
                            'fecha': self.fecha_tareo,
                            'iddetalle_contrato': id_detalle_contrato_tareo.id,
                            'cambio': True,
                            'idruta': id_detalle_contrato_tareo.ruta_id.id or '',
                        })
                    else:
                        id_tareo.write({
                            'tipo': 'a',
                            'idunidad': id_detalle_contrato_tareo.unidad_id.id,
                            'monto': line.valor,
                            'fecha': self.fecha_tareo,
                            'iddetalle_contrato': id_detalle_contrato_tareo.id,
                            'cambio': True,
                            'idruta': id_detalle_contrato_tareo.ruta_id.id or '',
                        })
                    id_valorizacion_descripcion = obj_valorizacion_descripciones.search(
                        [
                            ['contrato_id', '=', self.contrato.id],
                            ['unificado_varios_clientes', '=', False],
                            ['adicional', '=', True],
                            ['vehiculo_id', '=', line.vehiculo_id.id],
                            ['cliente', '=', self.contrato.cliente.id],
                            ['fecha_tareo', '=', self.fecha_tareo],
                            ['ruta_id', '=', line.ruta_id.id],
                            ['contrato_detalle_id', '=', id_detalle_contrato_tareo.id],
                        ])

                    if not id_valorizacion_descripcion:
                        # creamos las descripcion para variable
                        obj_valorizacion_descripciones.create({
                            'unificado_varios_clientes': False,
                            'fijo': False,
                            'variable': False,
                            'adicional': True,
                            'nota_detalle_contrato': line.descripcion,
                            'contrato_id': self.contrato.id,
                            'vehiculo_id': line.vehiculo_id.id,
                            'cliente': self.contrato.cliente.id,
                            'fecha_tareo': self.fecha_tareo,
                            'valor': line.valor,
                            'ruta_id': line.ruta_id.id,
                            'descripcion_detalle_tareo': line.descripcion_detalle_tareo,
                            'contrato_detalle_id': id_detalle_contrato_tareo.id,
                        })
                    else:
                        # si existe actualizamos las descripcion para variable
                        id_valorizacion_descripcion.write({
                            'unificado_varios_clientes': False,
                            'fijo': False,
                            'variable': False,
                            'adicional': True,
                            'nota_detalle_contrato': line.descripcion,
                            'contrato_id': self.contrato.id,
                            'vehiculo_id': line.vehiculo_id.id,
                            'cliente': self.contrato.cliente.id,
                            'fecha_tareo': self.fecha_tareo,
                            'valor': line.valor,
                            'ruta_id': line.ruta_id.id,
                            'descripcion_detalle_tareo': line.descripcion_detalle_tareo,
                            'contrato_detalle_id': id_detalle_contrato_tareo.id,
                        })
        # raise Warning()
        tareo_mensual = obj_tareo_mensual.search(
            [['contrato', '=', self.contrato.id], ['cliente_id', '=', self.contrato.cliente.id]])
        if tareo_mensual:
            tareo_mensual.write({
                'nota': ' - '.join(notas),
            })
        start = datetime.datetime.strptime(str(self.fecha_tareo), '%Y-%m-%d')
        self.fecha_tareo = start + datetime.timedelta(days=1)
        # return self.fecha_tareo

        self.onchange_method()
        self.get_room_summary()
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def room_reservation(self):
        '''
        @param self: object pointer
        '''
        mod_obj = self.env['ir.model.data']
        if self._context is None:
            self._context = {}
        context = self._context.copy()
        context.update({'contrato': self.contrato, 'fecha': self.fecha_tareo})

        model_data_ids = mod_obj.search([('model', '=', 'ir.ui.view'),
                                         ('name', '=',
                                          'vehiculo_contrato_summary_form_view')])
        resource_id = model_data_ids.read(fields=['res_id'])[0]['res_id']
        return {'name': _('Historial Tareos'),
                'context': self._context,
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'vehiculo.contrato.summary',
                'views': [(resource_id, 'form')],
                'type': 'ir.actions.act_window',
                'target': 'new',
                }


# costo fijo
class m_valorizaciones_tareo_wizard_det(models.TransientModel):
    _name = 'm.valorizacion.tareo.wizard.det'

    cliente = fields.Many2one('res.partner', 'Cliente')

    vehiculo_id = fields.Many2one('fleet.vehicle', 'Vehículo', required=True)
    ruta_id = fields.Many2one('modulo_valorizaciones.ruta', 'Ruta', required=True)
    valor = fields.Integer(string="valor", required=False, )
    descripcion = fields.Char('Descripción')
    contrato_id = fields.Many2one(comodel_name="m.valorizacion.tareo.wizard", string="Vehiculos", required=False, )
    unificado_varios_clientes = fields.Boolean(related='contrato_id.unificado_varios_clientes', string="Varios", store=True)
    descripcion_detalle_tareo = fields.Char('Descripción')

# costo variable
class m_valorizaciones_tareo_wizard_det_var(models.TransientModel):
    _name = 'm.valorizacion.tareo.wizard.det.var'

    cliente = fields.Many2one('res.partner', 'Cliente')

    vehiculo_id = fields.Many2one('fleet.vehicle', 'Vehículo', required=True)
    ruta_id = fields.Many2one('modulo_valorizaciones.ruta', 'Ruta', required=True)
    valor = fields.Integer(string="valor", required=False, )
    descripcion = fields.Char('Descripción')
    contrato_id = fields.Many2one(comodel_name="m.valorizacion.tareo.wizard", string="Vehiculos", required=False, )
    unificado_varios_clientes = fields.Boolean(related='contrato_id.unificado_varios_clientes', string="Varios", store=True)
    descripcion_detalle_tareo = fields.Char('Descripción')

# costo adicional
class m_valorizaciones_tareo_wizard_det_adi(models.TransientModel):
    _name = 'm.valorizacion.tareo.wizard.det.adi'

    cliente = fields.Many2one('res.partner', 'Cliente')

    vehiculo_id = fields.Many2one('fleet.vehicle', 'Vehículo', required=True)
    ruta_id = fields.Many2one('modulo_valorizaciones.ruta', 'Ruta', required=True)
    valor = fields.Integer(string="valor", required=False, )
    descripcion = fields.Char('Descripción')
    contrato_id = fields.Many2one(comodel_name="m.valorizacion.tareo.wizard", string="Vehiculos", required=False, )
    unificado_varios_clientes = fields.Boolean(related='contrato_id.unificado_varios_clientes', string="Varios", store=True)
    descripcion_detalle_tareo = fields.Char('Descripción')

class m_valorizacion_many2many_vd(models.TransientModel):
    _name = 'm.valorizacion.many2many.vd'
    # _description = 'New Description'

    vehiculo_ids = fields.Many2many('fleet.vehicle', 'm_valorizacion_vehiculos', 'vehiculo', 'tareo_vc_id', 'Vehiculos')

    @api.multi
    def pasar_datos(self):
        context = dict(self._context or {})
        vehiculo_id = context.get('vehiculo_id', False)
        if not vehiculo_id:
            return {'type': 'ir.actions.act_window_close'}

        data = self.read()[0]
        vehiculo_ids = data['vehiculo_ids']
        if not vehiculo_ids:
            return {'type': 'ir.actions.act_window_close'}

        line_obj = self.env['fleet.vehicle']
        statement_objeto = self.env['m.valorizacion.tareo.wizard']
        statement_obj = self.env['m.valorizacion.tareo.wizard'].search([], limit=1, order = 'id desc')
        statement_line_obj = self.env['m.valorizacion.tareo.wizard.det']
        statement_line_obj_var = self.env['m.valorizacion.tareo.wizard.det.var']
        statement_line_obj_adi = self.env['m.valorizacion.tareo.wizard.det.adi']


        # for each selected move lines
        for line in line_obj.browse(vehiculo_ids):
            ctx = context.copy()
            print (line)
            print ('----------')
            if statement_obj.contrato.costo_fijo:
                statement_line_obj.create({
                    'vehiculo_id': line.id,
                    'ruta_id': 1,
                    'valor': 13,
                    'descripcion': '',
                    'contrato_id': vehiculo_id,
                })
            if statement_obj.contrato.costo_variable:
                statement_line_obj_var.create({
                    'vehiculo_id': line.id,
                    'ruta_id': 13,
                    'valor': 0,
                    'descripcion': '',
                    'contrato_id': vehiculo_id,
                })
            if statement_obj.contrato.costo_adicional:
                statement_line_obj_adi.create({
                    'vehiculo_id': line.id,
                    'ruta_id': 13,
                    'valor': 0,
                    'descripcion': '',
                    'contrato_id': vehiculo_id,
                })
            # statement_obj.onchange_method()
            # statement_obj.get_room_summary()
        avc = self.env['warning_box'].info(title='Elija una Ruta!',
                                               message="Elija la ruta que desea se asigno una por defecto!")

        return avc
        # return {'type': 'ir.actions.act_window_close'}
