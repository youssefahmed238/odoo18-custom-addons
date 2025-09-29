from odoo import models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_create_rfq(self):
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'view_mode': 'form',
            'target': 'current',
            'context': {
                'default_source_sale_order_id': self.id,
                'default_origin': self.name,
            }
        }
