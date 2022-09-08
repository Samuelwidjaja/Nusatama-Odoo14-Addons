{
    'name': "Purchase Report",
    'version': '1.0',
    'depends': ['base','purchase','contacts'],
    'author': "Alphasoft",
    'category': 'Category',
    'description': """
    Description text
    """,
    # data files always loaded at installation
    'data': [
        # 'views/purchase_order.xml',
        'reports/report_purchase.xml',
        'reports/report.xml',
    ],
    # data files containing optionally loaded demonstration data
    # 'images':[
    #     'static/image/nusatama.png'
    #     'static/image/table.jpg'
    # ]
}