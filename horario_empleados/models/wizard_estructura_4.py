# -*- coding: utf-8 -*-
"""Framework for importing bank statement files."""
import logging
import base64

from openerp import api, models, fields
from openerp.tools.translate import _
import datetime


_logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


class Estructura4HrEmployee(models.TransientModel):
    def generate_file1111(self):
        return 'Estructura4:DATOSPERSONALES.txt'

    def generate_file22(self):
        content = ''
        obj_direcciones = self.env['hr.direccion.detalle'].search([])
        for f in obj_direcciones:
            content += str(f.direccion_or_id.direccion_id.tipo_documento or '') + '|' + str(
                f.direccion_or_id.direccion_id.identification_id or '') + '|' + str(
                f.direccion_or_id.direccion_id.pais_de_emision.code or '' if f.direccion_or_id.direccion_id.tipo_documento == '07' else '') + '|' + str(
                f.direccion_or_id.direccion_id.birthday or '') + '|' + str(f.direccion_or_id.direccion_id.apellido_paterno or '') + '|' + str(f.direccion_or_id.direccion_id.apellido_materno or '') + '|' + str(f.direccion_or_id.direccion_id.primer_nombre or '') + ' ' + str(f.direccion_or_id.direccion_id.segundo_nombre or '') + '|' + str(f.direccion_or_id.direccion_id.gender or '') + '|' + str(f.direccion_or_id.direccion_id.primera_nacionalidad.code or '') + '|' + str(f.direccion_or_id.direccion_id.cod_ldn.code or '') + '|' + str(f.direccion_or_id.direccion_id.numero or '') + '|' + str(f.direccion_or_id.direccion_id.work_email or '') + '|' + str(f.tipo_via.code or '') + '|' + str(f.nombre_via or '') + '|' + str(f.nro or '') + '|' + str(f.depto_nro or '') + '|' + str(f.interior or '') + '|' + str(f.mza or '') + '|' + str(f.nro_lote or '') + '|' + str(f.nro_kilom or '') + '|' + str(f.nro_block or '') + '|' + str(f.nro_etapa or '') + '|' + str(f.tipo_zona.code or '') + '|' + str(f.nombre_zona or '') + '|' + str(f.referencia or '') + '|' + str(f.referencia or '') + '|' + str(f.direccion_or_id.direccion_id.place_of_birth or '') + '|' + str(f.direccion_or_id.direccion_id.centro_salud or '') + '\n'
        return base64.encodestring(content)

    """Extend model account.bank.statement."""
    _name = 'hr.employee.estructura.4'
    _description = 'Estructura 4'

    txt_filename = fields.Char(default=generate_file1111)
    txt_binary = fields.Binary(default=generate_file22)


class Estructura5HrEmployee(models.TransientModel):
    def generate_file3(self):
        return 'Estructura 5: DATOS DEL TRABAJADOR.txt'

    def generate_file4(self):
        content = ''
        obj_employee = self.env['hr.employee']
        employees = obj_employee.search([])
        obj_contract = self.env['hr.contract']
        for emp in employees:
            contract_ids = obj_contract.search([('employee_id', '=', emp.id), ], order='date_start desc', limit=1)
            for f in contract_ids:

                content += str(f.employee_id.tipo_documento or '') + '|' + str(
                    f.employee_id.identification_id or '') + '|' + str(
                    f.employee_id.pais_de_emision.code or '' if f.employee_id.tipo_documento == '07' else '') + '|' + str(
                    f.regimen_laboral.code or '') + '|' + str(f.employee_id.situacion_educativa.code or '') + '|' + str(
                    f.employee_id.ocupacion.code or '') + '|' + str(
                    '1' or '' if f.employee_id.discapacidad else '0') + '|' + str(f.employee_id.cupps or '') + '|' + str(f.employee_id.sctr_pension or '') + '|' + str(f.type_id.code or '') + '|' + str(
                    '1' or '' if f.regimen_acumulativo else '0') + '|' + str(
                    '1' or '' if f.jornada_maxima else '0') + '|' + str(
                    '1' or '' if f.horario_nocturno else '0') + '|' + str(
                    '1' or '' if f.employee_id.es_sindicalizado else '0') + '|' + str(f.periodicidad_remu or '') + '|' + str(f.wage or '') + '|' + str(f.employee_id.situacion or '') + '|' + str(
                    '1' or '' if f.renta_5_exonerada else '0') + '|' + str(f.employee_id.situacion_especial or '') + '|' + str(f.tipo_pago or '') + '|' + str(f.employee_id.categoria_ocupacional.code or '') + '|' + str(f.employee_id.doble_tributacion or '') + '|' + str(f.employee_id.ruc_employee or '' if f.employee_id.tipo_trabajador.code == '67' else '') + '\n'
        return base64.encodestring(content)

    _name = 'hr.employee.estructura.5'
    _description = 'Estructura 5'

    txt_filename = fields.Char(default=generate_file3)
    txt_binary = fields.Binary(default=generate_file4)


