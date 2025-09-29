from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    source_purchase_order_id = fields.Many2one(
        comodel_name="purchase.order",
        string="Source Purchase Order",
        readonly=True,
    )

    @api.depends('order_line.purchase_line_ids.order_id', 'source_purchase_order_id')
    def _compute_purchase_order_count(self):
        """Override the standard method to include both direct and dropship purchase orders"""
        for order in self:
            # Get dropship purchase orders (need actual records for deduplication)
            purchase_orders_dropship = order.order_line.purchase_line_ids.order_id

            # Use search_count for direct purchases, but we need to combine with dropship
            # so we still need the actual records for deduplication
            purchase_orders_direct = self.env['purchase.order'].search([
                ('source_sale_order_id', '=', order.id)
            ])

            # Combine and remove duplicates
            all_purchase_orders = (purchase_orders_dropship | purchase_orders_direct)
            order.purchase_order_count = len(all_purchase_orders)

    def action_view_purchase_orders(self):
        """Override the standard method to show both direct and dropship purchase orders"""
        self.ensure_one()

        purchase_orders_dropship = self.order_line.purchase_line_ids.order_id

        purchase_orders_direct = self.env['purchase.order'].search([
            ('source_sale_order_id', '=', self.id)
        ])

        all_purchase_orders = (purchase_orders_dropship | purchase_orders_direct)

        action = {
            'type': 'ir.actions.act_window',
            'name': 'Purchase Orders',
            'res_model': 'purchase.order',
            'view_mode': 'list,form',
            'domain': [('id', 'in', all_purchase_orders.ids)],
            'context': {'default_source_sale_order_id': self.id},
        }

        if len(all_purchase_orders) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': all_purchase_orders.id,
                'views': [(False, 'form')]
            })

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
