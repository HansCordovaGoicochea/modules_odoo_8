# -*- coding: utf-8 -*-
import base64

from openerp import _, api, fields, models


# class hr_account_fiscalyear(models.Model):
#     _inherit = 'account.fiscalyear'
#

class hr_uit_sunat(models.Model):
    @api.multi
    def _default_fiscalyear(self):
        """Return default Fiscalyear value"""
        re = self.env['account.fiscalyear'].find()
        return re

    _name = 'hr.uit.sunat'
    # _rec_name = 'name'
    # _description = 'New Description'

    ejercicio_fiscal_id = fields.Many2one('account.fiscalyear', 'Ejercicio Fiscal', required=True, select=True,
                                          default=_default_fiscalyear)
    valor_uit = fields.Float('Valor UIT')


class hr_deducciones_x_ejercicio(models.Model):
    @api.multi
    def _default_fiscalyear(self):
        """Return default Fiscalyear value"""
        re = self.env['account.fiscalyear'].find()
        return re

    _name = 'hr.deducciones.x.ejercicio'
    # _rec_name = 'name'
    # _description = 'New Description'

    ejercicio_fiscal_id = fields.Many2one('account.fiscalyear', 'Ejercicio Fiscal', required=True, select=True,
                                          default=_default_fiscalyear)
    deducir = fields.Float('Deducir')
    deduccion = fields.Char('Deducción')


class hr_tasas_x_ejercicio(models.Model):
    @api.multi
    def _default_fiscalyear(self):
        """Return default Fiscalyear value"""
        re = self.env['account.fiscalyear'].find()
        return re

    _name = 'hr.tasas.x.ejercicio'
    _rec_name = 'ejercicio_fiscal_id'
    # _description = 'New Description'

    ejercicio_fiscal_id = fields.Many2one('account.fiscalyear', 'Ejercicio Fiscal', default=_default_fiscalyear)
    tasas_ids = fields.One2many(comodel_name="hr.tasas.x.ejercicio.detalle", inverse_name="tasas_id",
                                string="Tasas aplicables por ejercicio", required=False, )


class hr_tasas_x_ejercicio_detalle(models.Model):
    _name = 'hr.tasas.x.ejercicio.detalle'
    # _rec_name = 'name'
    # _description = 'New Description'

    tasas_id = fields.Many2one('hr.tasas.x.ejercicio', 'Ejercicio Fiscal')
    desde = fields.Char('Desde')
    hasta = fields.Char('Hasta')
    valor_minimo = fields.Float('Valor Mínimo')
    valor_maximo = fields.Float('Valor Máximo')
    porcentaje = fields.Float('Porcentaje')
    impuesto = fields.Float('Impuesto (Si el valor supera el valor máximo)')


class hr_factor_x_ejercicio(models.Model):
    @api.multi
    def _default_fiscalyear(self):
        """Return default Fiscalyear value"""
        re = self.env['account.fiscalyear'].find()
        return re

    _name = 'hr.factor.x.ejercicio'
    _rec_name = 'ejercicio_fiscal_id'
    # _description = 'New Description'

    ejercicio_fiscal_id = fields.Many2one('account.fiscalyear', 'Ejercicio Fiscal', default=_default_fiscalyear)
    factor_ids = fields.One2many(comodel_name="hr.factor.x.ejercicio.detalle", inverse_name="factor_id",
                                 string="Tasas aplicables por ejercicio", required=False, )


class hr_factor_x_ejercicio_detalle(models.Model):
    _name = 'hr.factor.x.ejercicio.detalle'
    # _rec_name = 'name'
    # _description = 'New Description'

    factor_id = fields.Many2one('hr.factor.x.ejercicio', 'Ejercicio Fiscal')
    mes_inicio = fields.Selection(string="Mes Inicio",
                                  selection=[('1', 'Enero'), ('2', 'Febrero'), ('3', 'Marzo'), ('4', 'Abril'),
                                             ('5', 'Mayo'), ('6', 'Junio'), ('7', 'Julio'), ('8', 'Agosto'),
                                             ('9', 'Septiembre'), ('10', 'Octubre'), ('11', 'Noviembre'),
                                             ('12', 'Diciembre'), ])

    mes_fin = fields.Selection(string="Mes Final",
                               selection=[('1', 'Enero'), ('2', 'Febrero'), ('3', 'Marzo'), ('4', 'Abril'),
                                          ('5', 'Mayo'), ('6', 'Junio'), ('7', 'Julio'), ('8', 'Agosto'),
                                          ('9', 'Septiembre'), ('10', 'Octubre'), ('11', 'Noviembre'),
                                          ('12', 'Diciembre'), ])

    factor = fields.Float(string='Factor')
    deduccion = fields.Boolean(string='Deducciones')
    mes_inicio_deduce = fields.Selection(string="Mes Inicio Deduces",
                                         selection=[('1', 'Enero'), ('2', 'Febrero'), ('3', 'Marzo'), ('4', 'Abril'),
                                                    ('5', 'Mayo'), ('6', 'Junio'), ('7', 'Julio'), ('8', 'Agosto'),
                                                    ('9', 'Septiembre'), ('10', 'Octubre'), ('11', 'Noviembre'),
                                                    ('12', 'Diciembre'), ])

    mes_fin_deduce = fields.Selection(string="Mes Final Deduces",
                                      selection=[('1', 'Enero'), ('2', 'Febrero'), ('3', 'Marzo'), ('4', 'Abril'),
                                                 ('5', 'Mayo'), ('6', 'Junio'), ('7', 'Julio'), ('8', 'Agosto'),
                                                 ('9', 'Septiembre'), ('10', 'Octubre'), ('11', 'Noviembre'),
                                                 ('12', 'Diciembre'), ])


