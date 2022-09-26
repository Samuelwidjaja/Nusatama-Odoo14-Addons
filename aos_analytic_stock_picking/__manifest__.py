# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Aos Account Analytic So To Stock Picking',
    'version': '14.0.0.1.0',
    'license': 'OPL-1',
    'summary': 'Aos Account Analytic So To Stock Picking',
    'sequence': 1,
    "author": "Alphasoft",
    'description': """
        Aos Account Analytic So To Stock Picking'
    """,
    'category' : 'Tools',
    'website': 'https://www.alphasoft.co.id/',
    'images':  ['images/main_screenshot.png'],
    'depends' : ['mrp','aos_sales_auto_analytic', "mrp_analytic","stock",'stock_analytic'],
    'data': [
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