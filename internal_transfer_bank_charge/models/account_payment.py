from odoo import models, fields, api, _, Command
from odoo.exceptions import UserError


class AccountPaymentInheritForPayment(models.Model):
    _inherit = "account.payment"

    allow_bank_charge_on_it = fields.Boolean(default=False)
    it_fixed_bank_charge_amount = fields.Float("Internal transfer fixed bank charge amount")
    related_bank_charge_account_id = fields.Many2one("account.journal", string="Related bank charge account")
    allowed_journals_ids = fields.Many2many("account.journal", string="Related bank charge account")
    charge_move_id = fields.Many2one("account.move", string="Charge move")

    @api.onchange("journal_id", "destination_journal_id", "is_internal_transfer", "payment_type")
    def _onchange_journal(self):
        # Only enable bank charge if all necessary fields are populated
        if self.journal_id and self.destination_journal_id and self.is_internal_transfer:
            self.allow_bank_charge_on_it = self.journal_id.allow_on_internal_transfer or self.destination_journal_id.allow_on_internal_transfer
            ids = []
            if self.journal_id.allow_on_internal_transfer: ids.append(self.journal_id.id)
            if self.destination_journal_id.allow_on_internal_transfer: ids.append(self.destination_journal_id.id)
            self.allowed_journals_ids = [(6, 0, ids)]
        else:
            self.allow_bank_charge_on_it = False

    @api.constrains('is_internal_transfer', 'destination_journal_id', 'journal_id', 'it_fixed_bank_charge_amount',
                    "payment_type")
    def _check(self):
        for record in self:
            if record.is_internal_transfer:
                if record.related_bank_charge_account_id:
                    if record.it_fixed_bank_charge_amount <= 0:
                        raise UserError("Internal transfer bank charge amount must be greater than zero.")
                else:
                    if record.allow_bank_charge_on_it:
                        raise UserError("Related bank charge account id must be set.")

    def _create_internal_transfer_bank_charge_move(self):

        for payment in self:
            if payment.charge_move_id:
                continue

            if self.env.context.get('skip_create_charge_move'):
                continue

            # Check if bank charge conditions are met
            if not (payment.allow_bank_charge_on_it and
                    payment.related_bank_charge_account_id and
                    payment.it_fixed_bank_charge_amount > 0):
                continue

            bank_charge_amount = payment.it_fixed_bank_charge_amount
            journal_id = payment.related_bank_charge_account_id
            tax_on_bank_charge_amount = (int((bank_charge_amount * (
                    journal_id.it_taxes_on_bank_charge_account_tax.amount / 100)) * 100)) / 100
            allow_tax_on_bank_charge = journal_id.it_taxes_on_bank_charge

            payment_ref = payment.payment_reference or payment.name

            # Prepare bank charge move lines
            bank_charge_vals = {
                'name': _(f"Bank Charge - {payment_ref or 'N/A'}"),
                'account_id': journal_id.it_bank_charge_account.id,
                'partner_id': payment.partner_id.id,
                'currency_id': payment.currency_id.id,
                'amount_currency': bank_charge_amount,
                'date_maturity': payment.date,
                'debit': bank_charge_amount,
                'credit': 0,
                'tax_ids': [(6, 0, journal_id.it_taxes_on_bank_charge_account_tax.ids)],
            }

            bank_cash_credit_vals = {
                'name': _(f"Bank Charge Reimbursement - {payment_ref or 'N/A'}"),
                'account_id': journal_id.default_account_id.id,
                'partner_id': payment.partner_id.id,
                'currency_id': payment.currency_id.id,
                'amount_currency': -(
                        bank_charge_amount + (tax_on_bank_charge_amount if allow_tax_on_bank_charge else 0.0)),
                'date_maturity': payment.date,
                'debit': 0,
                'credit': (bank_charge_amount + (tax_on_bank_charge_amount if allow_tax_on_bank_charge else 0.0)),
            }

            # Create journal entry
            move = self.env['account.move'].create({
                'move_type': 'entry',
                'date': payment.date,
                'journal_id': journal_id.id,
                'ref': f"{payment_ref or 'N/A'}",
                'line_ids': [
                    Command.create(bank_charge_vals),
                    Command.create(bank_cash_credit_vals),
                ],
            })

            # Post the move if it's in draft state
            if move.state == 'draft':
                move.action_post()

            # Link the move to the payment
            payment.charge_move_id = move.id if move else None

            # Add chatter messages
            payment_link = payment._get_html_link() or 'N/A'
            move.message_post(body=_("This move has been created from: ") + payment_link)

            move_link = move._get_html_link() if move else 'N/A'
            payment.message_post(body=_("A charge move has been created: ") + move_link)

    def _create_paired_internal_transfer_payment(self):
        """ Override to skip creating paired payment when creating bank charge move. """
        return super(AccountPaymentInheritForPayment,
                     self.with_context(skip_create_charge_move=True))._create_paired_internal_transfer_payment()

    def action_post(self):
        res = super(AccountPaymentInheritForPayment, self).action_post()

        self._create_internal_transfer_bank_charge_move()

        return res
