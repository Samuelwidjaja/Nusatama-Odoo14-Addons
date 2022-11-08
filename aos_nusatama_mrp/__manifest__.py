{
    'name': 'AOS MRP WIP Cost',
    'license': 'AGPL-3',
    'summary': """
        AOS MRP WIP Cost
        """,
    'version': '0.0.1',
    'category': 'mrp',
    'author': 'alphasoft',
    'description': """
        WIP entries as inventory post
    """,
    'depends': [
        'mrp','aos_bypass_reservation',
    ],
    'external_dependencies': {'python': [], 'bin': []},
    'data': [
        'views/stock_move.xml',
    ],
    'qweb':[
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    # 'post_init_hook':post_init.
}