{
    'name': 'AOS MRP Partial',
    'license': 'AGPL-3',
    'summary': """
        AOS MRP Partial
        Processing partial inventory post on mrp production""",
    'version': '0.0.1',
    'category': 'mrp',
    'author': 'La Jayuhni Yarsyah',
    'description': """
        Processing partial inventory post on mrp production
    """,
    'depends': [
        'mrp',
    ],
    'external_dependencies': {'python': [], 'bin': []},
    'data': [
        'security/ir.model.access.csv',
        'views/mrp_production.xml',
    ],
    'qweb':[
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    # 'post_init_hook':post_init.
}