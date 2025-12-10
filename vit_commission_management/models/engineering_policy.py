from odoo import models, fields, api


class EngineeringPolicy(models.Model):
    _inherit = 'engineering.policy'

    apply_commission = fields.Boolean(string='Apply Commission', default=True)
    total_amount = fields.Float(string='Total Amount', readonly=False, store=True)
    commission_line_ids = fields.One2many('commission.line', 'engineering_policy_id', store=True)

    @api.constrains('total_amount', 'net_premium_egp')
    def _check_total_amount(self):
        for record in self:
            if record.total_amount < 0:
                raise ValueError("Total Amount cannot be negative.")
            elif record.total_amount > record.net_premium_egp:
                raise ValueError("Total Amount cannot exceed Net Premium EGP.")

    def _get_contract_line(self):
        self.ensure_one()
        if not (self.insurer and self.product and self.create_date):
            return False

        contract = self.env['insurance.contract'].search([
            ('partner_id', '=', self.insurer.id),
            ('state', '=', 'confirm'),
            ('start_date', '<=', self.create_date.date()),
            ('end_date', '>=', self.create_date.date())
        ])

        return self.env['insurance.contract.line'].search([
            ('contract_id', '=', contract.id),
            ('insurance_line.name', '=', 'Engineering'),
            ('insurance_products', 'in', self.product.id)
        ])

    def _sync_commission(self):
        for record in self:
            if not (record.insurer and record.product):
                record.commission_line_ids.unlink()
                continue

            contract_line = record._get_contract_line()

            if record.apply_commission and contract_line:
                if record.commission_line_ids:
                    record.commission_line_ids.contract_line_id = contract_line.id
                else:
                    self.env['commission.line'].create({
                        'engineering_policy_id': record.id,
                        'contract_line_id': contract_line.id,
                    })
            else:
                if not record.commission_line_ids:
                    self.env['commission.line'].create({
                        'engineering_policy_id': record.id,
                        'total_amount': record.total_amount,
                    })
                record.commission_line_ids.contract_line_id = False

    @api.model
    def create(self, vals):
        record = super().create(vals)
        record._sync_commission()
        return record

    def write(self, vals):
        res = super().write(vals)
        self._sync_commission()
        return res
