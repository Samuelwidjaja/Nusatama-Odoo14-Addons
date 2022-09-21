# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Aos Add BOM From MO',
    'version': '14.0.0.1.0',
    'license': 'OPL-1',
    'summary': 'BOM Manufacturing',
    'sequence': 1,
    "author": "Alphasoft",
    'description': """
        Aos BOM add component from  Manufacturing Order'
    """,
    'category' : 'Tools',
    'website': 'https://www.alphasoft.co.id/',
    'images':  ['images/main_screenshot.png'],
    'depends' : ['mrp','stock', 'product'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/add_component.xml',
        'views/mrp_bom.xml',
    ],
    'demo': [],
    'test': [],
    'qweb': [],
    'css': [],
    'js': [],
    'price': 15.00,
    'currency': 'EUR',
    'installable': True,
    'application': False,
    'auto_install': False,
}