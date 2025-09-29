from odoo import models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_create_rfq(self):
        print("Creating RFQ from Sale Order")
