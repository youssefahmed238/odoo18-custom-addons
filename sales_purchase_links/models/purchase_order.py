from odoo import models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def action_create_quotation(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'form',
            'target': 'current',
        }
