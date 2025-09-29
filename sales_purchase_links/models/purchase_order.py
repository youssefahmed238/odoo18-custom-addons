from odoo import models, fields


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    source_sale_order_id = fields.Many2one(
        comodel_name="sale.order",
        string="Source Sale Order",
        readonly=True,
    )

    def action_create_quotation(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'form',
            'target': 'current',
        }
