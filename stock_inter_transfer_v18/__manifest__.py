# -*- coding: utf-8 -*-
{
    'name': "Inter Warehouse Transfere",

    'summary': "Inter Warehouse Transfer",

    'description': """ Transfer stock from one warehouse to another warehouse Warehouse Transfer Bakery Goods """,

    'author': "Ahmed",
    'category': 'Inventory',
    'version': '18.0.2.6',

    'depends': ['stock', 'sale', 'product','warehouse_stock_restrictions','sale_stock'],

    'data': [
        "data/ir_sequence.xml",
        "security/ir.model.access.csv",
        "security/stock_transfer_security.xml",
        "views/stock_transfer_view.xml",
        "views/res_config_settings_view.xml",
        "views/res_users_view.xml",
        "report/delivery_slip.xml",
        "views/kit_wizard.xml",
        "views/stock_transfer_report.xml",
        "views/report_stock_transfer_document.xml",
        "views/stock_transfer_view_inherit_report_button.xml",
    ],
    'images': ['static/description/main_screen.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}

