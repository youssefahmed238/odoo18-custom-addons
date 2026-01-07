from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    using_thermal_printer = fields.Boolean(
        compute='_compute_using_thermal_printer'
    )

    def _compute_using_thermal_printer(self):
        user = self.env.user
        for order in self:
            order.using_thermal_printer = user.using_thermal_printer

    def print_invoice_thermal_report(self):
        return self.env.ref('vit_html_thermal_invoice.action_report_invoice_thermal').report_action(self)
