{
    'name': "Aos Split Manufacturing Order",
    'category': "Manufacturing",
    'version': "14.0.1.0",
    'author': 'Equick ERP',
    'description': """
        This allows you to split manufacturing order.
    """,
    'summary': """split mo split mrp order split manufacturing order by number of quantity split manufacturing order by number of split manufacturing order split production order split manufacturing splitting split by number of order mrp split by number of order""",
    'depends': ['base', 'mrp'],
    'price': 20,
    'currency': 'EUR',
    'license': 'OPL-1',
    'website': "",
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/wizard_split_mo_view.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
