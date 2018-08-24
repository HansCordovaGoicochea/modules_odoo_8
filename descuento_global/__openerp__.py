# -*- coding: utf-8 -*-
{
    "name": """Global Discount\
    """,
    'version': '9.0.0.0.1',
    'category': 'Accoun/invoice',
    'sequence': 12,
    'author':  'H',
    'website': 'http://h.com',
    'license': 'AGPL-3',
    'summary': '',
    'description': """
Make available a global discount.
===============================================================
""",
    'depends': [
        'account',
        'sale',
        'product',
        'account_voucher',
        'base',
        ],
    'data': [
        #'security/ir.model.access.csv',
        'views/account_invoice.xml',
        'views/cabecera_periodo_view.xml',
        'views/pdf_report.xml',
    ],
    'js': ['static/src/js/cabecera_periodo.js'],
    'qweb': ['static/src/xml/cabecera_periodo.xml'],
    'css': ["static/src/css/cabecera_periodo.css"],

    'installable': True,
    'auto_install': False,
    'application': False,
}
