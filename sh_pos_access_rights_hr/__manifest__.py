# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

{
    "name": "Point Of Sale Access Rights - Change Cashier Supported | Point Of Sale Access Rights | Different Access Rights For Employee | Access Rights For Cashier",
    "author": "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",
    "category": "Point Of Sale",
    "license": "OPL-1",
    "summary": "Restrict Access Point Of Sale POS Disable Customer Button POS Deny Numpad POS Restrict Plus-Minus Buttons POS Disable Quantity Button POS Discount Disable POS Payment Button Disable POS Disable Pric POS Access Rights For Cashier Odoo",
    "description": """POS access rights module allows you to set access rights for different cashiers so when you switch cashier that cashier access rights will be changed based on configuration. You can easily manage specific access for a particular cashier.""",
    "version": "16.0.3",
    "depends": ["point_of_sale", "pos_hr"],
    "application": True,
    "data": [
        'views/hr_employee_views.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'sh_pos_access_rights_hr/static/src/js/models.js',
            'sh_pos_access_rights_hr/static/src/js/Screens/screens.js',
            'sh_pos_access_rights_hr/static/src/css/pos.css',
        ],
    },
    "auto_install": False,
    "installable": True,
    "images": ["static/description/background.png", ],
    "price": "40",
    "currency": "EUR"
}
