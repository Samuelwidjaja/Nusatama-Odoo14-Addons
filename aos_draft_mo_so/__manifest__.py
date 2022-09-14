# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Aos Draft Mo From So',
    'version': '14.0.0.1.0',
    'license': 'OPL-1',
    'summary': 'Aos Draft Mo From So',
    'sequence': 1,
    "author": "Alphasoft",
    'description': """
        Aos Draft Mo From So'
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
    'price': 15.00,
    'currency': 'EUR',
    'installable': True,
    'application': False,
    'auto_install': False,
}