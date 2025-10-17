from odoo import models, fields, api, _, Command
from odoo.exceptions import UserError, ValidationError


class AccountPaymentInheritForPayment(models.Model):
    _inherit = "account.payment"

    payment_allow_bank_charge = fields.Boolean(default=False)
    bank_charge_amount = fields.Float(default=0.0)
    fixed_bank_charge_amount = fields.Float(default=0.0)
    payment_bank_charge_type = fields.Selection([
        ('balanced_amount', 'Balanced Amount'),
        ('deduct_from_original_amount', 'Deduct from Original Amount'),
        ('mixed', 'Mixed')
    ])
    allow_tax_on_bank_charge = fields.Boolean(default=False)
    tax_on_bank_charge_amount = fields.Float(default=0.0)
    payment_taxes_on_bank_charge_type = fields.Selection([
        ('balanced_amount', 'Balanced Amount'), ('deduct_from_original_amount', 'Deduct from Original Amount'),
    ])
    is_from_register_wizard = fields.Boolean()

    allow_on_payment = fields.Boolean(
        string="Allow On Payment",
        related='journal_id.allow_on_payment',
        store=True,
    )
    expense_sheet_id = fields.Many2one('hr.expense.sheet', string="Expense Sheet")
    charge_move_id = fields.Many2one("account.move", string="Charge move")

    @api.constrains('payment_type', 'is_internal_transfer', 'fixed_bank_charge_amount')
    def payment_type_allow_fixed_amount(self):
        for record in self:
            if (record.payment_type == 'outbound' and
                    not record.is_internal_transfer and
                    record.fixed_bank_charge_amount < 0 and
                    record.show_partner_bank_account):
                raise ValidationError(_('Fixed bank charge amount must be greater than 0 for record: %s' % record.id))

    # ----------------------------------------------------------------------------------------------------------------------
    def create_taxes_journal(self):
        for payment in self:
            if payment.journal_id.allow_on_payment and not payment.is_internal_transfer and ((
                                                                                                     payment.fixed_bank_charge_amount > 0.0 and payment.payment_type == 'outbound') or payment.payment_type == 'inbound'):
                bank_charge_amount = self.env['res.currency'].search([('name', '=', 'SAR')])._convert(
                    from_amount=int(((
                                             payment.amount * payment.journal_id.payment_bank_charge_percentage) / 100) * 100) / 100 if payment.payment_type == 'inbound' else payment.fixed_bank_charge_amount,
                    to_currency=payment.currency_id,
                    company=payment.company_id,
                    date=fields.Date.context_today(payment),
                )
                journal_id = payment.journal_id
                tax_on_bank_charge_amount = payment.currency_id._convert(
                    from_amount=(
                                        bank_charge_amount * journal_id.payment_taxes_on_bank_charge_account_tax.amount / 100) * 100 / 100,
                    to_currency=self.env['res.currency'].search([('name', '=', 'SAR')]),
                    company=payment.company_id,
                    date=fields.Date.context_today(payment),
                )
                payment_ref = payment.payment_reference or payment.name
                sr_currency = self.env['res.currency'].sudo().search([('name', '=', 'SAR')], limit=1)
                print("sr_currency", sr_currency)
                # Prepare bank charge move lines
                bank_charge_vals = {
                    'name': _(f"Bank Charge - {payment_ref or 'N/A'}"),
                    'account_id': journal_id.payment_bank_charge_account.id,
                    'partner_id': payment.partner_id.id,
                    'currency_id': sr_currency.id,
                    'amount_currency': int(((
                                                    payment.amount * payment.journal_id.payment_bank_charge_percentage) / 100) * 100) / 100 if payment.payment_type == 'inbound' else payment.fixed_bank_charge_amount,
                    'date_maturity': payment.date,
                    'debit': int(((
                                          payment.amount * payment.journal_id.payment_bank_charge_percentage) / 100) * 100) / 100 if payment.payment_type == 'inbound' else payment.fixed_bank_charge_amount,
                    'credit': 0,
                    'tax_ids': [(6, 0, journal_id.payment_taxes_on_bank_charge_account_tax.ids)],
                }

                percentage = int(
                    ((payment.amount * payment.journal_id.payment_bank_charge_percentage) / 100) * 100) / 100
                bank_cash_credit_vals = {
                    'name': _(f"Bank Charge Reimbursement - {payment_ref or 'N/A'}"),
                    'account_id': journal_id.default_account_id.id,
                    'partner_id': payment.partner_id.id,
                    'currency_id': sr_currency.id,
                    'amount_currency': -(
                            percentage + tax_on_bank_charge_amount) if payment.payment_type == 'inbound' else -(
                            payment.fixed_bank_charge_amount + tax_on_bank_charge_amount),
                    'date_maturity': payment.date,
                    'debit': 0,
                    'credit': percentage + tax_on_bank_charge_amount if payment.payment_type == 'inbound' else payment.fixed_bank_charge_amount + tax_on_bank_charge_amount
                }
                # Create journal entry
                move_dict = {
                    'move_type': 'entry',
                    'date': payment.date,
                    'journal_id': journal_id.id,
                    'ref': f"{payment_ref or 'N/A'}",
                    'line_ids': [
                        Command.create(bank_charge_vals),
                        Command.create(bank_cash_credit_vals),
                    ],
                }
                move = self.env['account.move'].create(move_dict)
                # Post the move if it's in draft state
                if move.state == 'draft':
                    move.action_post()
                # Link the move to the payment
                payment.charge_move_id = move.id if move else None
                # Add chatter messages
                move_link = move._get_html_link() if move else 'N/A'
                payment.message_post(body=_("A charge move has been created: ") + move_link)

    def action_post(self):
        res = super(AccountPaymentInheritForPayment, self).action_post()
        if self.env.context.get('skip_payment_post'):
            self.create_taxes_journal()
        return res

    def action_draft(self):
        res = super(AccountPaymentInheritForPayment, self).action_draft()
        if self.charge_move_id:
            self.charge_move_id.button_draft()
        return res
