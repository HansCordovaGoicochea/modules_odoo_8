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
    'name' : 'Renta de Quinta Categoria Configuraciones',
    'version' : '1.0',
    'author' : 'H',
    'category' : 'HH.RR',
    'summary': 'Renta de Quinta Categoria Configuraciones',
    'license': 'AGPL-3',
    'contributors': [
        'H',
    ],
    'description' : """
Renta de Quinta Categoria Configuraciones

====================================

Tablas:
--------------------------------------------
    * Renta de Quinta Categoria Configuraciones

    """,
    'website': 'h.com',
    'depends' : ['base','hr'],
    'data': [
        'security/ir.model.access.csv',
        'views/quinta_view.xml',
        # 'views/quinta_widget.xml',
        # 'data/catalogo_data.xml',


    ],
    'qweb' : [
        # 'views/txt_button.xml',
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
