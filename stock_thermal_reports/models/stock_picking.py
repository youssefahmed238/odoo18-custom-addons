from odoo import models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def print_picking_thermal_report(self):
        """Print picking thermal report directly"""

        return self.env.ref('stock_thermal_reports.action_report_picking_thermal').report_action(self)

    def print_delivery_thermal_report(self):
        """Print delivery slip thermal report directly"""
        return self.env.ref('stock_thermal_reports.report_deliveryslip_thermal').report_action(self)
