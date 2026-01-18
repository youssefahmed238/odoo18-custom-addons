from datetime import datetime

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HRLoanInherits(models.Model):
    _inherit = 'hr.loan'

    apply_accounting = fields.Boolean("Apply Accounting", default=False)

    account_journal = fields.Many2one('account.journal',
                                      string='Payment Account',
                                      domain=[('type', 'in', ['cash', 'bank'])],
                                      required=True,
                                      copy=False,
                                      help='Select the payment journal for this operation.')

    installment_account = fields.Many2one('account.account',
                                          string='Installment Account',
                                          required=True,
                                          copy=False,
                                          help='Select the payment journal for this operation.')

    def pay_loan(self):
        # payment --> credit
        # installment --> debit
        if self.account_journal and self.installment_account and self.state == 'open':
            self.ensure_one()

            # Assuming you have the loan amount to be paid (e.g., self.loan_amount)
            loan_amount = self.loan_amount  # You need to define where this amount comes from

            # Create the journal entry lines
            move_line_vals = [
                # Debit line
                (0, 0, {
                    'account_id': self.installment_account.id,
                    'partner_id': self.env['res.partner'].search([('name', '=', self.employee_id.name)], limit=1).id,
                    'debit': loan_amount,
                    'credit': 0.0,
                    'name': 'Loan Payment',
                }),
                # Credit line
                (0, 0, {
                    'account_id': self.account_journal.default_account_id.id,
                    'debit': 0.0,
                    'credit': loan_amount,
                    'name': 'Loan Payment',
                }),
            ]

            # Create the journal entry
            self.env['account.move'].create({
                'ref': self.name,
                'date': self.due_date,
                'state': 'draft',
                'move_type': 'entry',
                'journal_id': self.account_journal.id,
                'line_ids': move_line_vals,
            })

        else:
            raise ValidationError(
                'Please make sure that Installment and payment journals are selected and loan is in Waiting Approval state')

    def action_get_loan_journal_entrie(self):
        self.ensure_one()

        journal_entries = self.env['account.move'].search([
            ('ref', '=', self.name),
            ('journal_id', '=', self.account_journal.id),
        ])

        action = {
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
        }
        if len(journal_entries) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': journal_entries[0].id,
            })
        else:
            action.update({
                'name': _('Sources Loan Payments %s', self.name),
                'domain': [('id', 'in', journal_entries.ids)],
                'view_mode': 'tree,form',
            })
        return action

    def approve_loan(self):
        self.ensure_one()
        if self.apply_accounting:
            self.pay_loan()
        res = super(HRLoanInherits, self).approve_loan()
        return res

    def set_to_draft(self):
        res = super(HRLoanInherits, self).set_to_draft()

        journal_entries = self.env['account.move'].search([
            ('ref', '=', self.name),
            ('journal_id', '=', self.account_journal.id),
        ])

        journal_entries.button_cancel()

        return res

    def set_to_cancel(self):
        res = super(HRLoanInherits, self).set_to_cancel()

        journal_entries = self.env['account.move'].search([
            ('ref', '=', self.name),
            ('journal_id', '=', self.account_journal.id),
        ])

        journal_entries.button_cancel()

        return res

