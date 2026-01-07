from odoo import models, fields, api


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    # Example state field
    example_state = fields.Selection([
        ('draft', "Draft"),
        ('assembly', "Assembly underway"),
        ('collection', "Collection area"),
        ('loaded', "Car has been loaded"),
        ('delivered', "Delivered"),
    ], string='Example State', default='draft', tracking=True, required=True)
