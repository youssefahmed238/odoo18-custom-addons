from odoo import api, fields, models
from odoo.exceptions import ValidationError


class AccountJournalInherit(models.Model):
    _inherit = 'account.journal'

    allow_payment_bank_charge = fields.Boolean(string='Bank Charge', default=True, copy=False)

    # Payment Bank Charge
    allow_on_payment = fields.Boolean(string='Allow On Payment', default=False, copy=False)
    payment_bank_charge_account = fields.Many2one('account.account', string='Payment Bank Charge Account')
    payment_bank_charge_type = fields.Selection([
        ('balanced_amount', 'Balanced Amount'),
        ('deduct_from_original_amount', 'Deduct from Original Amount'),
        ('mixed', 'Mixed'),
    ])
    payment_bank_charge_percentage = fields.Float(string='Payment Bank Charge Percentage', default=0.0)
    payment_taxes_on_bank_charge = fields.Boolean(string='Taxes on Bank Charge', default=False, copy=False)
    payment_taxes_on_bank_charge_account_tax = fields.Many2one('account.tax', string='Taxes on Bank Charge Account')
    payment_tax_percentage = fields.Float(string='Taxes Percentage',
                                          related="payment_taxes_on_bank_charge_account_tax.amount")
    payment_taxes_on_bank_charge_type = fields.Selection([
        ('balanced_amount', 'Balanced Amount'),
        ('deduct_from_original_amount', 'Deduct from Original Amount')
    ])

    @api.constrains('payment_bank_charge_percentage', 'payment_tax_percentage')
    def _validate_user_data(self):

        def check_amount(value, field_label):
            if value < 0 or value > 100:
                raise ValidationError(f"{field_label} must be between 0 and 100!")

        validation_rules = {
            'payment_bank_charge_percentage': "Payment bank charge amount",
            'payment_tax_percentage': "Payment tax percentage",
        }

        if self.allow_on_payment:
            for field, label in [
                ('payment_bank_charge_percentage', validation_rules['payment_bank_charge_percentage'])]:
                check_amount(getattr(self, field), label)
            if self.payment_taxes_on_bank_charge:
                for field, label in [('payment_tax_percentage', validation_rules['payment_tax_percentage'])]:
                    check_amount(getattr(self, field), label)

    # Reset fields based on booleans values change
    @api.onchange('allow_payment_bank_charge', 'allow_on_payment', 'payment_taxes_on_bank_charge', )
    def _fields_validate(self):
        def reset_fields(fields):
            for field in fields:
                setattr(self, field, False)

        # Use match-case for pattern matching
        match (self.allow_payment_bank_charge, self.allow_on_payment, self.payment_taxes_on_bank_charge):
            case (False, _, _):
                reset_fields([
                    'allow_on_payment',
                    'payment_bank_charge_account',
                    'payment_bank_charge_type',
                    'payment_bank_charge_percentage',
                    'payment_taxes_on_bank_charge',
                    'payment_taxes_on_bank_charge_account_tax',
                    'payment_tax_percentage',
                    'payment_taxes_on_bank_charge_type',
                ])

            case (_, False, _):
                reset_fields([
                    'payment_bank_charge_account',
                    'payment_bank_charge_type',
                    'payment_bank_charge_percentage',
                    'payment_taxes_on_bank_charge',
                    'payment_taxes_on_bank_charge_account_tax',
                    'payment_tax_percentage',
                    'payment_taxes_on_bank_charge_type',
                ])

            case (_, _, False):
                reset_fields([
                    'payment_taxes_on_bank_charge_account_tax',
                    'payment_tax_percentage',
                    'payment_taxes_on_bank_charge_type',
                ])
