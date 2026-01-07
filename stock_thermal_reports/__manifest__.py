{
    'name': 'Stock Thermal Reports',
    'version': '1.0',
    'author': 'Youssef Ahmed',
    'category': 'Inventory',
    'depends': ['stock', 'vit_html_thermal_base'],
    'data': [
        'views/stock_picking_view.xml',

        'reports/stock_report_views.xml',
        'reports/report_picking_thermal.xml',
        'reports/report_deliveryslip_thermal.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'stock_thermal_reports/static/src/js/report_action_override.js',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
