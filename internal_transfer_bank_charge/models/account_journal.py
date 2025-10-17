from odoo import api, fields, models


class AccountJournalInherit(models.Model):
    _inherit = 'account.journal'

    # === it_ --> Internal Transfer ===#

    # Internal Transfer Bank Charge`
    allow_on_internal_transfer = fields.Boolean(string='Allow On Payment', default=False, copy=False)
    it_bank_charge_account = fields.Many2one('account.account', string='Payment Bank Charge Account')

    it_taxes_on_bank_charge = fields.Boolean(string='Taxes on Bank Charge', default=False, copy=False)
    it_taxes_on_bank_charge_account_tax = fields.Many2one('account.tax', string='Taxes on Bank Charge Account')

    # Reset fields based on booleans values change
    @api.onchange('allow_on_internal_transfer', 'it_taxes_on_bank_charge')
    def _fields_validate(self):
        def reset_fields(fields):
            for field in fields:
                setattr(self, field, False)

        if not self.allow_on_internal_transfer:
            reset_fields([
                'allow_on_internal_transfer',
                'it_bank_charge_account',
                'it_taxes_on_bank_charge',
                'it_taxes_on_bank_charge_account_tax',
            ])
        elif not self.it_taxes_on_bank_charge:
            reset_fields([
                'it_bank_charge_account',
                'it_taxes_on_bank_charge',
                'it_taxes_on_bank_charge_account_tax',
            ])
