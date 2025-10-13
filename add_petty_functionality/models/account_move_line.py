from odoo import models, fields


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    petty_employee = fields.Many2one('hr.employee', string='Petty Employee', stor=True)
