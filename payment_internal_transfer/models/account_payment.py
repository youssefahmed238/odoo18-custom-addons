from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    is_internal_transfer = fields.Boolean(string="Internal Transfer", readonly=False, store=True,
                                          tracking=True, compute="_compute_is_internal_transfer")

    destination_journal_id = fields.Many2one(
        comodel_name='account.journal',
        string='Destination Journal',
        domain="[('type', 'in', ('bank','cash')), ('id', '!=', journal_id)]",
        check_company=True,
    )

    source_petty_employee_id = fields.Many2one('hr.employee', string='Source Petty Employee')
    destination_petty_employee_id = fields.Many2one('hr.employee', string='Destination Petty Employee')

    is_source_petty = fields.Boolean(related='journal_id.is_petty')
    is_destination_petty = fields.Boolean(related='destination_journal_id.is_petty')

    @api.depends('journal_id')
    def _compute_is_internal_transfer(self):
        for payment in self:
            payment.is_internal_transfer = payment.journal_id.is_petty

    @api.constrains('amount', 'is_internal_transfer')
    def _check_amount(self):
        for payment in self:
            if payment.is_internal_transfer and payment.amount == 0:
                raise ValidationError(_("The amount must be greater than zero for internal transfers."))

    def _generate_journal_entry(self, write_off_line_vals=None, force_balance=None, line_ids=None):
        """ Override to add a check for outstanding_account_id when the payment is an internal transfer. """
        if self.is_internal_transfer and not self.outstanding_account_id:
            raise UserError(_(
                "You can't create a new payment without an outstanding payments/receipts account set either "
                "on the company or the %(payment_method)s payment method in the %(journal)s journal.",
                payment_method=self.payment_method_line_id.name, journal=self.journal_id.display_name))

        return super(AccountPayment, self)._generate_journal_entry(write_off_line_vals, force_balance, line_ids)
