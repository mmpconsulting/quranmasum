# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
# Copyright AHA Tech

{
    'name': 'CPK CPB',
    'author': 'AHATECH',
    'category': 'Manufacturing',
    'version': '1.0',
    'description':
        """
CPK CPB
========================

        """,
    'depends': ['web', 'mrp'],
    'auto_install': False,
    'installable': True,
    'application': True,
    'data': [
        # # Configuration
        'data/ir_config_parameter_data.xml',
        'views/res_config_settings.xml',
        
        # # REPORTING
        'views/report_templates.xml',
        'report/cpk_cpb_report.xml',
        'report/pengolahan_report_templates.xml',
        'report/pengemasan_report_templates.xml',
        'report/paper_format.xml',

        'security/ir.model.access.csv',
        'views/product_template_views.xml',
        'views/mrp_alat_ruang_views.xml',
        'views/mrp_production_views.xml',
        'views/mrp_bom_views.xml',
        'wizard/mrp_production_penimbangan_views.xml',
        'wizard/mrp_production_pencampuran_views.xml',
        'wizard/mrp_production_filling_kapsul_views.xml',
        'wizard/mrp_production_filling_primer_views.xml',
        'wizard/mrp_production_evaluasi_views.xml',
        'wizard/mrp_production_prosedur_pengemasan_views.xml',
        'wizard/mrp_production_pengawasan_pengemasan_views.xml',
        'wizard/mrp_production_rekonsiliasi_pengemasan_views.xml',
    ],
    'license': 'LGPL-3',
}