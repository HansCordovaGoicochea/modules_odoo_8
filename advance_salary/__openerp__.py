# -*- coding: utf-8 -*-

{
    'name': "Adelanto de sueldo",
    'version': "8.0.1.0.0",
    'author': '',
    'company': '',
    'summary': 'Opción de pago por adelantado al empleado.',
    'website': '',
    'license': "AGPL-3",
    'category': "Human resources",
    'depends': ['hr', 'hr_payroll', 'hr_contract', 'hr_holidays'],
    'data': [
        "security/ir.model.access.csv",
        "views/salary_structure_view.xml",
        "views/salary_advance_menu.xml",
        "views/advance_rule_menu.xml",
        "views/journal_entry.xml",
        "data/catalogo_data.xml",
        "wizard/advance_salary_holidays_tree.xml",
    ],
    'installable': True,
    'active': False,
    'images': [''],
    'auto_install': False,
}
