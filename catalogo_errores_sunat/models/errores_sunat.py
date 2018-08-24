# -*- coding: utf-8 -*-
from openerp import _, api, fields, models


class catalogo_errores_sunat(models.Model):
    _name = "catalogo.errores.sunat"
    _description = 'Codigo errores de CDR Sunat'

    code = fields.Char(string='Codigo', size=4, select=True, required=True)
    name = fields.Char(string='Descripcion', size=255, select=True, required=True)
    
    @api.multi
    @api.depends('code', 'name')
    def name_get(self):
        result = []
        for table in self:
            l_name = table.code and table.code + ' - ' or ''
            l_name +=  table.name
            result.append((table.id, l_name ))
        return result

