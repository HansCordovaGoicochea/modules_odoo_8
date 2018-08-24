# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2009-TODAY Odoo Peru(<http://www.odooperu.pe>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

{
    'name' : 'Catalogo Registro de Derechohabientes SUNAT',
    'version' : '1.0',
    'author' : 'h',
    'category' : 'Accounting & Finance',
    'summary': 'TABLAS A SER USADAS EN EL T-REGISTRO /REGISTRO DE DERECHOHABIENTES',
    'license': 'AGPL-3',
    'contributors': [
        'h',
    ],
    'description' : """
ingrese al modulo web de  T-REGISTRO  - Registro de Derechohabientes www/sunat.gob.pe o llamenos al 0-801-12100

====================================

Tablas:
--------------------------------------------
    * ingrese al modulo web de  T-REGISTRO  - Registro de Derechohabientes www/sunat.gob.pe o llamenos al 0-801-12100

    """,
    'website': 'h.com',
    'depends' : ['base','hr'],
    'data': [
        'security/ir.model.access.csv',
        'views/catalogo_view.xml',
        'data/catalogo_data.xml',


    ],
    'qweb' : [

    ],
    'demo': [
        #'demo/account_demo.xml',
    ],
    'test': [
        #'test/account_test_users.yml',
    ],
    'images': [
        # 'static/description/banner.png',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    "sequence": 1,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
