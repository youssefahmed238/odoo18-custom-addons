from odoo import models, fields


class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

    payment_ids = fields.One2many('account.payment', 'expense_sheet_id', string="Payments")
    fixed_bank_charge_amount = fields.Float(string="Fixed Bank Charge Amount", default=0.0)
    allow_on_payment = fields.Boolean(
        string="Allow On Payment",
        related='journal_id.allow_on_payment',
        store=True,
    )

    def action_sheet_move_post(self):
        res = super(HrExpenseSheet, self).action_sheet_move_post()
        for sheet in self:
            if sheet.payment_ids:
                payment_to_update = sheet.payment_ids[0]
                payment_to_update.write({
                    'fixed_bank_charge_amount': sheet.fixed_bank_charge_amount,
                })
                payment_to_update.create_taxes_journal()
        return res
