{
    'name': 'Warehouse Products',
    'version': '1.0',
    'author': 'Youssef Ahmed',
    'category': 'Inventory',
    'depends': ['stock'],
    'data': [
        # Security
        'security/ir.model.access.csv',

        # Views
        'views/warehouse_products_dashboard_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
