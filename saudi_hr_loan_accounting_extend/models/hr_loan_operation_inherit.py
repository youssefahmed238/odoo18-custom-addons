from datetime import datetime

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HRLoanInherits(models.Model):
    _inherit = 'hr.loan.operation'

    payment_type = fields.Selection(
        selection_add=[('journal_entry','NO Payslip')],
    )

    account_journal = fields.Many2one('account.journal',
                                      string='Payment Account',
                                      domain=[('type', 'in', ['cash', 'bank'])],
                                      copy=False,
                                      help='Select the payment journal for this operation.')

    installment_account = fields.Many2one('account.account',
                                          string='Installment Account',
                                          copy=False,
                                          help='Select the payment journal for this operation.')

    def create_operation_journal_entry(self, loan_amount):
        # payment --> credit
        # installment --> debit
        if self.account_journal and self.installment_account:
            self.ensure_one()

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
                'date': datetime.now(),
                'state': 'draft',
                'move_type': 'entry',
                'journal_id': self.account_journal.id,
                'line_ids': move_line_vals,
            })

        else:
            raise ValidationError(
                'Please make sure that Installment and payment journals are selected')

    def approve_loan_operation(self):
        if self.loan_operation_type == 'loan_payment':
            loan_amount = self.loan_id.amount_to_pay if self.loan_payment_type == 'fully' else self.payment_amount
            self.create_operation_journal_entry(loan_amount)

            if self.payment_type != 'by_payslip':
                # Create Installment line at loan record
                self.env['installment.line'].create({
                    'loan_id': self.loan_id.id,
                    'operation_id': self.id,
                    'employee_id': self.loan_id.employee_id.id,
                    'date': datetime.now(),
                    'amount': loan_amount,
                })

            if self.loan_id.amount_to_pay == 0:
                self.loan_id.state = 'done'

        res = super(HRLoanInherits,self).approve_loan_operation()

        return res

    def action_get_loan_operation_journal_entry(self):
        self.ensure_one()
        journal_entries = self.env['account.move'].search([('ref', '=', self.name),
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
                'name': _('Sources Loan Operation Payments %s', self.name),
                'domain': [('id', 'in', journal_entries.ids)],
                'view_mode': 'tree,form',
            })
        return action

    def set_to_draft(self):
        res = super(HRLoanInherits, self).set_to_draft()
        journal_entries = self.env['account.move'].search([('ref', '=', self.name),
                                                           ('journal_id', '=', self.account_journal.id),
                                                           ('state', 'in', ['posted', 'draft']),
                                                           ])

        journal_entries.filtered(lambda r: r.state == 'posted').button_draft()
        journal_entries.button_cancel()

        for installment_line in self.loan_id.installment_lines:
            if installment_line.operation_id.id == self.id:
                installment_line.unlink()

            if self.loan_id.state == 'done':
                self.loan_id.state = 'approve'

        return res
