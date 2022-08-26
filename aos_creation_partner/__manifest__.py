# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Disable Quick Create Partner and User Restriction For Creating Partner',
    'version': '14.0.0.1.0',
    'license': 'OPL-1',
    'summary': 'Disable Quick Create Partner and User Restriction For Creating Partner',
    'sequence': 1,
    "author": "Alphasoft",
    'description': """
Partner
====================
    """,
    'category' : 'Tools',
    'website': 'https://www.alphasoft.co.id/',
    'images':  ['images/main_screenshot.png'],
    'depends' : ['account', 'sale_management', 'purchase', 'stock'],
    'data': [
        'security/ir_group.xml',
        'security/ir.model.access.csv',
        'views/sale_order_views.xml',
        'views/purchase_order_views.xml',
        'views/picking_views.xml',
        'views/account_move_views.xml',
        'views/product_supplierinfo_views.xml'
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
