from odoo import models, fields, api

class AccountInstallationLine(models.Model):
    _name = "account.installation.line"

    installation_id = fields.Many2one(
        "account.installation",
        ondelete="cascade",
        required=True
    )

    installation_date = fields.Date()
    installation_net = fields.Float()
    installation_gross = fields.Float()

    due_date = fields.Date('Due Date')
    payment_method = fields.Selection([('cheque', 'Cheque'),('transfer', 'Transfer')], string="Payment Method")
    amount_paid = fields.Float(string="Amount Paid")
    remaining_amount = fields.Float(string="Remaining Amount")

    @api.onchange('amount_paid', 'installation_gross')
    def _compute_remaining_amount(self):
        """Compute the remaining amount when amount_paid is updated"""
        for record in self:
            # Ensure installation_gross is not zero before subtracting
            if record.installation_gross:
                record.remaining_amount = record.installation_gross - record.amount_paid
            else:
                record.remaining_amount = 0



class PolicyInstallationMixin(models.AbstractModel):
    _name = "policy.installation.mixin"
    _description = "Policy Installation Mixin"

    def _get_installation_name(self):
        """Override if needed"""
        return self.name

    def _get_installment_lines(self):
        """Override if installment field name differs"""
        return self.instalment_ids

    def _create_installation(self):
        AccountInstallation = self.env['account.installation']

        for rec in self:
            # Prevent duplicates
            existing = AccountInstallation.search([
                ('policy_ref', '=', f'{rec._name},{rec.id}')
            ], limit=1)

            if existing:
                continue

            installation = AccountInstallation.create({
                'name': rec._get_installation_name(),
                'policy_ref': f'{rec._name},{rec.id}',
            })

            lines = []
            for inst in rec._get_installment_lines():
                lines.append((0, 0, {
                    'installation_date': inst.instalment_date,
                    'installation_net': inst.instalment_net,
                    'installation_gross': inst.instalment_gross,
                }))

            installation.installation_ids = lines
