from odoo import models, fields


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    is_petty = fields.Boolean(string='Is Petty ?!', default=False, copy=False)
    petty_employees_ids = fields.Many2many('hr.employee', string='Petty Employees')
