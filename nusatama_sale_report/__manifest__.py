{
    'name': "Sales Report",
    'version': '1.0',
    'depends': ['base','sale'],
    'author': "Alphasoft",
    'category': 'Report',
    'description': """
        This module inherited report quotation
    """,
    # data files always loaded at installation
    'data': [
        'reports/report_saleorder.xml',
        # 'reports/report.xml'
    ],
    # data files containing optionally loaded demonstration data
    'images':[
        'static/image/nusatama.png'
        'static/image/table.jpg'
    ]
}