{
    'name': 'Sale Product Configurator Fields',
    'author': 'Youssef Ahmed',
    'version': '1.0',
    'category': 'Sales',
    'depends': ['sale', 'website_sale'],
    'assets': {
        'web.assets_backend': [
            'sale_product_configurator_fields/static/src/js/sale_product_field.js',
            'sale_product_configurator_fields/static/src/js/product_configurator_dialog.js',
            'sale_product_configurator_fields/static/src/js/product_list.js',
            'sale_product_configurator_fields/static/src/xml/product_configurator_dialog.xml',
        ],
    },
    'application': False,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
