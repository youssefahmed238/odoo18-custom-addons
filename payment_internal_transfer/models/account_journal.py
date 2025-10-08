from odoo import models, fields


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    is_petty = fields.Boolean(string='Is Petty ?!', default=False, copy=False)

