# -*- coding: utf-8 -*-
{
    'name': "Modulo Valorizaciones",

    'summary': """
        Modulo Valorizaciones""",

    'description': """
       El Modulo de Valorizaciones ...
    """,

    'author': "http://www.scientechperu.com/",
    'website': "http://www.scientechperu.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Empresarial',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr', 'hr_timesheet_sheet', 'timesheet_task', 'fleet', 'report', 'mail','email_template'],

    # always loaded
    'data': [
        'security/valorizaciones_security.xml',
        'security/ir.model.access.csv',
        'wizard/wizard_tareos.xml',
        'templates.xml',
        'views/report_linea_credito.xml',
        'views/report_check_list.xml',
        'views/template_email_docs.xml',
        'valorizaciones_data.xml',
        'views/tareo_summ_view.xml',
        'views/report_proforma.xml',
        'valorizaciones_report.xml',
        'views/email.xml',

    ],
    'js': ['static/src/js/tareo_vehiculo_summary.js', 'static/src/js/cabecera_meses.js'],
    'qweb': ['static/src/xml/tareo_vehiculo_summary.xml', 'static/src/xml/cabecera_meses.xml'],
    'css': ["static/src/css/vehiculo_summary.css", "static/src/css/cabecera_meses.css"],
    # only loaded in demonstration mode
    'demo': [
        # 'demo.xml',
    ],
}