from odoo import models, fields, api


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    using_thermal_printer = fields.Boolean(
        compute='_compute_using_thermal_printer'
    )

    def _compute_using_thermal_printer(self):
        user = self.env.user
        for payment in self:
            payment.using_thermal_printer = user.using_thermal_printer

    def print_payment_thermal_report(self):
        return self.env.ref('vit_html_thermal_payment.action_report_payment_thermal').report_action(self)
