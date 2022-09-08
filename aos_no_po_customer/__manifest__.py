{
    'name': 'Generic Module - No PO Customer on SO, DO and Invoice',
    'summary': 'Generic Module - No PO Customer on SO, DO and Invoice',
    'description': """
 - Add No. PO Customer in SO, DO and Invoice   
    """,
    'version': '15.0.1.0.0',
    'author': 'Alphasoft',
    'website': 'https://www.alphasoft.co.id',
    'category': 'Sales',
    'depends': ['stock', 'sale', 'sale_stock', 'account'],
    'data': [
        'views/stock_picking_views.xml',
        'views/account_move_views.xml',
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
