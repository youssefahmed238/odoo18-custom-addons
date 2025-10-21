{
    'name': 'Website Product Quantity Buttons',
    'version': '1.0',
    'summary': 'Add quantity + / - buttons to website product cards',
    'depends': ['website_sale'],
    'data': ['views/website_sale_templates.xml'],
    'assets': {
        'web.assets_frontend': [
            '/vit_website_product_qty_buttons/static/src/js/product_qty.js',
            '/vit_website_product_qty_buttons/static/src/css/product_qty.css',
        ],
    },
    'installable': True,
}
