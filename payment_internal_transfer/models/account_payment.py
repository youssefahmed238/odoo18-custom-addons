from odoo import models, fields, api


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    is_internal_transfer = fields.Boolean(string="Internal Transfer", readonly=False, store=True,
                                          tracking=True, compute="_compute_is_internal_transfer")

    destination_journal_id = fields.Many2one(
        comodel_name='account.journal',
        string='Destination Journal',
        domain="[('type', 'in', ('bank','cash')), ('id', '!=', journal_id)]",
        check_company=True,
    )

    source_petty_employee_id = fields.Many2one('hr.employee', string='Source Petty Employee')
    destination_petty_employee_id = fields.Many2one('hr.employee', string='Destination Petty Employee')

    is_source_petty = fields.Boolean(related='journal_id.is_petty')
    is_destination_petty = fields.Boolean(related='destination_journal_id.is_petty')

    @api.depends('journal_id')
    def _compute_is_internal_transfer(self):
        for payment in self:
            payment.is_internal_transfer = payment.journal_id.is_petty
