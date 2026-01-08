# -*- coding: utf-8 -*-
{
    "name" : "Odoo Scrap Order for Multi Products Apps",
    "author": "Edge Technologies",
    "version" : "2.0",
    "live_test_url":'https://youtu.be/dp3q8HSb-LE',
    "images":["static/description/main_screenshot.png"],
    'summary': 'Multiple products scrap order for multi product scrap orders for multiple product scrap order create scrap order for multiple product scrap order mass product scrap order create scrap for multi product create scrap order for mass product scrap orders.',
    "description": """
        This app helps user to scrap multi product at ones.
    """,
    "license" : "OPL-1",
    "depends" : ['base','sale_management','stock'],
    "data": [
        'security/scrap_group.xml',
        'security/ir.model.access.csv',
        'data/stock_data.xml',
        'wizard/scrap_product_produce_views.xml',
        'views/scrap_order_view.xml',
        'views/stock_picking_view.xml',
    ],
    "auto_install": False,
    "installable": True,
    "price": 15,
    "currency": 'EUR',
    "category" : "Warehouse",
    
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

