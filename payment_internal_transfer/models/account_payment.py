from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools.misc import format_date, formatLang


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

    @api.constrains('amount', 'is_internal_transfer')
    def _check_amount(self):
        for payment in self:
            if payment.is_internal_transfer and payment.amount == 0:
                raise ValidationError(_("The amount must be greater than zero for internal transfers."))

    @api.depends('journal_id')
    def _compute_is_internal_transfer(self):
        for payment in self:
            payment.is_internal_transfer = payment.journal_id.is_petty

    @api.depends('journal_id', 'partner_id', 'partner_type', 'is_internal_transfer', 'destination_journal_id')
    def _compute_destination_account_id(self):
        """ Override to set the destination account for internal transfers. """
        for pay in self:
            if pay.is_internal_transfer:
                pay.destination_account_id = pay.destination_journal_id.company_id.transfer_account_id
            else:
                super(AccountPayment, pay)._compute_destination_account_id()

    @api.depends('is_internal_transfer')
    def _compute_partner_id(self):
        """ Override to set the partner for internal transfers. """
        for pay in self:
            if pay.is_internal_transfer:
                pay.partner_id = pay.journal_id.company_id.partner_id
            elif pay.partner_id == pay.journal_id.company_id.partner_id:
                pay.partner_id = False
            else:
                pay.partner_id = pay.partner_id

    @api.depends('payment_method_line_id.payment_account_id')
    def _compute_outstanding_account_id(self):
        """ Override to change dependency to payment method's payment account. """
        for pay in self:
            pay.outstanding_account_id = pay.payment_method_line_id.payment_account_id

    def _generate_journal_entry(self, write_off_line_vals=None, force_balance=None, line_ids=None):
        """ Override to add a check for outstanding_account_id when the payment is an internal transfer. """

        if self.is_internal_transfer and not self.outstanding_account_id:
                raise UserError(_(
                    "You can't confirm a payment without an outstanding payments/receipts account set either "
                    "on the company or the %(payment_method)s payment method in the %(journal)s journal.",
                    payment_method=self.payment_method_line_id.name, journal=self.journal_id.display_name))

        return super(AccountPayment, self)._generate_journal_entry(write_off_line_vals, force_balance, line_ids)

    def _prepare_move_line_default_vals(self, write_off_line_vals=None, force_balance=None):
        """ Override to set petty_employee on move lines for internal transfers. """
        line_vals = super(AccountPayment, self)._prepare_move_line_default_vals(write_off_line_vals, force_balance)

        line_vals[0]['name'] = ''.join(x[1] for x in self._get_aml_display_name_list(is_liquidity_line=True))
        line_vals[1]['name'] = ''.join(x[1] for x in self._get_aml_display_name_list())

        if self.is_internal_transfer:
            line_vals[0]['petty_employee'] = self.source_petty_employee_id.id if self.is_source_petty else False

        return line_vals

    def _get_aml_display_name_list(self, is_liquidity_line=False):
        """ Hook allowing custom values when constructing the label to set on the liquidity line.

        :return: A list of terms to concatenate all together. E.g.
            [('reference', "INV/2018/0001")]
        """
        self.ensure_one()
        if self.is_internal_transfer and is_liquidity_line:
            if self.payment_type == 'inbound':
                return [('transfer_to', _('Transfer to %s', self.journal_id.name))]
            else:  # payment.payment_type == 'outbound':
                return [('transfer_from', _('Transfer from %s', self.journal_id.name))]
        elif self.payment_reference:
            return [('reference', self.payment_reference)]
        else:
            return self._get_aml_default_display_name_list()

    def _get_aml_default_display_name_list(self):
        """ Hook allowing custom values when constructing the default label to set on the journal items.

        :return: A list of terms to concatenate all together. E.g.
            [
                ('label', "Vendor Reimbursement"),
                ('sep', ' '),
                ('amount', "$ 1,555.00"),
                ('sep', ' - '),
                ('date', "05/14/2020"),
            ]
        """
        self.ensure_one()
        display_map = self._get_aml_default_display_map()
        values = [
            ('label', _("Internal Transfer") if self.is_internal_transfer else display_map[
                (self.payment_type, self.partner_type)]),
            ('sep', ' '),
            ('amount', formatLang(self.env, self.amount, currency_obj=self.currency_id)),
        ]
        if self.partner_id:
            values += [
                ('sep', ' - '),
                ('partner', self.partner_id.display_name),
            ]
        values += [
            ('sep', ' - '),
            ('date', format_date(self.env, fields.Date.to_string(self.date))),
        ]
        return values

    def _get_aml_default_display_map(self):
        return {
            ('outbound', 'customer'): _("Customer Reimbursement"),
            ('inbound', 'customer'): _("Customer Payment"),
            ('outbound', 'supplier'): _("Vendor Payment"),
            ('inbound', 'supplier'): _("Vendor Reimbursement"),
        }

    def _create_paired_internal_transfer_payment(self):
        ''' When an internal transfer is posted, a paired payment is created
        with opposite payment_type and swapped journal_id & destination_journal_id.
        Both payments liquidity transfer lines are then reconciled.
        '''
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

    def action_post(self):
        """ Override to create the paired internal transfer payment when posting. """
        super(AccountPayment, self).action_post()

        self.filtered(
            lambda pay: pay.is_internal_transfer and not pay.paired_internal_transfer_payment_id
        )._create_paired_internal_transfer_payment()

    def action_cancel(self):
        """ Override to stop unlinking journal entry when canceling payment """
        self.state = 'canceled'
        self.move_id.button_cancel()
