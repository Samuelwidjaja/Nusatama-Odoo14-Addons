{
    'name': "Bypass Reservation",
    'version': '1.0',
    'depends': ['base','stock',],
    'author': "Alphasoft",
    'category': 'Inventory/Inventory',
    'description': """
        This module will store should_bypass_reservation into database column, and will use column value if the field called
    """,
    # data files always loaded at installation
    'data': [
        'views/stock_location_views.xml',
    ],
    # data files containing optionally loaded demonstration data
    'images':[

    ]
}