from odoo import models, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to set sequence for reordering discount lines."""
        for vals in vals_list:
            line_seq = vals.get('sequence', False)

            if line_seq and line_seq >= 1000:
                order_id = vals.get('order_id')
                order = self.env['sale.order'].browse(order_id)

                last_product_sequence = max(
                    order.order_line
                    .filtered(lambda l: l.sequence < 999)
                    .mapped('sequence'),
                    default=0
                )

                vals['sequence'] = last_product_sequence + 1

        return super(SaleOrderLine, self).create(vals_list)
