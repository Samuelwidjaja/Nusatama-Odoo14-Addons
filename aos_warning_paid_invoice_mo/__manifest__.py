# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Manufacture Order & Invoice',
    'version': '14.0.0.1.0',
    'license': 'OPL-1',
    'summary': 'MO & Invoice',
    'sequence': 1,
    "author": "Alphasoft",
    'description': """
        Blocking Mo if customer from so have a invoice draft
    """,
    'category' : 'Extensions',
    'website': 'https://www.alphasoft.co.id/',
    'depends' : ['mrp','stock','base','account'],
    'data': [
        # 'security/ir.model.access.csv',
        # 'security/res_groups.xml',
        'views/mrp_production_views.xml',
        # 'wizard/warning_invoice_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}