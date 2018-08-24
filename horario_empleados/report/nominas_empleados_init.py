# -*- coding: utf-8 -*-
import time
import xlwt
from openerp.osv import osv
from openerp.report import report_sxw
from datetime import datetime, date, timedelta
from openerp.addons.report_xls.report_xls import report_xls
from openerp.addons.report_xls.utils import rowcol_to_cell, _render
from openerp.osv import orm
from openerp.tools.translate import translate, _
import logging
import calendar
_logger = logging.getLogger(__name__)

_ir_translation_name = 'horario_empleados.report_nominas_empleados_pdf'
# _ir_translation_name = 'horario_empleados.report_liquidacion_empleado_pdf'


class general_nominas_empleados(report_sxw.rml_parse):

    def set_context(self, objects, data, ids, report_type=None):
        # _logger.warn('set_context, objects = %s, data = %s, ids = %s', objects, data, ids)
        super(general_nominas_empleados, self).set_context(objects, data, ids)
        self.quinta_con_vacaciones = 0.0
        if 'basico' in data and 'desde' in data and 'hasta' in data and 'hasta' in data and 'id_emp' in data:
            self.basico = data['basico']
            self.date_from = data['desde']
            self.date_to = data['hasta']
            self.id_emp = data['id_emp']

    def __init__(self, cr, uid, name, context):
        if context is None:
            context = {}
        super(general_nominas_empleados, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'try_parsing_date': self.try_parsing_date,
            '_': self._,
            'get_payslip': self.get_payslip,
            'get_payslip_line_incremento': self.get_payslip_line_incremento,
            'get_payslip_line_deduccion': self.get_payslip_line_deduccion,
            'get_payslip_line_ce': self.get_payslip_line_ce,
            'sum_total': self.sum_total,
            'sum_total_incremento': self.sum_total_incremento,
            'sum_total_ce': self.sum_total_ce,
            'sum_total_total': self.sum_total_total,
            'sum_dias_trabajados': self.sum_dias_trabajados,
            'sum_dias_no_trabajados': self.sum_dias_no_trabajados,
            'sum_permisos': self.sum_permisos,
            'sum_descansos_medicos': self.sum_descansos_medicos,
            'sum_vacaciones': self.sum_vacaciones,
            'direccion_empleado': self.direccion_empleado,
            'neto_empleado': self.neto_empleado,
            'quinta_empleado': self.quinta_empleado,
            'tiempo_entre': self.tiempo_entre,
            'motivo_cese_empleado': self.motivo_cese_empleado,
            'asignacion_empleado': self.asignacion_empleado,
            'extras_empleado2': self.extras_empleado2,
            'probando_empleados': self.probando_empleados,
            'suma_cts_empleado': self.suma_cts_empleado,
            'vacaciones_vencidas': self.vacaciones_vencidas,
            'vacaciones_truncas': self.vacaciones_truncas,
            'vacaciones_pendientes': self.vacaciones_pendientes,
            'quinta_cese_empleado': self.quinta_cese_empleado,
            'sum_total_ingresos_vacaciones': self.sum_total_ingresos_vacaciones,
            'sum_total_descuetos_menos_quinta': self.sum_total_descuetos_menos_quinta,
            'sum_total_liquidacion': self.sum_total_liquidacion,
        })
        self.context = context

    def _(self, src):
        lang = self.context.get('lang', 'en_US')
        return translate(self.cr, _ir_translation_name, 'report', lang, src) or src

    def try_parsing_date(self, text):
        for fmt in ('%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y'):
            try:
                date2 = datetime.strptime(text, fmt)
                return date2.strftime('%d/%m/%Y')
            except ValueError:
                pass
        raise ValueError('no valid date format found')

    def get_payslip(self, cod):
        # ids_hp = self.env['hr.payslip'].search([['payslip_run_id', '=', self.id]])

        # for d in cod:
        sql = """SELECT *,he.name_related as nombre_empleado, he.identification_id as nrodoc, he.otherid as idotro, hp.id as idslip FROM hr_payslip hp LEFT JOIN hr_employee he on hp.employee_id = he.id LEFT JOIN hr_contract hc ON hc.employee_id = he.id LEFT JOIN res_partner_bank rpb on rpb.id = he.bank_account_id
where payslip_run_id = %s or hp.id = %s"""
        self.cr.execute(sql, (cod,cod))
        wizard_data = self.cr.dictfetchall()
        # print (wizard_data)
        return wizard_data

    def get_payslip_solo(self, cod):
        # ids_hp = self.env['hr.payslip'].search([['payslip_run_id', '=', self.id]])
        # print ('>>>>>>>>>>>>>><',str(cod))

        # for d in cod:
        sql = """SELECT *,he.name_related as nombre_empleado, he.identification_id as nrodoc, he.otherid as idotro, hp.id as idslip FROM hr_payslip hp LEFT JOIN hr_employee he on hp.employee_id = he.id LEFT JOIN hr_contract hc ON hc.employee_id = he.id LEFT JOIN res_partner_bank rpb on rpb.id = he.bank_account_id
where hp.id = %s"""
        self.cr.execute(sql, [cod])
        wizard_data = self.cr.dictfetchall()
        # print (wizard_data)
        return wizard_data

    def sum_total_incremento(self):
        return self.regi_total_incremento

    def get_payslip_line_incremento(self, cod_slip):
        # ids_hp = self.env['hr.payslip'].search([['payslip_run_id', '=', self.id]])
        # print ('>>>>>>>>>>>>>><',str(cod_slip))
        # for d in cod:
        sql = """SELECT name, amount, total, quantity, code FROM hr_payslip_line where slip_id = %s AND category_id in ('1','2') ORDER BY sequence"""
        self.cr.execute(sql, [cod_slip])
        wizard_data = self.cr.dictfetchall()
        self.regi_total_incremento = 0.0
        for line in wizard_data:
            self.regi_total_incremento += abs(line['total'])

        # print (wizard_data)
        return wizard_data

    def sum_total(self):
        return self.regi_total

    def sum_advance_salary_total(self):
        return self.advance_salary_holidays

    def get_payslip_line_deduccion(self, cod_slip):
        # ids_hp = self.env['hr.payslip'].search([['payslip_run_id', '=', self.id]])
        # print ('>>>>>>>>>>>>>><',str(cod_slip))
        # for d in cod:
        sql = """SELECT name, amount, total, code, quantity FROM hr_payslip_line where slip_id = %s AND  category_id = '4' ORDER BY sequence"""
        self.cr.execute(sql, [cod_slip])
        wizard_data = self.cr.dictfetchall()
        self.regi_total = 0.0
        self.advance_salary_holidays = 0.0
        self.sumando_menos_quinta = 0.0
        for line in wizard_data:
            self.regi_total += abs(line['total'])
            if line['code'] == 'SAR':
                self.advance_salary_holidays += abs(line['total'])
            if line['code'] != 'R5ta':
                self.sumando_menos_quinta += abs(line['total'])
        return wizard_data

    def sum_total_ce(self):
        return self.regi_total_ce

    def get_payslip_line_ce(self, cod_slip):
        # ids_hp = self.env['hr.payslip'].search([['payslip_run_id', '=', self.id]])
        # print ('>>>>>>>>>>>>>><',str(cod_slip))
        # for d in cod:
        sql = """SELECT name, amount, total FROM hr_payslip_line where slip_id = %s AND  category_id = '8' ORDER BY sequence"""
        self.cr.execute(sql, [cod_slip])
        wizard_data = self.cr.dictfetchall()
        self.regi_total_ce = 0.0
        for line in wizard_data:
            self.regi_total_ce += abs(line['total'])


        sql2 = """SELECT hsr.code as code, hpl.quantity as quantity FROM hr_payslip_line hpl INNER JOIN hr_salary_rule hsr on hpl.salary_rule_id = hsr.id where slip_id = %s and hsr.code in ('PSP','DMM20D','DM20S','VCS','PPP','PS') ORDER BY hpl.sequence"""
        self.cr.execute(sql2, [cod_slip])
        wizard_data_2 = self.cr.dictfetchall()
        self.dias_no_trabajados = 0.0
        self.permisos = 0.0
        self.descansos_medicos = 0.0
        self.vacaciones = 0.0

        for line2 in wizard_data_2:
            if line2['code'] in ('PSP', 'DMM20D', 'DM20S', 'VCS', 'PPP', 'PS'):
                self.dias_no_trabajados += line2['quantity']
            if line2['code'] == 'PSP':
                self.permisos += line2['quantity']
            if line2['code'] == 'PPP':
                self.permisos += line2['quantity']
            if line2['code'] == 'PS':
                self.permisos += line2['quantity']
            if line2['code'] in ('DMM20D', 'DM20S'):
                self.descansos_medicos += line2['quantity']
            if line2['code'] == 'VCS':
                self.vacaciones += line2['quantity']

        return wizard_data

    def sum_total_total(self):
        return self.regi_total_incremento - self.regi_total

    def sum_dias_trabajados(self, mes_fiscal, anio_fiscal):
        # print (mes_fiscal, anio_fiscal)
        dias_del_mes = calendar.monthrange(int(anio_fiscal), int(mes_fiscal))
        # print (dias_del_mes)
        dias_trabajados_total = (int(dias_del_mes[1]) - self.dias_no_trabajados) or 0.0
        return dias_trabajados_total

    def sum_dias_no_trabajados(self):
        return self.dias_no_trabajados

    def sum_permisos(self):
        return self.permisos

    def sum_descansos_medicos(self):
        return self.descansos_medicos

    def sum_vacaciones(self):
        return self.vacaciones

    def probando_empleados(self, f_i, f_f, id_e):
        lng = """select count(i::date) from generate_series(%s, %s, '1 day'::interval) i;"""
        self.cr.execute(lng, (f_i, f_f))
        l = self.cr.fetchone()
        if l:
            l=l[0]
        else:
            l=False


        if l == 28:
            dias = 'name_related text, "1" text, "2" text, "3" text, "4" text, "5" text, "6" text, "7" text, "8" text, "9" text, "10" text, "11" text, "12" text, "13" text, "14" text, "15" text, "16" text, "17" text, "18" text, "19" text, "20" text, "21" text, "22" text, "23" text, "24" text, "25" text, "26" text, "27" text, "28" text'
        elif l == 29:
            dias = 'name_related text, "1" text, "2" text, "3" text, "4" text, "5" text, "6" text, "7" text, "8" text, "9" text, "10" text, "11" text, "12" text, "13" text, "14" text, "15" text, "16" text, "17" text, "18" text, "19" text, "20" text, "21" text, "22" text, "23" text, "24" text, "25" text, "26" text, "27" text, "28" text, "29" text'
        elif l == 30:
            dias = 'name_related text, "1" text, "2" text, "3" text, "4" text, "5" text, "6" text, "7" text, "8" text, "9" text, "10" text, "11" text, "12" text, "13" text, "14" text, "15" text, "16" text, "17" text, "18" text, "19" text, "20" text, "21" text, "22" text, "23" text, "24" text, "25" text, "26" text, "27" text, "28" text, "29" text, "30" text'
        elif l == 31:
            dias = 'name_related text, "1" text, "2" text, "3" text, "4" text, "5" text, "6" text, "7" text, "8" text, "9" text, "10" text, "11" text, "12" text, "13" text, "14" text, "15" text, "16" text, "17" text, "18" text, "19" text, "20" text, "21" text, "22" text, "23" text, "24" text, "25" text, "26" text, "27" text, "28" text, "29" text, "30" text, "31" text'


        sql = """SELECT * FROM crosstab($$ SELECT name_related, fecha, 
(CASE 
    WHEN (cast(hh.date_from as date) <= hda.fecha and hda.fecha <= cast(hh.date_to as date) AND hhs.indicador_ausentismo in ('PPP','PS','PSP')) THEN 'PS'
    WHEN (cast(hh.date_from as date) <= hda.fecha and hda.fecha <= cast(hh.date_to as date) AND hhs.indicador_ausentismo = 'VCS') THEN 'V'
    WHEN (cast(hh.date_from as date) <= hda.fecha and hda.fecha <= cast(hh.date_to as date) AND hhs.indicador_ausentismo = 'DM') THEN 'DM'
    WHEN (cast(hh.date_from as date) <= hda.fecha and hda.fecha <= cast(hh.date_to as date) AND hhs.indicador_ausentismo = 'F') THEN 'FI'
    WHEN (codigo_dias in ('OFF','OO')) THEN 'NT' 
ELSE 'T' 
END) AS codigo_dias 
FROM hr_employee he INNER JOIN horario_asistencias ha ON he.id = ha.employee_id INNER JOIN horario_detalle_asistencias hda ON ha.id = hda.horario_asistencias_id LEFT JOIN hr_holidays hh on (he.id = hh.employee_id AND cast(hh.date_from as date) <= hda.fecha and hda.fecha <= cast(hh.date_to as date) and hh.state = 'validate') LEFT JOIN hr_holidays_status hhs ON hh.holiday_status_id = hhs.id WHERE fecha >= %s and fecha <= %s AND ha.employee_id = %s ORDER BY 1 $$, $$ select i::date from generate_series(%s, %s, '1 day'::interval) i $$) AS ("""+dias+""");"""
        self.cr.execute(sql, (f_i, f_f, id_e, f_i, f_f))
        wizard_data = self.cr.dictfetchall()
        # print (wizard_data)
        return wizard_data

    def salary_advance(self, f_i, f_f, id_e):
        sql = """SELECT * from salary_advance where date BETWEEN %s and %s and employee_id = %s and state = 'approved'"""
        self.cr.execute(sql, (f_i, f_f, id_e))
        wizard_data = self.cr.dictfetchall()
        return wizard_data

    def direccion_empleado(self, dni):
        sql = """SELECT COALESCE(CONCAT(c5.name,' ', hdd.nombre_via,' ', hdd.nro)) as direccion FROM hr_employee he INNER JOIN hr_direccion hd on he.id = hd.direccion_id INNER JOIN hr_direccion_detalle hdd on hd.id = hdd.direccion_or_id INNER JOIN catalogo_tipo_via_5 c5 on hdd.tipo_via = c5.id where he.identification_id = %s and hdd.direco_estado = 'titular'"""
        self.cr.execute(sql, [dni])
        wizard_data = self.cr.fetchone()
        if wizard_data:
            wizard_data = wizard_data[0]
        else:
            wizard_data = False
        return wizard_data

    def neto_empleado(self, id_em):
        sql = """SELECT SUM(hpl.total) as neto from hr_payslip hp INNER JOIN hr_payslip_line hpl on hp.id = hpl.slip_id where hp.employee_id = %s AND date_part('year', hp.date_from) = date_part('year', CURRENT_DATE) and code = 'NET'"""
        self.cr.execute(sql, [id_em])
        wizard_data = self.cr.fetchone()
        if wizard_data:
            wizard_data = wizard_data[0]
        else:
            wizard_data = 0.0
        return wizard_data or 0.0

    def quinta_empleado(self, id_em):
        # print (id_em)
        sql = """SELECT SUM(hpl.total) as quinta from hr_payslip hp INNER JOIN hr_payslip_line hpl on hp.id = hpl.slip_id where hp.employee_id = %s AND date_part('year', hp.date_from) = date_part('year', CURRENT_DATE) and code = 'R5ta'"""
        self.cr.execute(sql, [id_em])
        wizard_data = self.cr.fetchone()
        if wizard_data:
            wizard_data = abs(wizard_data[0])
        else:
            wizard_data = 0.0
        # print (wizard_data)
        return wizard_data or 0.0

    def asignacion_empleado(self, id_em, id_slip):
        sql = """SELECT SUM(hpl.total) as asignacion from hr_payslip hp INNER JOIN hr_payslip_line hpl on hp.id = hpl.slip_id where hp.employee_id = %s AND hp.id = %s and code = 'ASIGNFAMIL'"""
        self.cr.execute(sql, (id_em, id_slip))
        wizard_data = self.cr.fetchone()
        self.asignacion_cts = 0.0
        if wizard_data:
            wizard_data = wizard_data[0]
            self.asignacion_cts = wizard_data
        else:
            wizard_data = 0.0

        return wizard_data or 0.0

    def extras_empleado2(self, id_em, id_slip):
        # print (id_em, id_slip)
        # do = 'HE25%','HE35%','HE100%','HEN25%','HEN35%'
        # print (str(do))
        sql = """SELECT SUM(hpl.total) as extras from hr_payslip hp INNER JOIN hr_payslip_line hpl on hp.id = hpl.slip_id where hp.employee_id = %s AND hp.id = %s and code in (%s,%s,%s,%s,%s,%s)"""
        self.cr.execute(sql, (id_em, id_slip,'HE25%','HE35%','HE100%','HEN25%','HEN35%','BNOC'))
        extras = self.cr.fetchone()
        self.extra_cts = 0.0
        if extras:
            extras = extras[0]
            self.extra_cts = extras
        else:
            extras = 0.0

        return extras or 0.0

    def vacaciones_truncas(self, id_em):
        sql = """SELECT coalesce(sum(hda.dias_truncos),0.0) AS truncos FROM horario_vacaciones_x_empleado ha INNER JOIN horario_detalle_vacaciones hda ON ha.id = hda.detalle_vacaciones_ids WHERE ha.employee_id = %s"""
        self.cr.execute(sql, [id_em])
        truncos = self.cr.fetchone()
        if truncos:
            truncos = truncos[0]
        else:
            truncos = 0.0
        return round(truncos, 2) or 0.0

    def vacaciones_pendientes(self, id_em):
        sql = """SELECT coalesce(sum(hda.dias_pendientes),0.0) AS truncos FROM horario_vacaciones_x_empleado ha INNER JOIN horario_detalle_vacaciones hda ON ha.id = hda.detalle_vacaciones_ids WHERE ha.employee_id = %s"""
        self.cr.execute(sql, [id_em])
        dias_pendientes = self.cr.fetchone()
        if dias_pendientes:
            dias_pendientes = dias_pendientes[0]
        else:
            dias_pendientes = 0.0
        return round(dias_pendientes, 2) or 0.0

    def vacaciones_vencidas(self, id_em):
        sql = """SELECT coalesce(sum(hda.dias_vencidos),0.0) AS truncos FROM horario_vacaciones_x_empleado ha INNER JOIN horario_detalle_vacaciones hda ON ha.id = hda.detalle_vacaciones_ids WHERE ha.employee_id = %s"""
        self.cr.execute(sql, [id_em])
        dias_vencidos = self.cr.fetchone()
        if dias_vencidos:
            dias_vencidos = dias_vencidos[0]
        else:
            dias_vencidos = 0.0
        return round(dias_vencidos, 2) or 0.0

    def suma_cts_empleado(self, basico):
        # print ('fffffffffffffffffff')
        # print (basico)
        # print (self.extra_cts)
        # print (self.asignacion_cts)
        if self.extra_cts and self.extra_cts > 0:
            extra = self.extra_cts
        else:
            extra = 0.0
        if self.asignacion_cts and self.asignacion_cts > 0:
            asignacion_cts = self.asignacion_cts
        else:
            asignacion_cts = 0.0

        return (extra + asignacion_cts + basico) or 0.0

    def motivo_cese_empleado(self, id_em):
        sql = """SELECT cm.name FROM hr_contract hc INNER JOIN hr_contract_periodos hcp on hc.id = hcp.periodo_id INNER JOIN catalogo_motivo_baja_registro_17 cm ON hcp.indicador_motivo_fin = cm.id WHERE hc.employee_id = %s"""
        self.cr.execute(sql, [id_em])
        wizard_data = self.cr.fetchone()
        if wizard_data:
            wizard_data = wizard_data[0]
        else:
            wizard_data = False
        return wizard_data

    def sum_total_ingresos_vacaciones(self):
        basico_30 = self.basico / float(30)
        sumando = (basico_30 * self.vacaciones_truncas(self.id_emp)) + \
                  (basico_30 * self.vacaciones_pendientes(self.id_emp)) + \
                  (basico_30 * self.vacaciones_vencidas(self.id_emp))
        sumado_total = self.sum_total_incremento() + sumando
        return sumado_total

    def sum_total_descuetos_menos_quinta(self):

        sum = float(abs(self.sumando_menos_quinta)) + float(abs(self.quinta_con_vacaciones) or 0.0)
        # sum = 0.0
        # print (sum)
        return sum

    def sum_total_liquidacion(self):
        return (self.sum_total_ingresos_vacaciones() - self.sum_total_descuetos_menos_quinta()) or 0.0

    def quinta_cese_empleado(self, id_emp, f_i, f_f):
        # print (id_emp,f_i, f_f)
        self.quinta_con_vacaciones = 0.0
        rule_obj = self.pool['hr.salary.rule']
        contract_obj = self.pool['hr.contract']
        deduccion_obj = self.pool['hr.deducciones.x.ejercicio']
        valor_obj = self.pool['hr.mes.x.ejercicio.detalle']
        d1 = date(int(f_i[0:4]), int(f_i[5:7]), int(f_i[-2:]))
        d2 = date(int(f_f[0:4]), int(f_f[5:7]), int(f_f[-2:]))
        order_desc = 'date_start DESC'
        contrato_ids = contract_obj.search(self.cr, self.uid, [('employee_id', '=', id_emp)], order=order_desc, limit=1)
        contrato = contract_obj.browse(self.cr, self.uid, contrato_ids)
        # sacar DEDUCCION
        order_ = 'id DESC'
        deducciones_ids2 = deduccion_obj.search(self.cr, self.uid, [], order=order_, limit=1)
        deducciones_ids = deduccion_obj.browse(self.cr, self.uid, deducciones_ids2)
        for deducciones_id in deducciones_ids:
            deduccion = deducciones_id.deducir

            # sacar VALOR
        valor_ids2 = valor_obj.search(self.cr, self.uid, [['mes', '=', int(d1.month)]])
        valor_ids = valor_obj.browse(self.cr, self.uid, valor_ids2)
        for valor_id in valor_ids:
            valor = valor_id.valor
        # print (valor)

        self.cr.execute(
            """SELECT factor from hr_factor_x_ejercicio hf INNER JOIN hr_factor_x_ejercicio_detalle hfd ON hf.id = hfd.factor_id INNER JOIN account_fiscalyear af on hf.ejercicio_fiscal_id = af.id where cast(mes_inicio as int) <= %s and cast(mes_fin as int) >= %s and af.code = %s""",
            (int(d1.month), int(d1.month), str(d1.year)))
        factor_valor = self.cr.fetchone()[0]
        # print (factor_valor)

        obj_emp_anterior = self.pool.get('hr.liquidacion.empresa.anterior')
        id_afs2 = rule_obj.search(self.cr, self.uid,[('code', '=', 'ASIGNFAMIL')])
        id_afs = rule_obj.browse(self.cr, self.uid,id_afs2)
        id_rule2 = rule_obj.search(self.cr, self.uid,[('code', '=', 'R5ta')])
        id_rule = rule_obj.browse(self.cr, self.uid,id_rule2)

        reglas_para_gratificacion2 = rule_obj.search(self.cr, self.uid,[('category_id.code', '=', 'INCREMENTO')])
        reglas_para_gratificacion = rule_obj.browse(self.cr, self.uid, reglas_para_gratificacion2)
        # horas extras y mas
        basico_30 = self.basico / float(30)
        sumando_a_proyeccion = 0.0 + (basico_30 * self.vacaciones_truncas(id_emp)) + (basico_30 * self.vacaciones_pendientes(id_emp)) + (basico_30 * self.vacaciones_vencidas(id_emp))
        for re in reglas_para_gratificacion:
            if re.afectacion_quinta:
                sumando_a_proyeccion += re.amount_fix * float(re.quantity)

        print (sumando_a_proyeccion)
        print ('''fffffffffffffffff''')
        print (self.context)
        print ('''fffffffffffffffff''')
        asignacion_familiar = 0.0
        # quintaaaaaaaaaaaaaaaaa
        if contrato.wage > 2025.10:
            print ('sueldo Basico->', str(contrato.wage))
            id_emp_ant = obj_emp_anterior.search(self.cr, self.uid, [('employee_id', '=', contrato.employee_id.id)])
            empresa_anterior = obj_emp_anterior.browse(self.cr, self.uid, id_emp_ant)
            total_a0 = contrato.wage * valor

            print ('Total remuneraciones proyectadas del periodo', str(total_a0))

            total_a0 = total_a0 + sumando_a_proyeccion

            print ('Total remuneraciones proyectadas del periodo (horas_extra y otros)', str(total_a0))

            asigfam = id_afs
            if asigfam.amount_select in ['fix']:
                asignacion_familiar = asigfam.amount_fix
            elif asigfam.amount_select in ['percentage']:
                asignacion_familiar = (contrato.wage * (asigfam.amount_percentage / 100.0)) or 0.0
            elif asigfam.amount_select in ['code']:
                raise osv.except_osv(_('Error!'),
                                     _(
                                         'Código de python incorrecto definido para la regla de salario %s (%s).') % (
                                         asigfam.name, asigfam.code))
            total_af = asignacion_familiar * valor
            # if total_af > 0 and int(contrato.date_start[-2:]) > 1:
            print ('Sumar Todas las Asignaciones familiares (VALOR)', str(total_af))

            if contrato.grati_julio and contrato.grati_dici:
                gratif = contrato.grati_julio_caja + contrato.grati_dici_caja
            elif contrato.grati_julio and not contrato.grati_dici:
                gratif = contrato.grati_julio_caja
            elif contrato.grati_dici and not contrato.grati_julio:
                gratif = contrato.grati_dici_caja
            else:
                gratif = 0
            self.cr.execute(
                """SELECT count(*) from hr_payslip where employee_id = %s and EXTRACT(MONTH FROM date_from) < %s AND date_part('year', date_from) = date_part('year', CURRENT_DATE)""",
                (contrato.employee_id.id, int(f_f[5:7])))
            meses_anteriores = self.cr.fetchone()[0]

            remu_mese_ant = contrato.wage * meses_anteriores
            asig_anteriores = asignacion_familiar * meses_anteriores

            # empresa anterior
            if empresa_anterior:
                if int(contrato.date_start[0:4]) == empresa_anterior.code and not empresa_anterior.liquidacion_anterior:
                    remu_mese_ant += empresa_anterior.monto_total_liquidacion + contrato.wage + asignacion_familiar
                    # asig_anteriores = total_af

            if int(contrato.date_start[5:7]) in [2, 3, 4, 5, 6, 7]:
                if contrato.calculo_gratificacion:
                    d1 = date(int(contrato.date_start[0:4]), int(contrato.date_start[5:7]),
                              int(contrato.date_start[-2:]))
                    enero = date(int(contrato.date_start[0:4]), int(1), int(1))
                    d2 = date(int(contrato.date_start[0:4]), int(6), int(30))
                    dias_enero_junio = d2 - enero
                    dias_enero_junio = (int(str(dias_enero_junio).split(' ', 1)[0]) + 1)
                    dias_trabajados_fin_anio = d2 - d1
                    dias_trabajados_fin_anio = (int(str(dias_trabajados_fin_anio).split(' ', 1)[0]) + 1)
                else:
                    mes_1 = (int(contrato.date_start[5:7]) - 1) * 30
                    dia_1 = (int(contrato.date_start[-2:]) - 1)
                    dias_enero_junio = 6 * 30
                    dias_trabajados_fin_anio = abs((abs(dias_enero_junio - mes_1)) - dia_1)

                print ('dias enero junio', str(dias_enero_junio))
                print ('dias trabajados hasta junio', str(dias_trabajados_fin_anio))
                gratif = (contrato.grati_julio_caja / dias_enero_junio) or 0.0

                gratif = (gratif * dias_trabajados_fin_anio) + contrato.grati_dici_caja

            elif int(contrato.date_start[5:7]) in [8, 9, 10, 11, 12]:
                # if int(payslip.date_from[5:7]) == 12 and not empresa_anterior.liquidacion_anterior:
                if contrato.calculo_gratificacion:
                    d1 = date(int(contrato.date_start[0:4]), int(contrato.date_start[5:7]),
                              int(contrato.date_start[-2:]))
                    julio = date(int(contrato.date_start[0:4]), int(7), int(1))
                    d2 = date(int(contrato.date_start[0:4]), int(12), int(31))
                    dias_julio_diciembre = d2 - julio
                    dias_julio_diciembre = (int(str(dias_julio_diciembre).split(' ', 1)[0]) + 1)
                    dias_trabajados_fin_anio = d2 - d1
                    dias_trabajados_fin_anio = (int(str(dias_trabajados_fin_anio).split(' ', 1)[0]) + 1)
                else:
                    mes_1 = (abs(int(contrato.date_start[5:7]) - int(12)) * 30) + 30
                    dia_1 = (int(contrato.date_start[-2:]) - 1)
                    dias_julio_diciembre = 6 * 30
                    dias_trabajados_fin_anio = abs(mes_1 - dia_1)

                print ('dias julio diciembre', str(dias_julio_diciembre))
                print ('dias trabajados hasta diciembre', str(dias_trabajados_fin_anio))
                gratif = (contrato.grati_dici_caja / dias_julio_diciembre) or 0.0
                gratif = gratif * dias_trabajados_fin_anio

            print ('mese anterirores', str(remu_mese_ant))
            print ('asig_anteriores anterirores', str(asig_anteriores))

            print ('Total gratificaciones', str(gratif))
            total_a = total_a0 + gratif + total_af
            print ('Total ingreso anual proyectado', str(total_a))
            # raise Warning('dddddddddddddddddd')
            if remu_mese_ant > 0 and not empresa_anterior:
                suma_a = total_a + remu_mese_ant + asig_anteriores  # agregar la suma de gratificaciones  bonificaciones  y participaciones
                # print (suma_a)
            elif remu_mese_ant > 0 and empresa_anterior:
                suma_a = total_a + remu_mese_ant + asig_anteriores
            else:
                suma_a = total_a
            print ('Total ingreso anual proyectado + meses anteriores', str(suma_a))
            print (suma_a, deduccion)
            resto_a = suma_a - deduccion  # (y si corresponde tambien se deduce 3UIT)
            print ("Renta Neta anual proyectada", str(resto_a))
            # posicionar el resto_a dependiendo a la tabla
            tasas_ids = self.pool('hr.tasas.x.ejercicio.detalle').search(self.cr, self.uid, [
                ['tasas_id.ejercicio_fiscal_id.code', '=', str(d1.year)]])
            print (tasas_ids)

            # print (anio_fiscal)
            acumular_impuestos = 0
            # raise Warning('dfdfdfdfdf')
            for tasa in self.pool('hr.tasas.x.ejercicio.detalle').browse(self.cr, self.uid, tasas_ids):
                # print ("Tasasssssssssssssssssss", str(resto_a))
                if resto_a > tasa.valor_maximo:
                    print ('Entreee  tasas mayorrrr')
                    # if acumular_impuestos < tasa.valor_maximo:
                    acumular_impuestos = acumular_impuestos + tasa.impuesto
                if tasa.valor_minimo < resto_a <= tasa.valor_maximo:
                    # acumular_impuestos = acumular_impuestos + tasa.impuesto
                    print ('Entreee  tasas menor')
                    print (resto_a, tasa.valor_minimo)
                    queda_a = resto_a - tasa.valor_minimo
                    print ('>impuestos queda_a>>' + str(queda_a))
                    impuesto_a = queda_a * ((tasa.porcentaje / 100) or 0.0)
                    print ('>impuestos impuesto_a>>' + str(impuesto_a))
                    impuesto_total = impuesto_a + acumular_impuestos
                    print ('>impuestos impuesto_total>>' + str(impuesto_total))
                    if empresa_anterior:
                        impuesto_total = abs(
                            impuesto_total - empresa_anterior.monto_descuento_quinta)  # agregar la su
                    print ('>impuestos impuesto_total22222>>' + str(impuesto_total))
                    # print (factor_valor)
                    # impuesto_mensual = 0.0
                    if factor_valor == 12.0:
                        impuesto_mensual = -(impuesto_total / factor_valor)  # falta ver la deduccion por mes
                    elif factor_valor == 9.0:
                        self.cr.execute("""SELECT SUM(amount) as monto FROM hr_payslip hp INNER JOIN hr_payslip_line hpl
                        ON hp.id = hpl.slip_id WHERE hp.employee_id = %s AND code='R5ta' AND substring(to_char(date_from,'YYYY-MM-DD') from 1 for 4) = %s AND substring(to_char(date_from,'YYYY-MM-DD') from 6 for 2) in ('01','02','03')""",
                                         (contrato.employee_id.id, str(d1.year)))
                        rentas_anteriores = self.cr.fetchone()
                        if rentas_anteriores:
                            rentas_anteriores = rentas_anteriores[0]
                        else:
                            rentas_anteriores = False

                        ant_impuesto_mensual = impuesto_total + (rentas_anteriores or 0.0)
                        print (ant_impuesto_mensual)
                        impuesto_mensual = -(ant_impuesto_mensual / factor_valor)
                        print (impuesto_mensual)
                    elif factor_valor == 8.0:
                        self.cr.execute("""SELECT SUM(amount) as monto FROM hr_payslip hp INNER JOIN hr_payslip_line hpl
                        ON hp.id = hpl.slip_id WHERE hp.employee_id = %s AND code='R5ta' AND substring(to_char(date_from,'YYYY-MM-DD') from 1 for 4) = %s AND substring(to_char(date_from,'YYYY-MM-DD') from 6 for 2) in ('01','02','03','04')""",
                                         (contrato.employee_id.id, str(d1.year)))
                        rentas_anteriores = self.cr.fetchone()
                        if rentas_anteriores:
                            rentas_anteriores = rentas_anteriores[0]
                        else:
                            rentas_anteriores = False

                        ant_impuesto_mensual = impuesto_total + (rentas_anteriores or 0.0)
                        impuesto_mensual = -(ant_impuesto_mensual / factor_valor)
                    elif factor_valor == 5.0:
                        self.cr.execute("""SELECT SUM(amount) as monto FROM hr_payslip hp INNER JOIN hr_payslip_line hpl
                        ON hp.id = hpl.slip_id WHERE hp.employee_id = %s AND code='R5ta' AND substring(to_char(date_from,'YYYY-MM-DD') from 1 for 4) = %s AND substring(to_char(date_from,'YYYY-MM-DD') from 6 for 2) in ('01','02','03','04','05','06','07')""",
                                         (contrato.employee_id.id, str(d1.year)))
                        rentas_anteriores = self.cr.fetchone()
                        if rentas_anteriores:
                            rentas_anteriores = rentas_anteriores[0]
                        else:
                            rentas_anteriores = False

                        ant_impuesto_mensual = impuesto_total + (rentas_anteriores or 0.0)
                        impuesto_mensual = -(ant_impuesto_mensual / factor_valor)
                    elif factor_valor == 4.0:
                        self.cr.execute("""SELECT SUM(amount) as monto FROM hr_payslip hp INNER JOIN hr_payslip_line hpl
                        ON hp.id = hpl.slip_id WHERE hp.employee_id = %s AND code='R5ta' AND substring(to_char(date_from,'YYYY-MM-DD') from 1 for 4) = %s AND substring(to_char(date_from,'YYYY-MM-DD') from 6 for 2) in ('01','02','03','04','05','06','07','08')""",
                                         (contrato.employee_id.id, str(d1.year)))
                        rentas_anteriores = self.cr.fetchone()
                        if rentas_anteriores:
                            rentas_anteriores = rentas_anteriores[0]
                        else:
                            rentas_anteriores = False

                        ant_impuesto_mensual = impuesto_total + (rentas_anteriores or 0.0)
                        impuesto_mensual = -(ant_impuesto_mensual / factor_valor)
                    elif factor_valor == 0.0:
                        self.cr.execute("""SELECT SUM(amount) as monto FROM hr_payslip hp INNER JOIN hr_payslip_line hpl
                        ON hp.id = hpl.slip_id WHERE hp.employee_id = %s AND code='R5ta' AND substring(to_char(date_from,'YYYY-MM-DD') from 1 for 4) = %s AND substring(to_char(date_from,'YYYY-MM-DD') from 6 for 2) in ('01','02','03','04','05','06','07','08','09','10','11')""",
                                         (contrato.employee_id.id, str(d1.year)))
                        rentas_anteriores = self.cr.fetchone()
                        if rentas_anteriores:
                            rentas_anteriores = rentas_anteriores[0]
                        else:
                            rentas_anteriores = False

                        ant_impuesto_mensual = impuesto_total + (rentas_anteriores or 0.0)
                        impuesto_mensual = -(ant_impuesto_mensual)
                        if empresa_anterior:
                            if int(contrato.date_from[5:7]) == 12 \
                                    and int(contrato.date_start[0:4]) == empresa_anterior.code \
                                    and not empresa_anterior.liquidacion_anterior:
                                print ('Empresa anterior cerrdaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
                                pass
                                # empresa_anterior.write({'liquidacion_anterior': True})
                    else:
                        impuesto_mensual = 0.0

                    import decimal
                    impuesto_mensual2 = decimal.Decimal(impuesto_mensual).quantize(decimal.Decimal('.01'),
                                                                                   rounding=decimal.ROUND_DOWN)
                    print ('>impuestos mensual>>' + str(impuesto_mensual2))
                    self.quinta_con_vacaciones = impuesto_mensual2
                    return impuesto_mensual2

        else:
            print ('>impuestojjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjs mensual>>')
            self.quinta_con_vacaciones = 0.0
            return 0.0

    def tiempo_entre(self, d1, m1, y1, d2, m2, y2):
        print (d1, m1, y1, d2, m2, y2)
        'Devuelve los días, meses y años transcurridos entre las dos fechas pasadas como argumento.'
        if not es_fecha(d1, m1, y1) or not es_fecha(d2, m2, y2):
            print 'ERROR: Una de las fechas ingresadas no es válida.'
            return

        # print '#0 %d/%d: %d' % (m1, y1, dias_mes(m1, y1))

        yf, mp = 0, 0
        for h in range(m1 + 1, 13):
            mp += 1
        # print '#%d %d/%d: %d' % (mp, h, y1, dias_mes(h, y1))
        for i in range(1, y2 - y1):
            yf += 1
            for j in range(1, 13):
                mp += 1
                # print '#%d %d/%d: %d' % (mp, j, y1 + i, dias_mes(j, y1 + i))
        for k in range(1, m2):
            mp += 1
        # print '#%d %d/%d: %d' % (mp, k, y2, dias_mes(k, y2))

        # print '#%d %d/%d: %d' % (mp + 1, m2, y2, dias_mes(m2, y2))

        mf = mp % 12
        df = fin_mes(d1, m1, y1) + d2 - 1
        if df > dias_mes(m1, y1):
            df -= dias_mes(m1, y1) - 1
            mf += 1

        ys = '' if yf == 1 else 's'
        ms = '' if mf == 1 else 'es'
        ds = '' if df == 1 else 's'

        return '%d año%s, %d mes%s y %d día%s.' % (yf, ys, mf, ms, df, ds)


def es_bisiesto(y):
    'Devuelve un valor lógico indicando si el año pasado como argumento es bisiesto.'
    return y % 4 == 0 and y % 100 != 0 or y % 400 == 0


def dias_mes(m, y):
    'Devuelve la cantidad de días que tiene un mes (m), según el año en que se encuentre (y).'
    if m == 2: return 29 if es_bisiesto(y) else 28
    return 30 if m in [4, 6, 9, 11] else 31


def es_fecha(d, m, y):
    'Devuelve un valor lógico indicando si la fecha pasada como argumento es válida.'
    return not (d < 1 or d > dias_mes(m, y) or m < 1 or m > 12 or y < 1)


def fin_mes(d, m, y):
    'Dada una fecha, devuelve los días que faltan para fin de mes.'
    dif = dias_mes(m, y) - d
    return dif


def fin_anio(d, m, y):
    'Dada una fecha, devuelve los días que faltan para fin de año.'
    dif = 365 - dias_transcurridos(d, m, y)
    if es_bisiesto(y): dif += 1
    return dif


def dias_transcurridos(d, m, y):
    'Devuelve los días transcurridos desde principio de año hasta el día de la fecha pasada como argumento.'
    dias = 0
    for i in range(1, m): dias += dias_mes(i, y)
    dias += d
    return dias



class report_factura_diario(osv.AbstractModel):
    _name = 'report.horario_empleados.report_nominas_empleados_pdf'
    _inherit = 'report.abstract_report'
    _template = 'horario_empleados.report_nominas_empleados_pdf'
    _wrapped_report_class = general_nominas_empleados

class report_liquidacion_empleado(osv.AbstractModel):
    _name = 'report.horario_empleados.report_liquidacion_empleado_pdf'
    _inherit = 'report.abstract_report'
    _template = 'horario_empleados.report_liquidacion_empleado_pdf'
    _wrapped_report_class = general_nominas_empleados




# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
