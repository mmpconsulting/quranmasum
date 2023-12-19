{
    'name': 'Dynamic Odoo',
    'summary': 'Dynamic Odoo',
    'version': '1.0',
    'category': 'Web',
    'description': """
        Dynamic Odoo. Customize and Build Odoo View on the fly without any technical knowledge
    """,
    'author': "truongdung.vd@gmail.com",
    'depends': ['web', "web_editor", "base_automation"],
    'data': [
        'views/templates.xml',
        'views/ir_ui_menu_view.xml',
        'views/report_kanban_view.xml',
        'security/view_dynamic_security.xml',
        'security/ir.model.access.csv',
    ],
    'qweb': [
        'static/src/xml/form_edit.xml',
        'static/src/xml/base.xml',
        'static/src/xml/form_fields.xml',
        'static/src/xml/kanban_template.xml',
        'static/src/xml/report_edit.xml',
    ],
    'images': ['images/main_screen.jpg'],
    'price': 450,
    'license': 'OPL-1',
    'currency': 'EUR',
    'installable': True,
    'auto_install': False,
    'application': False,
    'images': [
        'static/description/module_image.jpg',
    ],
}
