# -*- coding: utf-8 -*-
{
    'name': 'Sale Order - Quotation Attachment',
    'version': '14.0.1.0.0',
    'summary': 'Add a quotation attachment field to sale.order',
    'description': 'Add fields to sale.order to upload a quotation file (binary) and filename.',
    'author': 'Samuel Widjaja',
    'license': 'AGPL-3',
    'depends': ['sale'],
    'data': [
	'report/report_saleorder_extend.xml',
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': False,
}
