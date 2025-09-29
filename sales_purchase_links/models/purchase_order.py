from odoo import models, fields


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    source_sale_order_id = fields.Many2one(
        comodel_name="sale.order",
        string="Source Sale Order",
        readonly=True,
    )

    sale_order_count = fields.Integer(
        string="Sales",
        compute="_compute_sale_order_count"
    )

    def _compute_sale_order_count(self):
        for order in self:
            order.sale_order_count = self.env['sale.order'].search_count([
                ('source_purchase_order_id', '=', order.id)
            ])

    def action_view_sale_orders(self):
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': 'Sale Orders',
            'res_model': 'sale.order',
            'view_mode': 'list,form',
            'domain': [('source_purchase_order_id', '=', self.id)],
            'context': {'default_source_purchase_order_id': self.id},
        }

    def action_create_quotation(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'form',
            'target': 'current',
            'context': {
                'default_source_purchase_order_id': self.id,
                'default_origin': self.name,
            }
        }
