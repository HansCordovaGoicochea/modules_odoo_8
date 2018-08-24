# -*- coding: utf-8 -*-

{
    'name' : 'Comprobantes SUNAT',
    'version' : '1.0',
    'author' : 'Scientech',
    'category' : 'Accounting & Finance',
    'summary': 'Generacion de comprobantes SUNAT.',
    'license': 'AGPL-3',
    'contributors': [
        'Scientech',
    ],
    'description' : """
Comprobantes SUNAT.
====================================

Tablas:
--------------------------------------------
    * Tablas requeridas por la Factura electrónica

    """,
    'website': 'http://odooperu.pe/page/contabilidad',
    'depends' : ['account','account_accountant','mail','contacts','email_template'],
    'data': [
        'security/ir.model.access.csv',
        'views/comunicacion_from_invoice_view_lines.xml',
        'wizard/account_statement_from_invoice_view2.xml',
        'views/einvoice_view.xml',
        'data/einvoice_data.xml',
        'views/sec.xml',
        'views/email.xml',
        'views/report_nota_credito.xml',
        'views/report_nota_debito.xml',

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
        'static/description/banner.png',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    "sequence": 1,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
