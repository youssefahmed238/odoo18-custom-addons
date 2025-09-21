# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Inventory Report 2',
    'version': '17.0.0.1.0',
    'summary': 'Manage stock ',
    'description': "",
    'author': 'Mohamed Salem',
    'depends': ['product', 'barcodes', 'stock'],
    'category': 'Inventory/Inventory',
    'sequence': 25,
    'data': [
        'views/stock_quant_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