class Estructura11HrEmployee(models.TransientModel):
    def generate_file4(self):
        return 'Estructura 11: DATOS DE PERIODOS.txt'

    def generate_file5(self):
        content = ''
        obj_employee = self.env['hr.employee']
        employees = obj_employee.search([])
        obj_contract = self.env['hr.contract']

        for emp in employees:
            contract_ids = obj_contract.search([('employee_id', '=', emp.id), ], order='date_start desc', limit=1)
            obj_contract_periodos = self.env['hr.contract.periodos'].search([('periodo_id.employee_id', '=', emp.id), ])
            for f in contract_ids:
                for ar in obj_contract_periodos:
                    content += str(f.employee_id.tipo_documento or '') + '|' + str(
                        f.employee_id.identification_id or '') + '|' + str(
                        f.employee_id.pais_de_emision.code or '' if f.employee_id.tipo_documento == '07' else '') + '|' + str(ar.categoria or '') + '|' + str(ar.tipo_registro or '') + '|' + str(ar.fecha_inicio or '') + '|' + str(ar.fecha_fin or '') + '|' + str(ar.indicador_motivo_fin.code or '') + '' + str(ar.indicador_tipo_trabajador.code or '') + '' + str(ar.indicador_regimen_aseguramiento.code or '') + '' + str(ar.indicador_regimen_pensionario.code or '') + '' + str(ar.indicador_sctr_salud or '')+ '|' + str(ar.eps_servicio_propio or '') + '\n'
        return base64.encodestring(content)

    _name = 'hr.employee.estructura.11'
    _description = 'Estructura 11'

    txt_filename = fields.Char(default=generate_file4)
    txt_binary = fields.Binary(default=generate_file5)


class Estructura17HrEmployee(models.TransientModel):
    def generate_file6(self):
        return 'Estructura 17: ESTABLECIMIENTOS DONDE LABORA EL TRABAJADOR.txt'

    def generate_file7(self):
        content = ''
        obj_employee = self.env['hr.employee']
        employees = obj_employee.search([])
        obj_contract = self.env['hr.contract']
        company = self.env['res.company'].browse(1)
        for emp in employees:
            contract_ids = obj_contract.search([('employee_id', '=', emp.id), ], order='date_start desc', limit=1)
            for f in contract_ids:
                content += str(f.employee_id.tipo_documento or '') + '|' + str(
                    f.employee_id.identification_id or '') + '|' + str(
                    f.employee_id.pais_de_emision.code or '' if f.employee_id.tipo_documento == '07' else '') + '|' + str(
                    company.x_ruc or '') + '|' + str('') + '\n'
        return base64.encodestring(content)

    _name = 'hr.employee.estructura.17'
    _description = 'Estructura 17'

    txt_filename = fields.Char(default=generate_file6)
    txt_binary = fields.Binary(default=generate_file7)


class Estructura29HrEmployee(models.TransientModel):
    def generate_file8(self):
        return 'Estructura 29: DATOS DE ESTUDIOS CONCLUIDOS.txt'

    def generate_file9(self):
        content = ''
        # obj_employee = self.env['hr.employee']
        obj_employee_concluidos = self.env['hr.estudios.concluidos']
        employees_estudios = obj_employee_concluidos.search([])
        # employees = obj_employee.search([])

        for f in employees_estudios:
            content += str(f.employee_id.tipo_documento or '') + '|' + str(
                f.employee_id.identification_id or '') + '|' + str(
                f.employee_id.pais_de_emision.code or '' if f.employee_id.tipo_documento == '07' else '') + '|' + str(f.superior_completa.code or '') + '|' + str(f.ind_superior_completa or '') + '|' + str(f.codigo_inst_educativa.code_tipo_inst or '') + '|' + str(f.codigo_inst_educativa.code_tipo_inst or '') + '|' + str(f.anio_egreso or '') + '\n'
        return base64.encodestring(content)

    _name = 'hr.employee.estructura.29'
    _description = 'Estructura 29'

    txt_filename = fields.Char(default=generate_file8)
    txt_binary = fields.Binary(default=generate_file9)


