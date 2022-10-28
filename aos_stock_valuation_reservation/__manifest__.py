{
    'name': "Stock Valuation Reservation",
    'version': '1.0',
    'depends': ['base','stock_account',],
    'author': "Alphasoft",
    'category': 'Inventory/Inventory',
    'description': """
        
    """,
    # data files always loaded at installation
    'data': [
        'security/ir.model.access.csv',
        'views/stock_move_views.xml',
        'views/stock_valuation_layer_views.xml',
        'views/stock_valuation_layer_reservation_views.xml',
    ],
    # data files containing optionally loaded demonstration data
    'images':[

    ]
}