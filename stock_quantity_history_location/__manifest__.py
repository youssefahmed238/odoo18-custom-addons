# Copyright 2019 ForgeFlow S.L.
# Copyright 2019 Aleph Objects, Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Stock Quantity History Location",
    "summary": "Provides stock quantity by location on past date",
    "version": "2.0",
    "license": "AGPL-3",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "maintainers": [
        "luisg123v",
        "rolandojduartem",
    ],
    "website": "https://github.com/OCA/stock-logistics-reporting",
    "depends": ["stock"],
    "data": ["wizards/stock_quantity_history.xml", "views/inherit_stock_quantity_view.xml"],

}