class hr_mes_x_ejercicio(models.Model):
    @api.multi
    def _default_fiscalyear(self):
        """Return default Fiscalyear value"""
        re = self.env['account.fiscalyear'].find()
        return re

    _name = 'hr.mes.x.ejercicio'
    _rec_name = 'ejercicio_fiscal_id'
    # _description = 'New Description'

    ejercicio_fiscal_id = fields.Many2one('account.fiscalyear', 'Ejercicio Fiscal', default=_default_fiscalyear)
    mes_ids = fields.One2many(comodel_name="hr.mes.x.ejercicio.detalle", inverse_name="mes_id",
                              string="Mes aplicables por ejercicio", required=False, )


class hr_mes_x_ejercicio_detalle(models.Model):
    _name = 'hr.mes.x.ejercicio.detalle'
    # _rec_name = 'name'
    # _description = 'New Description'

    mes_id = fields.Many2one('hr.mes.x.ejercicio', 'Ejercicio Fiscal')
    mes = fields.Selection(string="Mes",
                           selection=[('1', 'Enero'), ('2', 'Febrero'), ('3', 'Marzo'), ('4', 'Abril'),
                                      ('5', 'Mayo'), ('6', 'Junio'), ('7', 'Julio'), ('8', 'Agosto'),
                                      ('9', 'Septiembre'), ('10', 'Octubre'), ('11', 'Noviembre'),
                                      ('12', 'Diciembre'), ])
    valor = fields.Integer(string="Valor", required=False, )


class hr_afps(models.Model):
    _name = 'hr.afps'
    _rec_name = 'afp'
    # _description = 'New Description'

    afp = fields.Char('AFP', required=True)
    porcentaje = fields.Float('Porcentaje')
    prima = fields.Float('Prima')
    comision_variable = fields.Float('Comisión variable')
    comision_fija = fields.Float('Comisión fija')

    monto_maximo = fields.Float('Monto máximo')


class hr_remuneracion_cts(models.Model):
    @api.multi
    def _default_fiscalyear(self):
        """Return default Fiscalyear value"""
        re = self.env['account.fiscalyear'].find()
        return re

    _name = 'hr.remuneracion.cts'
    # _rec_name = 'name'
    # _description = 'New Description'

    ejercicio_fiscal_id = fields.Many2one('account.fiscalyear', 'Ejercicio Fiscal', default=_default_fiscalyear)
    fecha_pago = fields.Date('Fecha de Pago')
    mes_pago = fields.Selection(string="Mes de Pago",
                                selection=[('1', 'Enero'), ('2', 'Febrero'), ('3', 'Marzo'), ('4', 'Abril'),
                                           ('5', 'Mayo'), ('6', 'Junio'), ('7', 'Julio'), ('8', 'Agosto'),
                                           ('9', 'Septiembre'), ('10', 'Octubre'), ('11', 'Noviembre'),
                                           ('12', 'Diciembre'), ])
    estado = fields.Boolean('Estado')


class hr_suma_cts(models.Model):
    @api.multi
    def _default_fiscalyear(self):
        """Return default Fiscalyear value"""
        re = self.env['account.fiscalyear'].find()
        return re

    _name = 'hr.suma.cts'
    # _rec_name = 'name'
    # _description = 'New Description'

    ejercicio_fiscal_id = fields.Many2one('account.fiscalyear', 'Ejercicio Fiscal', default=_default_fiscalyear)
    fecha_inicio = fields.Date('Fecha de Inicio')
    fecha_fin = fields.Date('Fecha de Fin')
    aplica_suma = fields.Boolean('Aplica Suma?')
    concepto = fields.Char('Concepto')
    estado = fields.Boolean('Estado')

    # txt_filename = fields.Char()
    # txt_binary = fields.Binary()
    #
    # @api.one
    # def generate_file(self):
    #     """
    #     function called from button
    #     """
    #     content = str(self.ejercicio_fiscal_id.name) + '|' + str(self.fecha_inicio) + '|' + str(self.fecha_fin) + '|' + str(self.aplica_suma)
    #     # make something to generate content
    #     return self.write({
    #         'txt_filename': 'file.txt',
    #         'txt_binary': base64.encodestring(content)
    #     })
