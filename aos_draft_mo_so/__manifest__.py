# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Generate draft MO from Sales Order with MTO',
    'version': '14.0.0.1.0',
    'license': 'OPL-1',
    'summary': 'Generate draft MO from Sales Order with MTO by Alphasoft',
    'sequence': 1,
    "author": "Alphasoft",
    'description': """
        Generate draft MO from Sales Order with MTO'
    """,
    'category' : 'Tools',
    'website': 'https://www.alphasoft.co.id/',
    'images':  ['images/main_screenshot.png'],
    'depends' : ['mrp','stock', 'product'],
    'data': [
        'views/mrp_inherited.xml',
    ],
    'demo': [],
    'test': [],
    'qweb': [],
    'css': [],
    'js': [],
    'price': 10.00,
    'currency': 'EUR',
    'installable': True,
    'application': False,
    'auto_install': False,
}