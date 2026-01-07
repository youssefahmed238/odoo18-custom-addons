from odoo import models, fields, api


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    # Example state field
    example_state = fields.Selection([
        ('draft', "Draft"),
        ('in_process', "In Process"),
        ('paid', "Paid"),
        ('canceled', "Canceled"),
        ('rejected', "Rejected"),
    ], string='Example State', default='draft', tracking=True)
