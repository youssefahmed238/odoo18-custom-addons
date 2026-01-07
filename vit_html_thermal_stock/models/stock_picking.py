from odoo import models, fields


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    using_thermal_printer = fields.Boolean(
        compute='_compute_using_thermal_printer'
    )

    def _compute_using_thermal_printer(self):
        user = self.env.user
        for order in self:
            order.using_thermal_printer = user.using_thermal_printer

    def print_picking_thermal_report(self):
        """Print picking thermal report directly"""

        return self.env.ref('vit_html_thermal_stock.action_report_picking_thermal').report_action(self)

    def print_delivery_thermal_report(self):
        """Print delivery slip thermal report directly"""
        return self.env.ref('vit_html_thermal_stock.action_report_delivery_thermal').report_action(self)
