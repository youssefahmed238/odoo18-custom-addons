from odoo import models, fields, api


class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

    petty_employee_id = fields.Many2one('hr.employee', string='Petty Employee')
    is_petty = fields.Boolean(related='payment_method_line_id.journal_id.is_petty', string='Is Petty', store=True)

    def action_sheet_move_post(self):
        res = super(HrExpenseSheet, self).action_sheet_move_post()
        for sheet in self:
            if sheet.payment_ids:
                payment_to_update = sheet.payment_ids[0]
                payment_to_update.write({
                    'source_petty_employee_id': sheet.petty_employee_id.id,
                })

                move_to_update = payment_to_update.move_id
                if move_to_update:
                    for line in move_to_update.line_ids:
                        if line.account_id.name == payment_to_update.journal_id.name:
                            line.petty_employee = sheet.petty_employee_id.id
        return res
