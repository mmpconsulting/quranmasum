# -*- coding: utf-8 -*-
{
    'name': "Employee's Contract Allowances",

    'summary': """
        Add allowance to your employees and add to your employee payslip automatically""",

    'description': """
        Add allowance to your employees and add to your employee payslip automatically 
    """,

    'author': "butirpadi",
    'website': "https://www.github.com/butirpadi",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'hr',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['hr_contract'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/hr_contract.xml',
        'views/hr_contract_allowance_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    "installable": True,
    'price': 60.00,
    'currency': 'EUR',
    'license': 'OPL-1',
    'images': ['static/description/main_screenshot.png'],
}
