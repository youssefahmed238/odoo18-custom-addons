from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    source_purchase_order_id = fields.Many2one(
        comodel_name="purchase.order",
        string="Source Purchase Order",
        readonly=True,
    )

    purchase_count = fields.Integer(
        string="Purchase",
        compute="_compute_purchase_count"
    )

    def _compute_purchase_count(self):
        for order in self:
            order.purchase_count = self.env['purchase.order'].search_count([
                ('source_sale_order_id', '=', order.id)
            ])

    def action_view_purchase_orders(self):
        self.ensure_one()

        action = {
            'type': 'ir.actions.act_window',
            'name': 'Purchase Orders',
            'res_model': 'purchase.order',
            'view_mode': 'list,form',
            'domain': [('source_sale_order_id', '=', self.id)],
            'context': {'default_source_sale_order_id': self.id},
        }

        purchase_orders = self.env['purchase.order'].search([
            ('source_sale_order_id', '=', self.id)
        ])

        if len(purchase_orders) == 1:
            action['view_mode'] = 'form'
            action['res_id'] = purchase_orders.id
            action['views'] = [(False, 'form')]

        return action

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
