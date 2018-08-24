# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.osv import osv


class SalaryStructure(models.Model):
    _inherit = 'hr.payroll.structure'
    max_percent = fields.Integer(string='Max. Porcentaje de adelanto de Sueldo', default=100)
    advance_date = fields.Integer(string='Adelanto de sueldo - Despues cuantos dias', default=1)


class AdvanceRule(models.Model):
    _name = "advance.rules"
    name = fields.Char(string='Nombre', required=True)
    debit = fields.Many2one('account.account', string='Cuenta de Debito', domain="[('type','=','other')]", required=True)
    credit = fields.Many2one('account.account', string='Cuenta de Credito', domain="[('type','=','other')]", required=True)
    journal = fields.Many2one('account.journal', string='Diario', required=True)
    company_id = fields.Many2one('res.company', string='Compañia', default=lambda self: self.env.user.company_id)
    analytic_journal = fields.Many2one('account.analytic.journal', string='Diario Analitico')

    @api.model
    def create(self, vals):
        company_id = vals.get('company_id')
        advance_rule_search = self.search([('company_id', '=', company_id)])
        if advance_rule_search:
            raise osv.except_osv('Error!', 'La regla de adelanto para esta compañía ya existe')
        res_id = super(AdvanceRule, self).create(vals)
        return res_id

    @api.multi
    def write(self, vals):
        company_id = self.company_id
        if 'company_id' in vals:
            company_id = vals.get('company_id')
        advance_rule_search = self.search([('company_id', '=', company_id)])
        if advance_rule_search and advance_rule_search.id != self.id:
            raise osv.except_osv('Error!', 'La regla de adelanto para esta compañía ya existe')
        super(AdvanceRule, self).write(vals)
        return True
