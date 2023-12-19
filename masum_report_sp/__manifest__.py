# -*- coding: utf-8 -*-
# Part of Odoo, odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'masum_report_sp',
    'author': 'Tinton Aji Sadewo',
    'version': '1.1',
    'category': 'masum_report_sp',
    'description': """
Add additional date information to the sales order.
===================================================

You can add the following additional dates to a sales order:
------------------------------------------------------------
    * Requested Date (will be used as the expected date on pickings)
    * Commitment Date
    * Effective Date
""",
    'website': 'https://odoohq.com/page/crm',
    'depends': ['sale', ],
    'data': [
        'report/masum_report_sp_head.xml',
        'report/report_masum_report_sp_doc.xml',
        'report/report.xml',

    ],
}
