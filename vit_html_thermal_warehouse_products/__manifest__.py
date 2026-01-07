{
    'name': 'Warehouse Products Thermal Report',
    'version': '1.0',
    'author': 'Youssef Ahmed',
    'category': 'Inventory',
    'depends': ['vit_warehouse_products', 'vit_html_thermal_base', 'web'],
    'data': [
        'reports/warehouse_product_report_views.xml',
        'reports/report_warehouse_product_thermal.xml'
    ],
    'assets': {
        'web.assets_backend_lazy': [
            'vit_html_thermal_warehouse_products/static/src/js/pivot_header_buttons.js',
            'vit_html_thermal_warehouse_products/static/src/xml/pivot_header_buttons.xml',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
