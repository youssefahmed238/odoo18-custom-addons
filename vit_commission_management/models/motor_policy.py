from odoo import models, fields, api


class MotorPolicy(models.Model):
    _inherit = 'motor.policy'

    apply_commission = fields.Boolean(string='Apply Commission', default=True)
    commission_line_ids = fields.One2many('commission.line', 'motor_policy_id', compute='_compute_commission_lines',
                                          store=True)

    @api.depends('insurer', 'product')
    def _compute_commission_lines(self):
        for record in self:
            contract = self.env['insurance.contract'].search(
                [('partner_id', '=', record.insurer.id), ('state', '=', 'confirm'),
                 ('start_date', '<=', record.create_date.date()),
                 ('end_date', '>=', record.create_date.date())])

            commission_line_ids = self.env['commission.line'].search(
                [('contract_id', '=', contract.id),
                 ('insurance_line.name', '=', 'Motor'),
                 ('insurance_product', '=', record.product.id)])

            if record.commission_line_ids:
                for line in record.commission_line_ids:
                    line.policy_name = ''

            record.commission_line_ids = commission_line_ids

            for line in record.commission_line_ids:
                line.medical_policy_id = record.id