# class hr_payslip_employees(models.TransientModel):
#     _inherit = 'hr.payslip.employees'
#
#     @api.v7
#     def compute_sheet(self, cr, uid, ids, context=None):
#         emp_pool = self.pool.get('hr.employee')
#         slip_pool = self.pool.get('hr.payslip')
#         run_pool = self.pool.get('hr.payslip.run')
#
#
#         obj_contract = self.pool.get('hr.contract')
#
#         data = self.read(cr, uid, ids, context=context)[0]
#         # print (data)
#         if context is None:
#             context = {}
#         if context and context.get('active_id', False):
#             run_data = run_pool.read(cr, uid, [context['active_id']], ['date_start', 'date_end', 'credit_note'])[0]
#         from_date = run_data.get('date_start', False)
#         to_date = run_data.get('date_end', False)
#         anio_fiscal = to_date[:4]
#         mes_fiscal = to_date[5:-3]
#         # año fiscal
#         re = self.pool.get('account.fiscalyear').find(cr, uid, context=context)
#         # mes actual
#         x = datetime.datetime.now()
#         mes = x.month
#         # sacar UIT
#         uit_ids = self.pool.get('hr.uit.sunat').search(cr, uid, [], context=context)
#         for uit_id in self.pool.get('hr.uit.sunat').browse(cr, uid, uit_ids):
#             uit = uit_id.valor_uit
#             # print (uit_id.valor_uit)
#         # sacar DEDUCCION
#         deducciones_ids = self.pool.get('hr.deducciones.x.ejercicio').search(cr, uid, [], context=context)
#         for deducciones_id in self.pool.get('hr.deducciones.x.ejercicio').browse(cr, uid, deducciones_ids):
#             deduccion = deducciones_id.deducir
#             # print (deducciones_id.deducir)
#         # sacar VALOR
#
#         valor_ids = self.pool.get('hr.mes.x.ejercicio.detalle').search(cr, uid, [['mes','=',int(mes_fiscal)]], context=context)
#         # print (valor_ids)
#         for valor_id in self.pool.get('hr.mes.x.ejercicio.detalle').browse(cr, uid, valor_ids):
#             valor = valor_id.valor
#             # print (valor_id.valor)
#         meses_anteriores = 0
#         if valor == 12:
#             meses_anteriores = 0
#         elif valor == 11:
#             meses_anteriores = 1
#         elif valor == 10:
#             meses_anteriores = 2
#         elif valor == 9:
#             meses_anteriores = 3
#         elif valor == 8:
#             meses_anteriores = 4
#         elif valor == 7:
#             meses_anteriores = 5
#         elif valor == 6:
#             meses_anteriores = 6
#         elif valor == 5:
#             meses_anteriores = 7
#         elif valor == 4:
#             meses_anteriores = 8
#         elif valor == 3:
#             meses_anteriores = 9
#         elif valor == 2:
#             meses_anteriores = 10
#         elif valor == 1:
#             meses_anteriores = 11
#
#         # sacar FACTOR
#         factor_ids = self.pool.get('hr.factor.x.ejercicio.detalle').search(cr, uid, [['factor_id.ejercicio_fiscal_id.code','=',anio_fiscal],['mes_inicio','=',int(mes_fiscal)]], context=context)
#         for factor in self.pool.get('hr.factor.x.ejercicio.detalle').browse(cr, uid, factor_ids):
#             factor_valor = factor.factor
#             # print (factor.factor)
#
#         # print (context)
#         for emp in emp_pool.browse(cr, uid, data['employee_ids'], context=context):
#             slip_data = slip_pool.onchange_employee_id(cr, uid, [], from_date, to_date, emp.id, contract_id=False,
#                                                        context=context)
#             # print (slip_data)
#             id_contrato = slip_data['value'].get('contract_id', False)
#             for contrato in obj_contract.browse(cr, uid, id_contrato):
#                 # print (emp)
#                 # print (contrato.wage)
#                 total_a = contrato.wage * valor
#                 remu_mese_ant = contrato.wage * meses_anteriores
#                 suma_a = total_a + remu_mese_ant  # agregar la suma de gratificaciones  bonificaciones  y participaciones
#                 resto_a = suma_a - deduccion  #(y si corresponde tambien se deduce 3UIT)
#                 # print (resto_a)
#                 # posicionar el resto_a dependiendo a la tabla
#                 tasas_ids = self.pool.get('hr.tasas.x.ejercicio.detalle').search(cr, uid,
#                                                                                    [['tasas_id.ejercicio_fiscal_id.code', '=', anio_fiscal]], context=context)
#                 acumular_impuestos = 0
#                 for tasa in self.pool.get('hr.tasas.x.ejercicio.detalle').browse(cr, uid, tasas_ids):
#                     if resto_a > tasa.valor_minimo:
#                         if acumular_impuestos < tasa.valor_maximo:
#                             acumular_impuestos = acumular_impuestos + tasa.impuesto
#                     if tasa.valor_minimo < resto_a <= tasa.valor_maximo:
#                         queda_a = resto_a - tasa.valor_minimo
#                         # print ('>impuestos queda_a>>' + str(queda_a))
#                         impuesto_a = queda_a * ((tasa.porcentaje / 100) or 0.0)
#                         # print ('>impuestos impuesto_a>>' + str(impuesto_a))
#                         impuesto_total = impuesto_a + acumular_impuestos
#                         # print ('>impuestos impuesto_total>>' + str(impuesto_total))
#                         impuesto_mensual = impuesto_total / factor_valor # falta ver la deduccion por mes
#                         # print ('>impuestos mensual>>' + str(impuesto_mensual))
#
#             # id_p = slip_pool.search(cr, uid, [['payslip_run_id', '=', context['active_id']]], context=context)
#             # print ('ssssssssss',str(id_p))
#             # aaa = line_pool.search(cr, uid, [['employee_id', '=', emp.id], ['contract_id', '=', id_contrato]], context=context)
#             # print (aaa)
#             # print (context['active_id'])
#             # print (slip_data)
#
#         return super(hr_payslip_employees, self).compute_sheet(cr, uid, ids, context=context)