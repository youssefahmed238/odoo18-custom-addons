from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class AccountPaymentRegisterInherit(models.TransientModel):
    _inherit = 'account.payment.register'

    bank_amount = fields.Float("Bank Amount", store=True)
    apply_bank_amount = fields.Boolean("Apply Bank Amount", related="journal_id.allow_on_payment", store=True)
    bank_charge_amount = fields.Float("Bank Charge Amount")
    bank_charge_amount_required = fields.Boolean("Bank Charge Amount Required", store=True,
                                                 compute="_compute_apply_bank_amount")

    @api.onchange('apply_bank_amount', 'amount')
    def _onchange_apply_bank_amount(self):
        if self.apply_bank_amount and self.payment_type == 'inbound':
            self.bank_amount = self.amount * (self.journal_id.payment_bank_charge_percentage / 100.0)

    @api.depends('payment_type', 'apply_bank_amount')
    def _compute_apply_bank_amount(self):
        for record in self:
            record.bank_charge_amount_required = (record.apply_bank_amount and record.payment_type == 'outbound')

    @api.constrains('bank_charge_amount_required', 'bank_charge_amount')
    def _check_bank_charge_amount(self):
        for record in self:
            if record.bank_charge_amount_required and record.bank_charge_amount < 0:
                raise ValidationError(
                    _("Bank Charge Amount is required for send payment in case of bank charge journal."
                      "and must be greater than 0."))

    def extend_result_for_bank_charge(self, res):
        # Calculate the bank charge amount based on the context (inbound or outbound)
        if self.apply_bank_amount:
            bank_charge_amount = int((self.amount * (
                    self.journal_id.payment_bank_charge_percentage / 100.0)) * 100) / 100 if self.payment_type == 'inbound' else self.bank_charge_amount
            res.update({
                'is_from_register_wizard': True,
                'payment_allow_bank_charge': self.apply_bank_amount,
                'bank_charge_amount': bank_charge_amount,
                'fixed_bank_charge_amount': bank_charge_amount,
                'payment_bank_charge_type': self.journal_id.payment_bank_charge_type,
            })
            if self.journal_id.payment_taxes_on_bank_charge:
                # Taxes on bank charge
                res.update({
                    'allow_tax_on_bank_charge': True,
                    'tax_on_bank_charge_amount': int(
                        (bank_charge_amount * (self.journal_id.payment_tax_percentage / 100)) * 100) / 100,
                    'payment_taxes_on_bank_charge_type': self.journal_id.payment_taxes_on_bank_charge_type
                })

        return res

    def _create_payment_vals_from_wizard(self, batch_result):
        res = super(AccountPaymentRegisterInherit, self)._create_payment_vals_from_wizard(batch_result)
        return self.extend_result_for_bank_charge(res)

    def _create_payment_vals_from_batch(self, batch_result):
        res = super(AccountPaymentRegisterInherit, self)._create_payment_vals_from_batch(batch_result)
        return self.extend_result_for_bank_charge(res)
