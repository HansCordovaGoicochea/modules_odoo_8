# -*- coding: utf-8 -*-
from datetime import datetime, date, timedelta
import calendar
from openerp import models, fields, api, _
from openerp.osv import osv
from openerp.exceptions import Warning

from dateutil.relativedelta import relativedelta


DATETIME_FORMAT = "%Y-%m-%d"


class AdvanceSalaryHolidays(models.Model):
    _name = "advance.holidays"

    def _get_reason(self):
        ids = self.env['advance.razon'].search([('code', '=', 'ADV')])
        if ids:
            return ids[0]
        return False

    name = fields.Char('Nombre', required=True)
    state = fields.Selection([
                ('draft', 'Borrador'),
                ('approved', 'Pagado'),
                ('cancel', 'Cancelar')], 'Estado', copy=False, default='draft')
    date_start = fields.Date('Fecha Desde', required=True)
    date_end = fields.Date('Fecha Hasta', required=True)
    journal_id = fields.Many2one('account.journal', 'Metodo de Pago', required=True)

    reason = fields.Many2one('advance.razon', string='Razón', required=True, default=_get_reason)

    advance_holidays_ids = fields.One2many('salary.advance', 'advance_holidays_id', 'Adelanto de Sueldo para Vacaciones')

    @api.onchange('journal_id')
    def onchange_journal_id(self):
        if self.journal_id:
            if not self.journal_id.default_debit_account_id or not self.journal_id.default_credit_account_id:
                raise osv.except_osv(_('Error!'), _('Porfavor Configure las cuentas del metodo de pago!.'))

    @api.onchange('date_start')
    def onchange_date_start(self):
        if self.date_start and not self.date_end:
            date_to_with_delta = datetime.strptime(self.date_start, DATETIME_FORMAT) + relativedelta(months=1, days=-1)
            self.date_end = str(date_to_with_delta)

        if (self.date_start and self.date_end) and (self.date_start > self.date_end):
            raise osv.except_osv(_('Error!'), _('La fecha de inicio no puede ser mayor que la fecha de fin.'))


    @api.onchange('date_end')
    def onchange_date_end(self):
        if (self.date_start and self.date_end) and (self.date_start > self.date_end):
            raise osv.except_osv(_('Error!'), _('La fecha de inicio no puede ser mayor que la fecha de fin.'))

    @api.multi
    def compute_holidays(self):
        print('calculandooooo!!!!!!!!')
        if self.journal_id:
            if not self.journal_id.default_debit_account_id or not self.journal_id.default_credit_account_id:
                raise osv.except_osv(_('Error!'), _('Porfavor Configure las cuentas del metodo de pago!.'))

        start = datetime.strptime(self.date_start, "%Y-%m-%d") - relativedelta(month=1)
        end = datetime.strptime(self.date_end, "%Y-%m-%d") + timedelta(days=7)

        ids_holidays = self.env['hr.holidays'].search((['date_from', '>=', str(start)],
                                                       ['date_from', '<=', str(end)],
                                                       ['paid', '=', False],
                                                       ['state', '=', 'validate'],
                                                       ['holiday_status_id.indicador_ausentismo', '=', 'VCS']))
        # print (ids_holidays)
        # line_sav = []
        if ids_holidays:
            for line in ids_holidays:
                order_desc = 'date_start DESC'
                ids_contract = self.env['hr.contract'].search([['employee_id', '=', line.employee_id.id]], order=order_desc, limit=1)
                d1 = date(int(line.date_from[0:4]), int(line.date_from[5:7]), int(line.date_from[8:10]))
                d2 = date(int(line.date_to[0:4]), int(line.date_to[5:7]), int(line.date_to[8:10]))
                # dias_del_mes = d2 - d1
                # dias_del_mes = (int(str(dias_del_mes).split(' ', 1)[0]) + 1)
                dias_del_mes = calendar.monthrange(d1.year, d1.month)

                # Decuento de quinta ######
                    # sacar UIT
                order_ = 'id DESC'
                uit_ids = self.env['hr.uit.sunat'].search([], order=order_, limit=1)
                for uit_id in uit_ids:
                    uit = uit_id.valor_uit

                    # sacar DEDUCCION
                deducciones_ids = self.env['hr.deducciones.x.ejercicio'].search([], order=order_, limit=1)
                for deducciones_id in deducciones_ids:
                    deduccion = deducciones_id.deducir

                    # sacar VALOR
                valor_ids = self.env['hr.mes.x.ejercicio.detalle'].search([['mes', '=', int(d1.month)]])
                for valor_id in valor_ids:
                    valor = valor_id.valor
                    # print (valor_id.valor)

                self._cr.execute("""SELECT factor from hr_factor_x_ejercicio hf INNER JOIN hr_factor_x_ejercicio_detalle hfd ON hf.id = hfd.factor_id INNER JOIN account_fiscalyear af on hf.ejercicio_fiscal_id = af.id where cast(mes_inicio as int) <= %s and cast(mes_fin as int) >= %s and af.code = %s""",(int(d1.month), int(d1.month), str(d1.year)))
                factor_valor = self._cr.fetchone()[0]
                # print (factor_valor)

                rule_obj = self.env['hr.salary.rule']
                id_rule = rule_obj.search([['code', '=', 'R5ta']])
                id_afs = rule_obj.search([['code', '=', 'ASIGNFAMIL']])
                id_bnoct = rule_obj.search([['code', '=', 'BNOC']])
                id_rule.write({'amount_fix': 0})

                contrato = ids_contract
                # extrassssssssssssssssssss
                sueldo = contrato.wage

                sueldo_por_hora = sueldo / float(240)
                """BONO NOCTURNO"""
                if contrato.horario_nocturno:
                    self._cr.execute(
                        """SELECT coalesce(sum((CASE WHEN (segunda_hora_entrada > 22) THEN (24 - segunda_hora_entrada) + segunda_hora_salida ELSE (2) + segunda_hora_salida END)),0.0) AS horas_noctunas FROM horario_asistencias ha INNER JOIN horario_detalle_asistencias hda ON ha.id = hda.horario_asistencias_id WHERE fecha >= %s and fecha <= %s and ha.employee_id = %s and codigo_dias = 'NAA01'""",
                        (self.date_start, self.date_end, contrato.employee_id.id))
                    horas_noctunas = self._cr.fetchone()
                    if horas_noctunas:
                        horas_noctunas = horas_noctunas[0]
                    else:
                        horas_noctunas = 0.0

                    bono_nocturno = horas_noctunas * sueldo_por_hora
                    id_bnoct.write({'quantity': str(horas_noctunas), 'amount_fix': sueldo_por_hora})
                else:
                    id_bnoct.write({'quantity': '0', 'amount_fix': 0})

                """TIEMPO EN ESPERA"""
                self._cr.execute("SELECT hora_inicio FROM horas_extra WHERE employee_id = %s AND motivo=5 AND estado_pag=False AND fecha BETWEEN %s AND %s and concepto = 'pago'",
                                 (contrato.employee_id.id, self.date_start, self.date_end))

                hora_inicio = self._cr.fetchone()
                if hora_inicio:
                    hora_inicio = hora_inicio[0]
                else:
                    hora_inicio = False

                feriados = self.pool.get('modulo_valorizaciones.feriados').search(self._cr, self._uid,[])
                if not hora_inicio:
                    id_rule_extras = rule_obj.search([['code', 'in', ('HE100%', 'HE25%', 'HE35%', 'HEN25%', 'HEN25%', 'HEN35%')]])
                    id_rule_extras.write({'quantity': '0', 'amount_fix': 0})

                """TIEMPO EN ESPERA"""
                self._cr.execute(
                    "SELECT COALESCE(SUM(horas), 0) AS ho, fecha, hora_inicio_diurno, hora_fin_diurno, hora_inicio_nocturno, hora_fin_nocturno  FROM horas_extra WHERE employee_id = %s AND motivo=5 AND estado_pag=False AND fecha BETWEEN %s AND %s and concepto = 'pago' GROUP BY fecha, hora_inicio_diurno, hora_fin_diurno, hora_inicio_nocturno, hora_fin_nocturno", (contrato.employee_id.id,  self.date_start, self.date_end))
                g_ho_extra = self._cr.dictfetchall()

                h_e_al100 = 0
                horas_al100 = 0
                porc_25_2_100 = 0
                for fechas in g_ho_extra:
                    for feriado in self.pool.get('modulo_valorizaciones.feriados').browse(self._cr, self._uid, feriados):
                        f = feriado.fecha
                        if fechas['fecha'] == f:
                            # print('feriado', str(fechas['ho']))
                            porc_25_1 = contrato.wage / float(240)
                            porc_25_2_100 = porc_25_1 * 1
                            h_feriado = fechas['ho'] * porc_25_2_100
                            # print ('>>>feriado>>>', str(h_feriado))
                            h_e_al100 = h_feriado + h_e_al100
                            horas_al100 = horas_al100 + fechas['ho']

                    if fechas['hora_inicio_diurno'] == 0 and fechas['hora_fin_diurno'] == 0 and fechas[
                        'hora_inicio_nocturno'] == 0 and fechas['hora_fin_nocturno'] == 0:
                        # print('descanso',str(fechas['ho']))
                        porc_25_1 = contrato.wage / float(240)
                        porc_25_2_100 = porc_25_1 * 1
                        h_descanso = fechas['ho'] * porc_25_2_100
                        h_e_al100 = h_descanso + h_e_al100
                        # print ('>>>Descanso>>>', str(h_descanso))
                        horas_al100 = horas_al100 + fechas['ho']

                    id_rule_extras_100 = rule_obj.search([['code', '=', ('HE100%')]])
                    id_rule_extras_100.write({'quantity': str(horas_al100), 'amount_fix': porc_25_2_100})

                """TIEMPO EN ESPERA """
                self._cr.execute(
                    "SELECT COALESCE(SUM(horas), 0) AS ho, fecha FROM horas_extra WHERE employee_id = %s AND motivo=5 AND estado_pag=False AND fecha BETWEEN %s AND %s and concepto = 'pago' GROUP BY fecha ORDER BY fecha",
                    (contrato.employee_id.id,  self.date_start, self.date_end))
                g_ho_esperas = self._cr.dictfetchall()
                punto = 1
                horas_al_25 = 0
                horas_al_35 = 0
                horas_al_N35 = 0
                horas_al_N45 = 0

                importe_al_25 = 0.0
                importe_al_35 = 0.0
                importe_al_N35 = 0.0
                importe_al_N45 = 0.0

                for g_ho in g_ho_esperas:
                    g_ho_espera11 = g_ho['ho']
                    g_ho_espera = g_ho['ho']
                    fecha = g_ho['fecha']
                    while g_ho_espera > 0:
                        if hora_inicio:
                            if hora_inicio < 22.0:
                                if 2.0 > g_ho_espera == g_ho_espera11:
                                    porc_25_1 = contrato.wage / float(240)
                                    porc_25_2 = porc_25_1 * 0.25
                                    porc_25_3 = 2 * porc_25_2
                                    importe_al_25 = porc_25_3
                                    horas_al_25 = horas_al_25 + g_ho_espera

                                elif 2.0 <= g_ho_espera == g_ho_espera11:
                                    porc_25_1 = contrato.wage / float(240)
                                    porc_25_2 = porc_25_1 * 0.25
                                    porc_25_3 = 2 * porc_25_2
                                    importe_al_25 = porc_25_3
                                    horas_al_25 = horas_al_25 + 2

                                elif g_ho_espera > 0:
                                    porc_35_1 = contrato.wage / float(240)
                                    porc_35_2 = porc_35_1 * 0.35
                                    porc_35_3 = g_ho_espera * porc_35_2
                                    importe_al_35 = porc_35_3
                                    horas_al_35 = horas_al_35 + g_ho_espera

                                    break
                                g_ho_espera = g_ho_espera - 2
                                punto = punto - 1
                            else:
                                if 2.0 > g_ho_espera == g_ho_espera11:
                                    porc_35_1 = contrato.wage / float(240)
                                    porc_35_2 = porc_35_1 * 0.35
                                    porc_35_3 = g_ho_espera * porc_35_2
                                    importe_al_N35 = porc_35_3
                                    horas_al_N35 = horas_al_N35 + g_ho_espera

                                elif 2.0 <= g_ho_espera == g_ho_espera11:
                                    porc_35_1 = contrato.wage / float(240)
                                    porc_35_2 = porc_35_1 * 0.35
                                    porc_35_3 = g_ho_espera * porc_35_2
                                    importe_al_N35 = porc_35_3
                                    horas_al_N35 = horas_al_N35 + g_ho_espera

                                elif g_ho_espera > 0:
                                    porc_45_1 = contrato.wage / float(240)
                                    porc_45_2 = porc_45_1 * 0.35
                                    porc_45_3 = g_ho_espera * porc_45_2
                                    importe_al_N45 = porc_45_3
                                    horas_al_N45 = horas_al_N45 + g_ho_espera

                                    break
                                g_ho_espera = g_ho_espera - 2

                            id_rule_extras_25 = rule_obj.search([['code', '=', ('HE25%')]])
                            id_rule_extras_25.write({'quantity': str(horas_al_25), 'amount_fix': importe_al_25})

                            id_rule_extras_35 = rule_obj.search([['code', '=', ('HE35%')]])
                            id_rule_extras_35.write({'quantity': str(horas_al_35), 'amount_fix': importe_al_35})

                            id_rule_extras_N35 = rule_obj.search([['code', '=', ('HEN25%')]])
                            id_rule_extras_N35.write({'quantity': str(horas_al_N35), 'amount_fix': importe_al_N35})

                            id_rule_extras_N45 = rule_obj.search([['code', '=', ('HEN35%')]])
                            id_rule_extras_N45.write({'quantity': str(horas_al_N45), 'amount_fix': importe_al_N45})

                        else:
                            id_rule_extras2 = rule_obj.search([['code', 'in', ('HE100%', 'HE25%', 'HE35%', 'HEN25%', 'HEN35%')]])
                            id_rule_extras2.write({'quantity': '0', 'amount_fix': 0},)

                reglas_para_gratificacion = rule_obj.search([('category_id.code', '=', 'INCREMENTO')])

                # horas extras y mas
                sumando_a_proyeccion = 0.0
                for re in reglas_para_gratificacion:
                    if re.afectacion_quinta:
                        sumando_a_proyeccion += re.amount_fix * float(re.quantity)

                print (sumando_a_proyeccion)

                obj_emp_anterior = self.pool.get('hr.liquidacion.empresa.anterior')
                id_afs = rule_obj.search([('code', '=', 'ASIGNFAMIL')])
                id_rule = rule_obj.search([('code', '=', 'R5ta')])

                asignacion_familiar = 0.0
                # quintaaaaaaaaaaaaaaaaa

                print ('sueldo Basico->', str(contrato.wage))
                id_emp_ant = obj_emp_anterior.search(self._cr, self._uid, [('employee_id', '=', contrato.employee_id.id)])
                empresa_anterior = obj_emp_anterior.browse(self._cr, self._uid, id_emp_ant)
                total_a0 = contrato.wage * valor

                print ('Total remuneraciones proyectadas del periodo', str(total_a0))

                total_a0 = total_a0 + sumando_a_proyeccion

                print ('Total remuneraciones proyectadas del periodo (horas_extra y otros)', str(total_a0))

                asigfam = id_afs
                if contrato.employee_id.children > 0:
                    if asigfam.amount_select in ['fix']:
                        asignacion_familiar = asigfam.amount_fix
                    elif asigfam.amount_select in ['percentage']:
                        asignacion_familiar = (contrato.wage * (asigfam.amount_percentage / 100.0)) or 0.0
                    elif asigfam.amount_select in ['code']:
                        raise osv.except_osv(_('Error!'),
                                             _('Código de python incorrecto definido para la regla de salario %s (%s).') % (asigfam.name, asigfam.code))
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
                self._cr.execute(
                    """SELECT count(*) from hr_payslip where employee_id = %s and EXTRACT(MONTH FROM date_from) < %s AND date_part('year', date_from) = date_part('year', CURRENT_DATE)""",
                    (contrato.employee_id.id, int(self.date_start[5:7])))
                meses_anteriores = self._cr.fetchone()[0]

                remu_mese_ant = sueldo * meses_anteriores
                asig_anteriores = asignacion_familiar * meses_anteriores
                print ('sueldo * meses_anteriores', str(remu_mese_ant))

                # empresa anterior
                print('dddddddddddddddddddddddddddddddddddddddddddd')
                print (empresa_anterior)
                if empresa_anterior and empresa_anterior.monto_total_liquidacion > 0:
                    if int(contrato.date_start[0:4]) == empresa_anterior.code and not empresa_anterior.liquidacion_anterior:
                        remu_mese_ant += empresa_anterior.monto_total_liquidacion
                        print (remu_mese_ant)

                # falta aaaaaaaaaaaaaaaaaaaa

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
                    suma_a = total_a + remu_mese_ant
                else:
                    suma_a = total_a
                print ('Total ingreso anual proyectado + meses anteriores', str(suma_a))
                print (suma_a, deduccion)
                resto_a = suma_a - deduccion  # (y si corresponde tambien se deduce 3UIT)
                print ("Renta Neta anual proyectada", str(resto_a))
                if resto_a <= 0:
                    print ('fgfgfg')
                    id_rule.write({'amount_fix': 0})
                    # rule_obj.write(cr, uid, id_rule, {'amount_fix': 0}, context=context)
                else:
                    # posicionar el resto_a dependiendo a la tabla
                    tasas_ids = self.pool.get('hr.tasas.x.ejercicio.detalle').search(self._cr, self._uid, [
                        ['tasas_id.ejercicio_fiscal_id.code', '=', str(d1.year)]])
                    # print (tasas_ids)
                    # print (anio_fiscal)
                    acumular_impuestos = 0
                    # raise Warning('dfdfdfdfdf')
                    for tasa in self.pool.get('hr.tasas.x.ejercicio.detalle').browse(self._cr, self._uid, tasas_ids):
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
                                if int(self.date_start[0:4]) == empresa_anterior.code and not empresa_anterior.liquidacion_anterior:
                                    impuesto_total = abs(impuesto_total - empresa_anterior.monto_descuento_quinta)  # agregar la su
                            print ('>impuestos impuesto_total22222>>' + str(impuesto_total))
                            # print (factor_valor)
                            # impuesto_mensual = 0.0
                            if factor_valor == 12.0:
                                impuesto_mensual = -(impuesto_total / factor_valor)  # falta ver la deduccion por mes
                            elif factor_valor == 9.0:
                                self._cr.execute("""SELECT SUM(amount) as monto FROM hr_payslip hp INNER JOIN hr_payslip_line hpl
                ON hp.id = hpl.slip_id WHERE hp.employee_id = %s AND code='R5ta' AND substring(to_char(date_from,'YYYY-MM-DD') from 1 for 4) = %s AND substring(to_char(date_from,'YYYY-MM-DD') from 6 for 2) in ('01','02','03')""",(contrato.employee_id.id, str(d1.year)))
                                rentas_anteriores = self._cr.fetchone()
                                if rentas_anteriores:
                                    rentas_anteriores = rentas_anteriores[0]
                                else:
                                    rentas_anteriores = False

                                ant_impuesto_mensual = impuesto_total + (rentas_anteriores or 0.0)
                                print (ant_impuesto_mensual)
                                impuesto_mensual = -(ant_impuesto_mensual / factor_valor)
                                print (impuesto_mensual)
                            elif factor_valor == 8.0:
                                self._cr.execute("""SELECT SUM(amount) as monto FROM hr_payslip hp INNER JOIN hr_payslip_line hpl
                ON hp.id = hpl.slip_id WHERE hp.employee_id = %s AND code='R5ta' AND substring(to_char(date_from,'YYYY-MM-DD') from 1 for 4) = %s AND substring(to_char(date_from,'YYYY-MM-DD') from 6 for 2) in ('01','02','03','04')""",
                                           (contrato.employee_id.id, str(d1.year)))
                                rentas_anteriores = self._cr.fetchone()
                                if rentas_anteriores:
                                    rentas_anteriores = rentas_anteriores[0]
                                else:
                                    rentas_anteriores = False

                                ant_impuesto_mensual = impuesto_total + (rentas_anteriores or 0.0)
                                impuesto_mensual = -(ant_impuesto_mensual / factor_valor)
                            elif factor_valor == 5.0:
                                self._cr.execute("""SELECT SUM(amount) as monto FROM hr_payslip hp INNER JOIN hr_payslip_line hpl
                ON hp.id = hpl.slip_id WHERE hp.employee_id = %s AND code='R5ta' AND substring(to_char(date_from,'YYYY-MM-DD') from 1 for 4) = %s AND substring(to_char(date_from,'YYYY-MM-DD') from 6 for 2) in ('01','02','03','04','05','06','07')""",
                                           (contrato.employee_id.id, str(d1.year)))
                                rentas_anteriores = self._cr.fetchone()
                                if rentas_anteriores:
                                    rentas_anteriores = rentas_anteriores[0]
                                else:
                                    rentas_anteriores = False

                                ant_impuesto_mensual = impuesto_total + (rentas_anteriores or 0.0)
                                impuesto_mensual = -(ant_impuesto_mensual / factor_valor)
                            elif factor_valor == 4.0:
                                self._cr.execute("""SELECT SUM(amount) as monto FROM hr_payslip hp INNER JOIN hr_payslip_line hpl
                ON hp.id = hpl.slip_id WHERE hp.employee_id = %s AND code='R5ta' AND substring(to_char(date_from,'YYYY-MM-DD') from 1 for 4) = %s AND substring(to_char(date_from,'YYYY-MM-DD') from 6 for 2) in ('01','02','03','04','05','06','07','08')""",
                                           (contrato.employee_id.id, str(d1.year)))
                                rentas_anteriores = self._cr.fetchone()
                                if rentas_anteriores:
                                    rentas_anteriores = rentas_anteriores[0]
                                else:
                                    rentas_anteriores = False

                                ant_impuesto_mensual = impuesto_total + (rentas_anteriores or 0.0)
                                impuesto_mensual = -(ant_impuesto_mensual / factor_valor)
                            elif factor_valor == 0.0:
                                self._cr.execute("""SELECT SUM(amount) as monto FROM hr_payslip hp INNER JOIN hr_payslip_line hpl
                ON hp.id = hpl.slip_id WHERE hp.employee_id = %s AND code='R5ta' AND substring(to_char(date_from,'YYYY-MM-DD') from 1 for 4) = %s AND substring(to_char(date_from,'YYYY-MM-DD') from 6 for 2) in ('01','02','03','04','05','06','07','08','09','10','11')""",
                                           (contrato.employee_id.id, str(d1.year)))
                                rentas_anteriores = self._cr.fetchone()
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

                            id_rule.write({'amount_fix': impuesto_mensual2})

                """FALTAS INJUSTIFICADAS"""
                self._cr.execute(
                    "SELECT hora_inicio FROM horas_extra WHERE employee_id = %s AND motivo=7 AND estado_pag=False AND fecha BETWEEN %s AND %s",
                    (contrato.employee_id.id, self.date_start, self.date_end))
                hora_inicio = self._cr.fetchone()
                if hora_inicio:
                    hora_inicio = hora_inicio[0]
                else:
                    hora_inicio = False

                id_rule_faltas = rule_obj.search([('code', '=', 'FI')])
                if not hora_inicio:
                    id_rule_faltas.write({'quantity': '0', 'amount_fix': 0})
                    # cr.execute('update hr_salary_rule set quantity= %s,amount_fix= %s where code = %s',
                    #            (0, 0, 'FI'))

                """FALTAS INJUSTIFICADAS"""
                self._cr.execute(
                    "SELECT COALESCE(SUM(horas), 0) AS ho, fecha FROM horas_extra WHERE employee_id = %s AND motivo=7 AND estado_pag=False AND fecha BETWEEN %s AND %s GROUP BY fecha ORDER BY fecha",
                    (contrato.employee_id.id, self.date_start, self.date_end))
                g_falta_inj = self._cr.dictfetchall()

                horas_falta_inj = 0
                importe_falta_inj = 0.0
                if g_falta_inj:
                    for g_f_inj in g_falta_inj:
                        g_falta_inj1 = g_f_inj['ho']
                        g_falta_inj2 = g_f_inj['ho']
                        # print ('-----------------------')
                        # print ('>>>>>>>>>>>>>>>>>>>>>', str(g_falta_inj1))
                        while g_falta_inj1 > 0:
                            # print ('>>>>>>>>esp>>>>>>>>>', str(g_falta_inj1))
                            if hora_inicio:
                                # print ('entre')
                                porc_fa_1 = contrato.wage / float(240)
                                porc_fa_2 = porc_fa_1 * 0.25
                                porc_fa_3 = porc_fa_2
                                importe_falta_inj = porc_fa_3
                                horas_falta_inj = horas_falta_inj + g_falta_inj1
                                # print ('suma', str(horas_falta_inj))
                                # cr.execute(
                                #     'update horas_extra set estado_pag=%s where employee_id = %s and motivo=%s',
                                #     (True, payslip.employee_id.id, 7))
                            g_falta_inj1 = g_falta_inj1 - 2

                    # cr.execute('update hr_salary_rule set quantity= %s, amount_fix= %s where code = %s',(horas_falta_inj, importe_falta_inj, 'FI'))
                    id_rule_faltas.write({'quantity': str(horas_falta_inj), 'amount_fix': -importe_falta_inj})
                else:
                    id_rule_faltas.write({'quantity': '0', 'amount_fix': 0})

                """Descansos Medicos"""
                # import datetime
                today = datetime.now()
                primer_dia = "%s-01-01 00:00:00" % (today.year)
                ultimo_dia = "%s-12-31 23:59:59" % (today.year)

                dm = self.pool.get('hr.holidays')
                id_dm = dm.search(self._cr, self._uid, [('holiday_status_id.indicador_ausentismo', '=', 'DM'),
                                            ('date_from', '>=', primer_dia), ('date_to', '<=', ultimo_dia),
                                            ('state', '=', 'validate'), ('employee_id', '=', contrato.employee_id.id)])
                id_rule_dmme20 = rule_obj.search([['code', '=', 'DMM20D']])
                id_rule_dmma20s = rule_obj.search([['code', '=', 'DM20S']])
                id_rule_dmma20s.write({'quantity': str(0), 'amount_fix': 0})
                id_rule_dmme20.write({'quantity': str(0), 'amount_fix': 0})
                if id_dm:
                    dias = sum(sum_dias.number_of_days_temp for sum_dias in dm.browse(self._cr, self._uid, id_dm))

                    # Total de dias entre fechas
                    dias_de_fecha_ids = dm.search(self._cr, self._uid, [('holiday_status_id.indicador_ausentismo', '=', 'DM'),
                                                            ('date_from', '>=', self.date_start), ('date_to', '<=', self.date_end),
                                                            ('state', '=', 'validate'),
                                                            ('employee_id', '=', contrato.employee_id.id)])
                    dias_de_fecha = sum(sum_dias.number_of_days_temp for sum_dias in  dm.browse(self._cr, self._uid, dias_de_fecha_ids))
                    """Descansos Medicos menores a 20 dias"""
                    print (dias)
                    print (dias_de_fecha)
                    if dias <= 20:
                        # print (dias_de_fecha)
                        descanso_medico = contrato.wage / float(240)
                        if dias_de_fecha > 0:
                            id_rule_dmme20.write({'quantity': str(dias_de_fecha), 'amount_fix': -descanso_medico})
                    else:
                        """Descansos Medicos MAYORES a 20 dias SUBSIDIOS"""
                        resto_dias = abs(dias - 20)
                        descanso_medico = contrato.wage / float(240)
                        if dias_de_fecha > 0:
                            resto_dias2 = abs(resto_dias - dias_de_fecha)
                            id_rule_dmme20.write(
                                           {'quantity': str(resto_dias2),
                                            'amount_fix': -descanso_medico},
                                           )
                            id_rule_dmma20s.write(
                                           {'quantity': str(resto_dias), 'amount_fix': -descanso_medico},
                                           )
                """PERMISOS"""
                salario_por_hora = contrato.wage / float(240)
                """PERMISO SINDICAL"""
                id_ps = dm.search(self._cr, self._uid, [('holiday_status_id.indicador_ausentismo', '=', 'PS'),
                                            ('date_from', '>=', self.date_start),
                                            ('date_to', '<=', self.date_end),
                                            ('state', '=', 'validate'),
                                            ('employee_id', '=', contrato.employee_id.id)])
                ps_salary_rule = rule_obj.search([['code', '=', 'PS']])
                print ('ps_sindical', str(id_ps))
                if id_ps:
                    dias_ps = sum(
                        sum_ps.number_of_days_temp for sum_ps in dm.browse(self._cr, self._uid, id_ps))
                    print ('ps_sindical_dias', str(dias_ps))
                    ps_salary_rule.write(
                                   {'quantity': str(dias_ps), 'amount_fix': salario_por_hora})
                else:
                    print ('ps_sindical else')
                    ps_salary_rule.write({'quantity': str(0), 'amount_fix': 0})

                """PERMISO SIN PAGO"""
                id_psp = dm.search(self._cr, self._uid, [('holiday_status_id.indicador_ausentismo', '=', 'PSP'),
                                             ('date_from', '>=', self.date_start),
                                             ('date_to', '<=', self.date_end),
                                             ('state', '=', 'validate'),
                                             ('employee_id', '=', contrato.employee_id.id)])
                psp_salary_rule = rule_obj.search([('code', '=', 'PSP')])
                if id_psp:
                    dias_psp = sum(
                        sum_psp.number_of_days_temp for sum_psp in dm.browse(self._cr, self._uid, id_psp))
                    psp_salary_rule.write(
                                   {'quantity': str(dias_psp), 'amount_fix': -salario_por_hora})
                else:
                    psp_salary_rule.write({'quantity': str(0), 'amount_fix': 0})

                """PERMISO POR PATERNIDAD"""
                id_ppp = dm.search(self._cr, self._uid, [('holiday_status_id.indicador_ausentismo', '=', 'PPP'),
                                             ('date_from', '>=', self.date_start),
                                             ('date_to', '<=', self.date_end),
                                             ('state', '=', 'validate'),
                                             ('employee_id', '=', contrato.employee_id.id)])
                ppp_salary_rule = rule_obj.search([('code', '=', 'PPP')])
                if id_ppp:
                    dias_ppp = sum(
                        sum_ppp.number_of_days_temp for sum_ppp in dm.browse(self._cr, self._uid, id_ppp))
                    ppp_salary_rule.write(
                                   {'quantity': str(dias_ppp), 'amount_fix': salario_por_hora},
                                   )
                else:
                    ppp_salary_rule.write({'quantity': str(0), 'amount_fix': 0},
                                   )

                """VACACIONES"""
                id_vcs = dm.search(self._cr, self._uid, [('holiday_status_id.indicador_ausentismo', '=', 'VCS'),
                                             ('date_from', '>=', self.date_start),
                                             ('date_to', '<=', self.date_end),
                                             ('state', '=', 'validate'),
                                             ('employee_id', '=', contrato.employee_id.id)])

                vcs_salary_rule = rule_obj.search([('code', '=', 'VCS')])
                print (id_vcs, vcs_salary_rule)
                if id_vcs:
                    dias_vcs = sum(
                        sum_vcs.number_of_days_temp for sum_vcs in dm.browse(self._cr, self._uid, id_vcs))
                    vcs_salary_rule.write(
                                   {'quantity': str(dias_vcs), 'amount_fix': salario_por_hora})
                else:
                    vcs_salary_rule.write({'quantity': str(0), 'amount_fix': 0})


                """DESCUENTO POR EL PODER JUDICIAL"""
                # hr_j = self.pool.get('hr.judiciales')
                # ids_judiciales = hr_j.search(cr, uid, [('inicio_vigencia', '>=', from_date),
                #                             ('fin_vigencia', '<=', to_date),
                #                             ('employee_id', '=', payslip.employee_id.id)], context=context)
                dpj_salary_rule = rule_obj.search([('code', '=', 'DPJ')])
                self._cr.execute("""SELECT * from hr_judiciales WHERE (inicio_vigencia, fin_vigencia) OVERLAPS(%s::DATE, %s::DATE) AND employee_id = %s""",
                           (self.date_start,self.date_end, contrato.employee_id.id))
                ids_j = self._cr.dictfetchall()
                print (ids_j)
                if ids_j:
                    for ids_judiciales in ids_j:
                        if ids_judiciales['importe_descontar'] > 0 and ids_judiciales['tipo_importe_descuento']:
                                print("Entre descontar")
                                descuento = ids_judiciales['importe_descontar']
                                descuento_final = 0.0
                                if ids_judiciales['tipo_importe_descuento'] in ['amount']:
                                    if ids_judiciales['tipo_moneda'] in ['nacional']:
                                        descuento_final = -(descuento) or 0.0
                                        dpj_salary_rule.write({'amount_pencentage':100, 'amount_fix': descuento_final})
                                    elif ids_judiciales['tipo_moneda'] in ['extranjera']:
                                        moneda = self.env['res.currency'].search([('name', '=', 'USD')], limit=1)
                                        print (moneda)
                                        descuento_final = -(descuento * moneda.tc_compra) or 0.0
                                        dpj_salary_rule.write({'amount_pencentage':100, 'amount_fix': descuento_final}
                                                      )
                                elif ids_judiciales['tipo_importe_descuento'] in ['percent']:
                                    descuento_final = -(contrato.wage * (descuento / 100.0)) or 0.0
                                    dpj_salary_rule.write({'amount_pencentage':descuento, 'amount_fix': descuento_final}
                                                   )


                                print('>>>monto>>>' + str(descuento_final))
                else:
                    dpj_salary_rule.write({'amount_pencentage':100, 'amount_fix': 0})


                """DESCUENTOS AFP"""
                """APORTE OBLIGATORIO"""
                reglas_para_afp = rule_obj.search([('category_id.code', '=', 'DEDUCCION')])
                BASE_IMPONIBLE_AFP = contrato.wage + sumando_a_proyeccion
                if reglas_para_afp:
                    for reafp in reglas_para_afp:
                        aoafp = rule_obj.search([('code', '=', 'AOAFP')])
                        psafp = rule_obj.search([('code', '=', 'PSAFP')])
                        cvafp = rule_obj.search([('code', '=', 'CVAFP')])
                        if reafp.afectacion_afp:
                            if contrato.employee_id.afp:
                                ao = BASE_IMPONIBLE_AFP * (contrato.employee_id.afp.porcentaje / 100)
                                if BASE_IMPONIBLE_AFP > contrato.employee_id.afp.monto_maximo:
                                    ps = contrato.employee_id.afp.monto_maximo * (contrato.employee_id.afp.prima / 100)
                                else:
                                    ps = BASE_IMPONIBLE_AFP * (contrato.employee_id.afp.prima / 100)
                                cv = BASE_IMPONIBLE_AFP * (contrato.employee_id.afp.comision_variable / 100)

                                aoafp.write({'amount_percentage':contrato.employee_id.afp.porcentaje, 'amount_fix': -ao})
                                psafp.write({'amount_percentage':contrato.employee_id.afp.prima, 'amount_fix': -ps})
                                cvafp.write({'amount_percentage':contrato.employee_id.afp.comision_variable, 'amount_fix': -cv})
                            else:
                                raise osv.except_osv('Error!','Defina un AFP para el empleado! %s' % contrato.employee_id.name_related)

                reglas_para_deduccion = rule_obj.search([('category_id.code', '=', 'DEDUCCION')])
                # horas extras y mas
                sumando_a_deduccion = 0.0
                for de in reglas_para_deduccion:
                    if de.amount_select == 'fix':
                        sumando_a_deduccion += abs(de.amount_fix * float(de.quantity))

                sueldo_basico = contrato.wage
                asignacion = asignacion_familiar
                incrementos = sumando_a_proyeccion
                deducciones = sumando_a_deduccion

                neto = (sueldo_basico + asignacion + incrementos) - deducciones

                # Sueldo Adelantado
                advance = (line.number_of_days_temp * (neto / int(dias_del_mes[1]))) or 0.0

                line_sav = ({
                    'advance_holidays_id': self.id,
                    'employee_id': line.employee_id.id,
                    'date': str(d1),
                    'date_end': str(d2),
                    'number_days': line.number_of_days_temp,
                    'number_days_temp': line.number_of_days_temp,
                    'advance': advance,
                    'advance_holidays': neto,
                    'state': 'draft',
                    'reason': self.reason.id,
                    # 'reason_code': amount_cu,
                    # 'reason_code_check': move_lines.currency_id.id,
                    'payment_method': self.journal_id.id,
                    'exceed_condition': False,
                    'department': line.employee_id.department_id.id if line.employee_id.department_id else False,
                })

                self.env['salary.advance'].create(line_sav)

                # self.write({'state': 'draft'})
            # print (line_sav)
            # self.advance_holidays_ids = line_sav
        else:
            raise osv.except_osv(_('Aviso!'), _('No existen vacaciones en estas fechas!!'))

    @api.one
    def approved(self):
        self.write({'state': 'approved'})
        ids_salary_advance = self.env['salary.advance'].search([['advance_holidays_id','=',self.id]])
        for salary in ids_salary_advance:
            salary.approve()


    @api.one
    def cancel(self):
        self.write({'state': 'cancel'})
        ids_salary_advance = self.env['salary.advance'].search([['advance_holidays_id', '=', self.id]])
        for salary in ids_salary_advance:
            salary.cancel()


