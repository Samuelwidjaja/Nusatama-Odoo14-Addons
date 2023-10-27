# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'MRP Timesheet',
    'version': '14.0.0.1.0',
    'license': 'OPL-1',
    'summary': 'Manufacturing Order Timesheet',
    'sequence': 1,
    "author": "Alphasoft - Imronsyabani",
    'description': """
        Manage Timesheet Manufacturing Order and Work Order 
    """,
    'category' : 'MRP',
    'website': 'https://www.alphasoft.co.id/',
    'images':  [],
    'depends' : ['mrp',
                 'analytic',
                 'project',
                 'hr',
    ],
    'data': [
        'views/mrp_production_view.xml',
        'views/mrp_timesheet_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}