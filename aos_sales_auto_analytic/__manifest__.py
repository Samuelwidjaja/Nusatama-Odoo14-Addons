# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Aos Sales Auto Analytic',
    'version': '14.0.0.1.0',
    'license': 'OPL-1',
    'summary': 'Auto Analytic',
    'sequence': 1,
    "author": "Alphasoft",
    'description': """
Account Voucher
====================
    """,
    'category' : 'Tools',
    'website': 'https://www.alphasoft.co.id/',
    'images':  ['images/main_screenshot.png'],
    'depends' : ['account', 'sale_management', 'purchase', 'stock'],
    'data': [
        'views/sale_inherit.xml',
            
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