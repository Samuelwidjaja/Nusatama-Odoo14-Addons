{
    'name': "Stock Report",
    'version': '1.0',
    'depends': ['base','stock','account','sale_stock','purchase_stock'],
    'author': "Alphasoft",
    'category': 'Report',
    'description': """
        This module inherited report quotation
    """,
    # data files always loaded at installation
    'data': [
        'views/stock.xml',
        'reports/report_stock_picking.xml',
        'reports/report_stock_bast.xml',
        'reports/report_good_receipt.xml',
        'reports/report_action.xml',
    ],
    # data files containing optionally loaded demonstration data
    'images':[
        'static/image/nusatama.png'
        'static/image/table.jpg'
    ]
}