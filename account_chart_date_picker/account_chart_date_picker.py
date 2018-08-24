# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014-2015  Delta Comm LLC  (<http://www.delta-comm.ge>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api, _
from openerp.exceptions import Warning


class account_chart(models.TransientModel):
    _name = "account.chart"
    _inherit = "account.chart"

    period_from_dp = fields.Date('period_from_dp')
    period_to_dp = fields.Date('period_to_dp')

    @api.onchange('period_from')
    def _onchange_period_from(self):
        if not self.period_from_dp or \
                self.period_from_dp != self.period_from.date_start:
            self.period_from_dp = self.period_from.date_start
    
    @api.onchange('period_from_dp')
    def _onchange_period_from_dp(self):
        if not self.period_from_dp:
            return False
        periods = self.env['account.period'].search(['&',
            ('date_start','<=',self.period_from_dp),
            ('date_stop','>=',self.period_from_dp)])
        if not periods:
            raise Warning(_('Date selected is out of scope!'))
            return False
        if self.period_from and self.period_from != periods[0]:
            self.period_from = periods[0]
        if self.period_from_dp != periods[0].date_start:
            self.period_from_dp = periods.date_start

    @api.onchange('period_to')
    def _onchange_period_to(self):
        if not self.period_to_dp or self.period_to_dp != self.period_to.date_stop:
            self.period_to_dp = self.period_to.date_stop

    @api.onchange('period_to_dp')
    def _onchange_period_to_dp(self):
        if not self.period_to_dp:
            return False
        periods = self.env['account.period'].search(['&',
            ('date_start','<=',self.period_to_dp),
            ('date_stop','>=',self.period_to_dp)])
        if not periods:
            raise Warning(_('Date selected is out of scope!'))
            return False
        if self.period_to and self.period_to != periods[0]:
            self.period_to = periods[0]
        if self.period_to_dp != periods[0].date_stop:
            self.period_to_dp = periods.date_stop

account_chart()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
