from odoo import models, fields


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    is_internal_transfer = fields.Boolean(string="Internal Transfer", readonly=False, store=True,
                                          tracking=True, compute="_compute_is_internal_transfer")

    def _compute_is_internal_transfer(self):
        # wait adding destination_journal_id field
        pass
