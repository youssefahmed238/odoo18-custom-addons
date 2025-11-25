from odoo import models, fields, api


class MarinePolicy(models.Model):
    _inherit = 'marine.policy'

    commission_line_ids = fields.One2many('commission.line', 'marine_policy_id', compute='_compute_commission_lines',
                                          store=True)

    @api.depends('insurer', 'product')
    def _compute_commission_lines(self):
        for record in self:
            contract = self.env['insurance.contract'].search(
                [('partner_id', '=', record.insurer.id), ('state', '=', 'confirm')])

            record.commission_line_ids = False

            commission_line_ids = []

            for line in contract.line_ids:
                if record.create_date and line.start_date <= record.create_date.date() <= line.end_date:
                    if line.insurance_line.name == 'Marine':
                        if record.product.id in line.insurance_products.ids:
                            commission_line = self.env['commission.line'].create({
                                'marine_policy_id': record.id,
                                'contract_line_id': line.id,
                            })

                            commission_line_ids.append(commission_line.id)

            record.commission_line_ids = self.env['commission.line'].search([('id', 'in', commission_line_ids)])
