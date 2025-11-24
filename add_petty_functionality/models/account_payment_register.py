from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class AccountPaymentRegisterInherit(models.TransientModel):
    _inherit = 'account.payment.register'

    source_petty_employee_id_domain = fields.Binary(string='Petty Employees domain', compute="_compute_source_petty_employee_id_domain")
    source_petty_employee_id = fields.Many2one('hr.employee', string='Source Petty Employee')
    is_source_petty = fields.Boolean(related='journal_id.is_petty')

    @api.depends('journal_id', 'journal_id.petty_employees_ids')
    def _compute_source_petty_employee_id_domain(self):
        for rec in self:
            rec.source_petty_employee_id_domain = [('id', '=', self.env.user.employee_id.id)]
            if self.env.user.has_group('add_petty_functionality.group_petty_account_manager'):
                rec.source_petty_employee_id_domain = []
            elif self.env.user.has_group('add_petty_functionality.group_petty_branch_accountant'):
                rec.source_petty_employee_id_domain = [('id', "in", rec.journal_id.petty_employees_ids.ids)]

    def extend_result_for_bank_charge(self, res):
        """ Extend payment vals to include petty employee when created from the register wizard. """

        parent_method = getattr(super(AccountPaymentRegisterInherit, self), "extend_result_for_bank_charge",
                                None)
        if parent_method:
            res = parent_method(res)

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
