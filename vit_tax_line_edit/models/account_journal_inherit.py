from odoo import models, fields, api


class AccountJournalInherit(models.Model):
    _inherit = 'account.journal'

    per_line_calc = fields.Boolean(
        string='Per Line Calculation',
        default=False,
        readonly=False,
        store=True,
        compute='_compute_per_line_calc',
    )

    @api.depends('type')
    def _compute_per_line_calc(self):
        for journal in self:
            journal.per_line_calc = journal.type == 'general'
