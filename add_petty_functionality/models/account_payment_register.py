from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class AccountPaymentRegisterInherit(models.TransientModel):
    _inherit = 'account.payment.register'

    source_petty_employee_id = fields.Many2one('hr.employee', string='Source Petty Employee')
    is_source_petty = fields.Boolean(related='journal_id.is_petty')

    def extend_result_for_bank_charge(self, res):
        res.update({
            'is_internal_transfer': False,
            'is_from_register_wizard': True,
            'source_petty_employee_id': self.source_petty_employee_id.id,
        })

        return res


def _create_payment_vals_from_wizard(self, batch_result):
    res = super(AccountPaymentRegisterInherit, self)._create_payment_vals_from_wizard(batch_result)
    return self.with_context(from_bank_charge_wizard=True).extend_result_for_bank_charge(res)


def _create_payment_vals_from_batch(self, batch_result):
    res = super(AccountPaymentRegisterInherit, self)._create_payment_vals_from_batch(batch_result)
    return self.with_context(from_bank_charge_wizard=True).extend_result_for_bank_charge(res)
