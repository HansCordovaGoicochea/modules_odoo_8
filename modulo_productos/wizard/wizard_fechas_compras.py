from openerp import models, fields, api, _
from openerp.exceptions import Warning
from datetime import datetime
import time


class purchase_order_wizard(models.TransientModel):
    _name = "purchase.order.wizard"

    period_from_dp = fields.Datetime('Inicio', required=True)
    period_to_dp = fields.Datetime('Fin', required=True)

    @api.v7
    def account_chart_open_window(self, cr, uid, ids, context=None):
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        # period_obj = self.pool.get('account.period')
        # fy_obj = self.pool.get('account.fiscalyear')
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, context=context)[0]
        result = mod_obj.get_object_reference(cr, uid, 'purchase', 'purchase_form_action')
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]
        # fiscalyear_id = data.get('fiscalyear', False) and data['fiscalyear'][0] or False
        # result['periods'] = []
        if data['period_from_dp'] and data['period_to_dp']:
            period_from_dp = data.get('period_from_dp', False) and data['period_from_dp'] or False
            period_to_dp = data.get('period_to_dp', False) and data['period_to_dp'] or False
            # result['periods'] = period_obj.build_ctx_periods(cr, uid, period_from, period_to)
            period_from_dp = datetime.strptime(period_from_dp, '%Y-%m-%d %H:%M:%S')
            period_to_dp = datetime.strptime(period_to_dp, '%Y-%m-%d %H:%M:%S')
            period_from_dp = period_from_dp.strftime("%d/%m/%Y 00:00:00")
            period_to_dp = period_to_dp.strftime("%d/%m/%Y 23:59:59")

            result['context'] = str({'search_default_date_order': str(period_from_dp), 'search_default_date_order_hasta': str(period_to_dp)})

        print result
        return result

