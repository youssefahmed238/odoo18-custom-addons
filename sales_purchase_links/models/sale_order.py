from odoo import models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_create_rfq(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'view_mode': 'form',
            'target': 'current',
        }
