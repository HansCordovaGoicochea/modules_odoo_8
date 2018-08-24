# -*- coding: utf-8 -*-
{
    "name": """Horario de Empleados\
    """,
    'version': '8.0.0.0.0',
    'category': 'hr/Employee',
    'sequence': 12,
    'author':  'H',
    'website': 'http://h.com',
    'license': 'AGPL-3',
    'summary': '',
    'description': """
.
===============================================================
""",
    'depends': [
        'report',
        'base',
        'hr',
        'hr_payroll',
        'hr_contract',
        'hr_holidays',
        'decimal_precision',
        'hr_timesheet_sheet',
        'hr_attendance',
        'hr_timesheet'
        ],
    'data': [
        'security/ir.model.access.csv',
        'views/empleados.xml',
        # 'views/empleados_data.xml',
        'views/emp.xml',
        'views/wizard_estructura_4.xml',
        'views/reporte_nominas_empleados_view.xml',
        'views/report_nominas_empleados_pdf.xml',
        'wizard/reporte_excel_asistencias_view.xml',
        'views/report_liquidacion_empleado_pdf.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
