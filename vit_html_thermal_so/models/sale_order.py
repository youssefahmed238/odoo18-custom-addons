from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    using_thermal_printer = fields.Boolean(
        compute='_compute_using_thermal_printer'
    )

    def _compute_using_thermal_printer(self):
        user = self.env.user
        for order in self:
            order.using_thermal_printer = user.using_thermal_printer

    def print_order_thermal_report(self):
        return self.env.ref('vit_html_thermal_so.action_report_sale_order_thermal').report_action(self)
