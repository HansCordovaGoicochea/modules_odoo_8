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

{
    'name': 'Date Picker - Chart of Accounts',
    'version': '1.1',
    'author': 'Temur',
    'license': 'AGPL-3',
    'category': 'Accounting & Finance',
    'summary': 'Adds date range selection fields with date picker field in the "chart of accounts" dialog window',
    'website': 'http://www.delta-comm.ge/',
    'description': """
This module adds selection fields with Date Picker in Chart of Accounts
=======================================================================
            
This module adds date range selection fields with date picker field in the "chart of accounts" dialog window.
It's recommended to use this module only if you are using "daily periods" (or some small periods) in accounting.

    """,
    'depends': ['account_accountant'],
    'images':[],
    'demo':[],
    'test': [],
    'data':['account_chart_date_picker_view.xml'],
    'application': False,
    'auto_install': False,
    'installable': True,
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
