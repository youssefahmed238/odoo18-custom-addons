from odoo import models, fields, api


class AccountInstallationLine(models.Model):
    _inherit = "account.installation.line"

    policy_ref = fields.Reference(related='installation_id.policy_ref', readonly=True)

    commission_line_ids = fields.Many2many(
        'commission.line', compute='_compute_commission_line_ids', store=False
    )

    total_amount_p = fields.Float(
        compute='_compute_total_amount_p',
        string="Comm Total Amount %",
        store=True,
        readonly=True
    )

    @api.depends('installation_id.policy_ref')
    def _compute_commission_line_ids(self):
        for record in self:
            if record.installation_id and record.installation_id.policy_ref:
                try:
                    record.commission_line_ids = record.installation_id.policy_ref.commission_line_ids
                except AttributeError:
                    record.commission_line_ids = self.env['commission.line']

            else:
                record.commission_line_ids = self.env['commission.line']

    @api.depends('commission_line_ids.total_amount_p')
    def _compute_total_amount_p(self):
        for record in self:
            record.total_amount_p = sum(
                record.commission_line_ids.mapped('total_amount_p')) if record.commission_line_ids else 0.0
