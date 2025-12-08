from odoo import models, fields, api


class InsuranceContract(models.Model):
    _inherit = 'insurance.contract'

    # Override action_confirm to create commission lines for all relevant contract lines
    def action_confirm(self):
        res = super(InsuranceContract, self).action_confirm()

        for contract in self:
            for line in contract.line_ids:
                existing_commission_lines = self.env['commission.line'].search([
                    ('contract_line_id', '=', line.id),
                    ('insurance_line', '=', line.insurance_line.id),
                ])
                for product in line.insurance_products:
                    existing_commission_line = existing_commission_lines.filtered(
                        lambda cl: cl.insurance_product.id == product.id)
                    if not existing_commission_line:
                        self.env['commission.line'].create({
                            'contract_line_id': line.id,
                            'insurance_line': line.insurance_line.id,
                            'insurance_product': product.id,
                        })
                if existing_commission_lines:
                    for cl in existing_commission_lines:
                        if cl.insurance_product.id not in line.insurance_products.ids:
                            cl.unlink()

        return res
