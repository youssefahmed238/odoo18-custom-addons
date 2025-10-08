from odoo import models, fields, api


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    is_internal_transfer = fields.Boolean(string="Internal Transfer", readonly=False, store=True,
                                          tracking=True, compute="_compute_is_internal_transfer")

    @api.depends('journal_id')
    def _compute_is_internal_transfer(self):
        for payment in self:
            payment.is_internal_transfer = payment.journal_id.is_petty
