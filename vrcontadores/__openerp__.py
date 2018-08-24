# -*- coding: utf-8 -*-
{
    'name': "vrcontadores",

    'summary': """
        Añade conexión con sunat/reniec""",

    'description': """
        Permite recibir los datos de sunat/reniec mediante el documento de identificación
    """,

    'author': "scientechperu",
    'website': "http://www.scientechperu.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['web', 'base','calendar','web_calendar'],

    # always loaded
    'data': [
        'security/vrcontadores_security.xml',
        'security/ir.model.access.csv',
        'vrcontadores.xml',
        'vrcontadores_data.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo.xml',
    ],
}