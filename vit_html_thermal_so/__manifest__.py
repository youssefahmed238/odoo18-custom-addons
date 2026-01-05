{
    'name': 'Sales Order Thermal Report',
    'version': '1.0',
    'author': 'Youssef Ahmed',
    'category': 'Sales',
    'depends': ['sale_management', 'vit_html_thermal_base'],
    'data': [
        'views/sale_order_view.xml',

        'reports/sale_order_report_views.xml',
        'reports/report_sale_order_thermal.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