class SalaryAdvancePayment(models.Model):
    _name = "salary.advance"

    def _employee_get(self):
        ids = self.pool.get('hr.employee').search(self._cr, self._uid, [('user_id', '=', self._uid)])
        if ids:
            return ids[0]
        return False

    def _get_currency(self):
        user = self.pool.get('res.users').browse(self._cr, self._uid, [self._uid])[0]
        return user.company_id.currency_id.id

    name = fields.Char(string='Name', readonly=True, select=True, default=lambda self: 'Adv/')
    employee_id = fields.Many2one('hr.employee', string='Empleado', required=True, default=_employee_get)
    date = fields.Date(string='Fecha de adelanto', required=True, default=lambda self: fields.Date.today(), store=True)
    reason = fields.Many2one('advance.razon', string='Razón', required=True)
    reason_code = fields.Char(related='reason.code', string="Codigo de Razon", store=True)
    reason_code_check = fields.Boolean(string="Check Razon", compute='_check_reason_code_check', store=True)
    currency_id = fields.Many2one('res.currency', string='Moneda', required=True,
                                  default=_get_currency)
    company_id = fields.Many2one('res.company', string='Compañia', required=True,
                                 default=lambda self: self.env.user.company_id)
    advance = fields.Float(string='Importe de Adelanto', required=True)
    payment_method = fields.Many2one('account.journal', string='Metodo de Pago', required=True)
    exceed_condition = fields.Boolean(string='Sobrepasar el limite maximo ')
    department = fields.Many2one('hr.department', string='Departamento')
    state = fields.Selection([('draft', 'Borrador'),
                              ('approved', 'Aprobado'),
                              ('cancel', 'Cancel')], string='Estado', copy=False)
    # Holidays
    advance_holidays_id = fields.Many2one('advance.holidays', 'Adelanto de Sueldo para Vacaciones', ondelete='cascade')
    date_end = fields.Date('Fecha Hasta', store=True)
    number_days = fields.Float('# Dias')
    advance_holidays = fields.Float(string='Sueldo Neto', readonly=True, store=True)
    number_days_temp = fields.Float('Dias temporales')

    estado_contador = fields.Integer(default=1)

    @api.onchange('date')
    def onchange_date_inicio(self):
        if self.date and not self.date_end:
            date_to_with_delta = datetime.strptime(self.date, DATETIME_FORMAT) + relativedelta(months=1, days=-1)
            self.date_end = str(date_to_with_delta)

        if (self.date and self.date_end) and (self.date > self.date_end):
            raise osv.except_osv(_('Error!'), _('La fecha de inicio no puede ser mayor que la fecha de fin.'))

        if self.date and self.date_end:
            d1 = date(int(self.date[0:4]), int(self.date[5:7]), int(self.date[-2:]))
            d2 = date(int(self.date_end[0:4]), int(self.date_end[5:7]), int(self.date_end[-2:]))
            dias_del_mes = d2 - d1
            dias_del_mes = (int(str(dias_del_mes).split(' ', 1)[0]) + 1)
            self.number_days = dias_del_mes
            self.number_days_temp = dias_del_mes

    @api.onchange('date_end')
    def onchange_date_fin(self):
        if (self.date and self.date_end) and (self.date > self.date_end):
            raise osv.except_osv(_('Error!'), _('La fecha de inicio no puede ser mayor que la fecha de fin.'))

        if self.date and self.date_end:
            d1 = date(int(self.date[0:4]), int(self.date[5:7]), int(self.date[-2:]))
            d2 = date(int(self.date_end[0:4]), int(self.date_end[5:7]), int(self.date_end[-2:]))
            dias_del_mes = d2 - d1
            dias_del_mes = (int(str(dias_del_mes).split(' ', 1)[0]) + 1)
            self.number_days = dias_del_mes
            self.number_days_temp = dias_del_mes

    @api.depends('reason')
    def _check_reason_code_check(self):
        if self.reason.code == 'ADV':
            self.reason_code_check = True
        else:
            self.reason_code_check = False

    @api.onchange('payment_method')
    def onchange_payment_method(self):
        res = {'value': {'currency_id': False}}
        if self.payment_method.currency:
            c_ids = self.pool.get('res.currency').search(self._cr, self._uid, [('id', '=', self.payment_method.currency.id)])
            if c_ids:
                self.currency_id = c_ids[0]
        else:
            c_ids = self.pool.get('res.currency').search(self._cr, self._uid, [('name', '=', 'PEN')])
            if c_ids:
                self.currency_id = c_ids[0]
        return res

    @api.onchange('currency_id')
    def onchange_currency_id(self, currency_id=False, company_id=False):
        res = {'value': {'journal_id': False}}
        journal_ids = self.pool.get('account.journal').search(self._cr, self._uid, [('type', '=', 'purchase'),
                                                                                    ('currency', '=', currency_id),
                                                                                    ('company_id', '=', company_id)])
        if journal_ids:
            res['value']['journal_id'] = journal_ids[0]
        return res

    @api.onchange('company_id')
    def onchange_company_id(self):
        company = self.company_id
        domain = [('company_id.id', '=', company.id), ]
        result = {
            'domain': {
                'payment_method': domain,
            },

        }
        return result

    def onchange_employee_id(self, cr, uid, ids, employee_id, context=None):
        emp_obj = self.pool.get('hr.employee')
        department_id = False
        if employee_id:
            employee = emp_obj.browse(cr, uid, employee_id, context=context)
            department_id = employee.department_id.id
        return {'value': {'department': department_id}}

    @api.model
    def create(self, vals):
        # vals['name'] = self.env['ir.sequence'].get('adv')
        emp_id = vals.get('employee_id')
        contract_obj = self.env['hr.contract']
        emp_obj = self.env['hr.employee']
        search_contract = contract_obj.search([('employee_id', '=', emp_id)])
        # print (search_contract)
        full_name = emp_obj.browse([emp_id]).name_related
        address = emp_obj.browse([emp_id]).address_home_id
        # raise Warning('full_name')
        if not address.id:
            raise osv.except_osv('Error!', 'Defina una dirección particular (address_home_id) para el empleado %s' % full_name)
        salary_advance_search = self.search([('employee_id', '=', emp_id)])
        for each_advance in salary_advance_search:
            current_month = datetime.strptime(vals.get('date'), '%Y-%m-%d').date().month
            existing_month = datetime.strptime(each_advance.date, '%Y-%m-%d').date().month
            # if current_month == existing_month or current_month < existing_month:
            #     raise osv.except_osv('Error!', 'Solo se puede hacer un adelanto por mes Gracias!')
        if not search_contract:
            raise osv.except_osv('Error!', 'Defina un contrato para el empleado!')
        for each_contract in search_contract:
            struct_id = each_contract.struct_id
            if not struct_id.max_percent or not struct_id.advance_date:
                raise osv.except_osv('Error!', 'El porcentaje o días máximos de adelanto no se han registrado (RRHH/Config/Nomina/Estructuras salariales)')
            adv = vals.get('advance')
            amt = (each_contract.struct_id.max_percent * each_contract.wage) / 100
            if adv > each_contract.wage:
                raise osv.except_osv('Error!', 'El monto de adelanto es mayor que el salario')
            if adv > amt and vals.get('exceed_condition') == False:
                raise osv.except_osv('Error!', 'El monto de adelanto no puede ser mayor al porcentaje asignado (Si lo desea marque Sobrepasar el Limite)')
        vals.update({'state': 'draft'})
        res_id = super(SalaryAdvancePayment, self).create(vals)
        return res_id

    @api.multi
    def write(self, vals):
        print (vals)
        # print (self.employee_id.id,self.date,self.advance)
        # print (self._context)
        emp_id = self.employee_id.id
        date = self.date
        advance = self.advance
        if 'employee_id' in vals:
            emp_id = vals.get('employee_id')
        if 'date' in vals:
            date = vals.get('date')
        if 'advance' in vals:
            advance = vals.get('advance')
        contract = self.env['hr.contract']
        search_contract = contract.search([('employee_id', '=', emp_id)])
        emp_obj = self.env['hr.employee']
        full_name = emp_obj.browse([emp_id]).name_related
        # raise Warning(full_name)
        address = emp_obj.browse([emp_id]).address_home_id
        if not address.id:
            # raise Warning([emp_id])
            raise osv.except_osv('Error!', 'Defina una dirección particular (address_home_id) para el empleado %s' % full_name)
        salary_advance_search = self.search([('employee_id', '=', emp_id)])
        for each_advance in salary_advance_search:
            current_month = datetime.strptime(date, '%Y-%m-%d').date().month
            existing_month = datetime.strptime(each_advance.date, '%Y-%m-%d').date().month
            if each_advance.id != self.id and (current_month == existing_month or current_month < existing_month):
                raise osv.except_osv('Error!', 'Solo se puede hacer un adelanto por mes Gracias!')
        if not search_contract:
            raise osv.except_osv('Error!', 'Defina un contrato para el empleado!')
        for each_contract in search_contract:
            if not each_contract.struct_id.max_percent or not each_contract.struct_id.advance_date:
                raise osv.except_osv('El porcentaje o días máximos de adelanto no se han registrado (RRHH/Config/Nomina/Estructuras salariales)')
            amt = (each_contract.struct_id.max_percent * each_contract.wage) / 100
            if advance > each_contract.wage:
                raise osv.except_osv('Error!', 'El monto de adelanto es mayor que el salario')
            if advance > amt and vals.get('exceed_condition') == False:
                raise osv.except_osv('Error!', 'El monto de adelanto no puede ser mayor al porcentaje asignado (Si lo desea marque Sobrepasar el Limite)')
        super(SalaryAdvancePayment, self).write(vals)
        return True

    def compute_advance_totals(self, account_move_lines):
        total = 0.0
        for i in account_move_lines:
            total -= i['price']
        return total, account_move_lines

    def line_get_convert(self, x, part, date):
        partner_id = self.env['res.partner']._find_accounting_partner(part).id
        res = {
            'date_maturity': x.get('date_maturity', False),
            'partner_id': partner_id,
            'name': x.get('name'),
            'date': date,
            'debit': x['price'] > 0 and x['price'],
            'credit': x['price'] < 0 and -x['price'],
            'account_id': x['account_id'],
            'analytic_lines': x.get('analytic_lines', False),
            'amount_currency': x['price'] > 0 and abs(x.get('amount_currency', False)) or -abs(
                x.get('amount_currency', False)),
            'currency_id': x.get('currency_id', False),
            'ref': x.get('ref', False),
            'product_id': x.get('product_id', False),
            'product_uom_id': x.get('uos_id', False),
            'analytic_account_id': x.get('account_analytic_id', False),
        }
        return res

    def account_adv_get(self, salary_adv_obj):
        return self.env['account.move'].account_move_prepare(salary_adv_obj.journal.id, date=False,
                                                             ref=self.employee_id.name, company_id=False)

    @api.multi
    def button_vacaciones(self):
        self.ensure_one()
        treeview_id = self.env.ref('advance_salary.view_advance_holidays_form_yo').id
        ctx = {'employee_id': self.employee_id.id, 'indicador_ausentismo': 'VCS'}
        return {
            'name': 'Vacaciones',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'advance.holidays.tree',
            'views': [(treeview_id, 'form')],
            # 'view_id': treeview_id,
            'target': 'new',
            'context': ctx,
            # 'domain': [],

        }
        ### in domain pass ids if you want to show only filter data else it will display all data of that model.

    @api.one
    def approve(self):
        self.name = self.env['ir.sequence'].get('adv')

        self.employee_id.write({'advance_amount': self.advance})
        move_obj = self.env['account.move']
        company_id = self.env['res.users'].browse(self._uid).company_id
        salary_adv_obj = self.env['advance.rules'].search([('company_id', '=', company_id.id)])
        if not salary_adv_obj:
            raise Warning(
                _("No se define una regla de adelanto de salario Para la empresa del usuario que inicio sesión."))

        else:
            move_id = move_obj.create(self.account_adv_get(salary_adv_obj))
            acc_debit = salary_adv_obj.debit.id
            adv_line = {
                'type': 'src',
                'name': 'Adelanto de Sueldo',
                'price_unit': self.advance,
                'price': self.advance,
                'account_id': acc_debit,
                'currency_id': self.currency_id.id,
            }
            total, adv_line = self.compute_advance_totals([adv_line])
            credit_acc = self.payment_method.default_credit_account_id.id
            adv_line.append({
                'type': 'dest',
                'name': 'Adelanto de Sueldo2222',
                'price': total,
                'account_id': credit_acc,
                'ref': self.ids[0]
            })
            journal = move_id.journal_id
            company_currency = self.env.user.company_id.currency_id.id
            total, total_currency, adv_line = self.compute_expense_totals(self, company_currency, self.name, adv_line)
            lines = map(lambda x: (0, 0, self.line_get_convert(x, self.employee_id.address_home_id, self.date)),
                        adv_line)
            if journal.entry_posted:
                move_obj.button_validate(move_id.id)
            # print (lines)
            move_id.write({'line_id': lines})
            self.write({'state': 'approved'})

            print (str(self.date)+' 00:00:00')
            print (str(self.date_end)+' 23:59:59')

            # ids_holidays = self.env['hr.holidays'].search((['date_from', '>=', str(self.date)+' 00:00:00'],
            #                                                ['date_to', '<=', str(self.date_end)+' 23:59:59'],
            #                                                ['employee_id', '=', self.employee_id.id],
            #                                                ['state', '=', 'validate'],
            #                                                ['holiday_status_id.indicador_ausentismo', '=', 'VCS']), limit=1)
            # print ('ssssssssssssss')
            # print (ids_holidays)
            # if ids_holidays:
            # for l in ids_holidays:
            #     l.write({'paid': True})

    def compute_expense_totals(self, cr, uid, adv, company_currency, ref, account_move_lines, context=None):
        cur_obj = self.pool.get('res.currency')
        total = 0.0
        total_currency = 0.0
        for i in account_move_lines:
            if adv.currency_id.id != company_currency:
                i['currency_id'] = adv.currency_id.id
                i['amount_currency'] = i['price']
                i['price'] = cur_obj.compute(cr, uid, adv.currency_id.id,
                                             company_currency, i['price'],
                                             context=context)
            else:
                i['amount_currency'] = False
                i['currency_id'] = False
            total -= i['price']
            total_currency -= i['amount_currency'] or i['price']
        return total, total_currency, account_move_lines

    @api.one
    def cancel(self):
        self.write({'state': 'cancel'})
        # ids_holidays = self.env['hr.holidays'].search((['date_from', '>=', str(self.date)+' 00:00:00'],
        #                                                ['date_to', '<=', str(self.date_end)+' 23:59:59'],
        #                                                ['employee_id', '=', self.employee_id.id],
        #                                                ['state', '=', 'validate'],
        #                                                ['holiday_status_id.indicador_ausentismo', '=', 'VCS']), limit=1)
        # print ('ssssssssssssss')
        # print (ids_holidays)
        # if ids_holidays:
        # for l in ids_holidays:
        #     l.write({'paid': False})


class EmployeeAdvance(models.Model):
    _inherit = 'hr.employee'
    advance_amount = fields.Float("Monto de adelanto")


class SalaryAdvanceRazon(models.Model):
    _name = 'advance.razon'
    # _rec_name = 'name'
    # _description = 'New Description'

    name = fields.Char('Razón', required=True)
    code = fields.Char('Codigo', required=True)
    discount = fields.Boolean('¿Calcular Descuentos?')

    _sql_constraints = [
            ('code', 'unique(code)', 'El codigo ya existe!'),
            ('name', 'unique(name)', 'El nombre ya existe!'),
    ]


class hr_holidays(models.Model):
    # _name = 'new_module.new_module'
    _inherit = 'hr.holidays'
    _order = 'date_from desc'

    paid = fields.Boolean('¿Pagado?')
