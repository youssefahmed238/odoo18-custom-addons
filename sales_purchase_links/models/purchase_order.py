from odoo import models, fields, api


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

    @api.depends('source_sale_order_id')
    def _compute_sale_order_count(self):
        """Override the standard method to  include linked sale orders"""
        for order in self:
            order.sale_order_count = self.env['sale.order'].search_count([
                ('source_purchase_order_id', '=', order.id)
            ])

    def action_view_sale_orders(self):
        """Override the standard method to show linked sale orders"""
        self.ensure_one()

        sale_orders_direct = self.env['sale.order'].search([
            ('source_purchase_order_id', '=', self.id)
        ])

        action = {
            'type': 'ir.actions.act_window',
            'name': 'Sale Orders',
            'res_model': 'sale.order',
            'view_mode': 'list,form',
            'domain': [('id', 'in', sale_orders_direct.ids)],
            'context': {'default_source_purchase_order_id': self.id},
        }

        if len(sale_orders_direct) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': sale_orders_direct.id,
                'views': [(False, 'form')]
            })

        return action

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
