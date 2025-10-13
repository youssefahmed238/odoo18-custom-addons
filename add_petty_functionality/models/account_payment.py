from odoo import models, fields, api, _


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    source_petty_employee_id = fields.Many2one('hr.employee', string='Source Petty Employee')
    destination_petty_employee_id = fields.Many2one('hr.employee', string='Destination Petty Employee')

    is_source_petty = fields.Boolean(related='journal_id.is_petty')
    is_destination_petty = fields.Boolean(related='destination_journal_id.is_petty')

    @api.depends('journal_id')
    def _compute_is_internal_transfer(self):
        """ Override to set internal transfer if the journal is petty. """
        for payment in self:
            payment.is_internal_transfer = payment.journal_id.is_petty

    def _prepare_move_line_default_vals(self, write_off_line_vals=None, force_balance=None):
        """ Override to set petty_employee on move lines for internal transfers. """
        line_vals = super(AccountPayment, self)._prepare_move_line_default_vals(write_off_line_vals, force_balance)

        if self.is_internal_transfer:
            line_vals[0]['petty_employee'] = self.source_petty_employee_id.id if self.is_source_petty else False

        return line_vals

    def _create_paired_internal_transfer_payment(self):
        """ Override to add petty employee to the paired payment. """""
        for payment in self:
            # Get available payment methods for the destination journal and payment type
            destination_journal = payment.destination_journal_id
            new_payment_type = 'inbound' if payment.payment_type == 'outbound' else 'outbound'
            available_methods = destination_journal._get_available_payment_method_lines(new_payment_type)

            paired_payment = payment.copy({
                'journal_id': destination_journal.id,
                'source_petty_employee_id': payment.destination_petty_employee_id.id if payment.is_destination_petty else False,
                'destination_journal_id': payment.journal_id.id,
                'destination_petty_employee_id': payment.source_petty_employee_id.id if payment.is_source_petty else False,
                'payment_type': new_payment_type,
                'move_id': None,
                'paired_internal_transfer_payment_id': payment.id,
                'date': payment.date,
                'payment_method_line_id': available_methods[0].id if available_methods else False,
            })

            paired_payment.action_post()

            payment.paired_internal_transfer_payment_id = paired_payment
            body = _("This payment has been created from:") + payment._get_html_link()
            paired_payment.message_post(body=body)
            body = _("A second payment has been created:") + paired_payment._get_html_link()
            payment.message_post(body=body)

            lines = (payment.move_id.line_ids + paired_payment.move_id.line_ids).filtered(
                lambda l: l.account_id == payment.destination_account_id and not l.reconciled)
            lines.reconcile()

            payment.state = 'paid'
            paired_payment.state = 'paid'
