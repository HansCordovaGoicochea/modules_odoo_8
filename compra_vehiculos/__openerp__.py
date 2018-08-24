# -*- coding: utf-8 -*-
{
    "name": """Compra Vehiculos""",
    'version': '8.0.0.0.1',
    'category': 'Accoun/invoice',
    'sequence': 12,
    'author':  'H',
    'website': 'http://h.com',
    'license': 'AGPL-3',
    'summary': '',
    'description': """
Compra de vehiculos.
===============================================================
""",
    'depends': [
        'modulo_valorizaciones',
        ],
    'data': [
        #'security/ir.model.access.csv',
        'views/compra_vehiculos.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
