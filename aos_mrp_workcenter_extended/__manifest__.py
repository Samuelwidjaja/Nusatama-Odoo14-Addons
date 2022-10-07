{
    'name': 'MRP Work Center Extended',
    'license': 'AGPL-3',
    'summary': """
        - Adding Flow sequential process of WO based on workcenter bom level
    """,
    'version': '0.0.1',
    'category': 'manufacturing',
    'author': 'La Jayuhni Yarsyah',
    'description': """
        - Adding Flow sequential process of WO based on workcenter bom level
    """,
    'depends': [
        'mrp'
    ],
    'external_dependencies': {'python': [], 'bin': []},
    'data': [
        'views/mrp_routing_views.xml',
        'views/mrp_workorder_views.xml',
    ],
    'qweb':[
    ],
    'assets':{
    },
    'installable': True,
    'auto_install': False,
    'application': True,
}