# -*- coding: utf-8 -*-
from datetime import datetime, date
import calendar
from openerp import models, fields, api, _

amount = 0
dias_del_mes = 0
vacaciones_del_mes = 0
advance = 0
# a.var = 1


class SalaryRuleInput(models.Model):
    _inherit = 'hr.payslip'

    # global cont
    cont = 1
    def get_inputs(self, cr, uid, contract_ids, date_from, date_to, context=None):
        global amount
        global dias_del_mes
        global vacaciones_del_mes
        global advance
        # global cont
        res = super(SalaryRuleInput, self).get_inputs(cr, uid, contract_ids, date_from, date_to, context=None)
        contract_obj = self.pool.get('hr.contract')
        contr_id = contract_obj.browse(cr, uid, contract_ids[0], context=context)
        emp_id = contract_obj.browse(cr, uid, contract_ids[0], context=context).employee_id.name
        adv_salary = self.pool.get('salary.advance').search(cr, uid, [('employee_id', '=', emp_id)])
        # print (date_from, date_to)

        for each_employee in adv_salary:
            current_date = datetime.strptime(date_from, '%Y-%m-%d').date().month
            date_f = self.pool.get('salary.advance').browse(cr, uid, each_employee, context).date
            date_en = self.pool.get('salary.advance').browse(cr, uid, each_employee, context).date_end
            existing_date = datetime.strptime(date_f, '%Y-%m-%d').date().month
            existing_date_end = datetime.strptime(date_en, '%Y-%m-%d').date().month
            if current_date == existing_date or current_date == existing_date_end:
                adv_browse = self.pool.get('salary.advance').browse(cr, uid, each_employee, context)
                state = adv_browse.state
                reason = adv_browse.reason_code_check

                fechas_desde = adv_browse.date
                fechas_hasta = adv_browse.date_end
                days= adv_browse.number_days
                days_temp = adv_browse.number_days_temp
                neto = adv_browse.advance_holidays
                contador = adv_browse.estado_contador
                # advance = 0.0
                for result in res:

                    # if state == 'approved' and amount != 0:

                    if state == 'approved':
                        if not reason:
                            amount = adv_browse.advance
                        else:
                            # los dias deberían ser 31 para para poder estandarizar el monto de adelanto ---
                            # esta saliendo mal calculo si se hace por los dias del mes
                            d1 = date(int(fechas_desde[0:4]), int(fechas_desde[5:7]), int(fechas_desde[-2:]))
                            d2 = date(int(date_to[0:4]), int(date_to[5:7]), int(date_to[-2:]))
                            print ('countcojuntnn')
                            print (contador)
                            print ('countcojuntnn')
                            if contador == 1:
                                if date_to < fechas_hasta and days == days_temp:
                                    dias_del_mes = calendar.monthrange(d1.year, d1.month)
                                    vacaciones_del_mes = d2 - d1
                                    print ('daysvacaciones_del_mesvacaciones_del_mes_temp', str(vacaciones_del_mes))
                                    vacaciones_del_mes = (int(str(vacaciones_del_mes).split(' ', 1)[0]) + 1)
                                    print ('vacaciones_del_mesvacaciones_del_messsssss', str(vacaciones_del_mes))
                                    print ('dias del mes if', str(dias_del_mes))
                                    # Sueldo Adelantado no todo
                                    advance = (vacaciones_del_mes * (neto / int(dias_del_mes[1]))) or 0.0
                                    print ('days_temp',str(days_temp))
                                    print ('vacaciones_del_mes',str(vacaciones_del_mes))
                                    print ('days_temp - vacaciones_del_mes',str(days_temp - vacaciones_del_mes))
                                    adv_browse.write({'number_days_temp': days_temp - vacaciones_del_mes})
                                    amount = advance
                                else:
                                    monto_adelantado = adv_browse.advance
                                    # dias_del_mes = calendar.monthrange(d2.year, d2.month)
                                    print ('dias del mes else',str(dias_del_mes))
                                    # resto
                                    # advance = (days_temp * (neto / int(dias_del_mes[1]))) or 0.0
                                    # advance = (vacaciones_del_mes * (neto / int(dias_del_mes[1]))) or 0.0
                                    # adv_browse.write({'number_days_temp': days_temp - days_temp})
                                    # amount = advance
                                    print ('advanceadvance',str(advance))
                                    print ('monto_adelantadomonto_adelantado',str(monto_adelantado))
                                    amount2 = monto_adelantado - advance
                                    print ('amount2',str(amount2))
                                    amount = amount2
                                adv_browse.write({'estado_contador': 3})

                                print ('dias_del_mes', str(dias_del_mes))

                        print ('advancssssse fueraaaaaa', str(amount))
                        if reason:
                            if result.get('code') in ('SAR', 'SARI'):
                                result['amount'] = amount
                        else:
                            if result.get('code') == 'SAR':
                                result['amount'] = amount

        return res
    # cont = 1
