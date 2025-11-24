from odoo import models, fields, api


class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

    petty_employee_id_domain = fields.Binary(string='Petty Employees domain',
                                             compute="_compute_petty_employee_id_domain")
    petty_employee_id = fields.Many2one('hr.employee', string='Petty Employee')
    is_petty = fields.Boolean(related='payment_method_line_id.journal_id.is_petty', string='Is Petty', store=True)

    @api.depends('journal_id', 'journal_id.petty_employees_ids')
    def _compute_petty_employee_id_domain(self):
        for rec in self:
            rec.petty_employee_id_domain = [('id', '=', self.env.user.employee_id.id)]
            if self.env.user.has_group('add_petty_functionality.group_petty_account_manager'):
                rec.petty_employee_id_domain = []
            elif self.env.user.has_group('add_petty_functionality.group_petty_branch_accountant'):
                rec.petty_employee_id_domain = [('id', "in", rec.journal_id.petty_employees_ids.ids)]

    def action_sheet_move_post(self):
        res = super(HrExpenseSheet, self).action_sheet_move_post()
        for sheet in self:
            if sheet.payment_ids:
                for payment in sheet.payment_ids:
                    payment.write({
                        'source_petty_employee_id': sheet.petty_employee_id.id,
                    })

                    move_to_update = payment.move_id
                    if move_to_update:
                        for line in move_to_update.line_ids:
                            if line.account_id.name == payment.journal_id.name:
                                line.petty_employee = sheet.petty_employee_id.id
        return res
