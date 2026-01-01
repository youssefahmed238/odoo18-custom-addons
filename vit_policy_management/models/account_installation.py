from odoo import models, fields

class AccountInstallation(models.Model):
    _name = "account.installation"

    name = fields.Char(required=True)

    # Generic reference to ANY policy
    policy_ref = fields.Reference(
        selection=[
            ('motor.policy', 'Motor Policy'),
            ('engineering.policy', 'Engineering Policy'),
            ('fire.policy', 'Fire Policy'),
            ('life.policy', 'Life Policy'),
            ('marine.policy', 'Marine Policy'),
            ('medical.policy', 'Medical Policy'),
            ('misc.policy', 'Misc Policy'),
        ],
        string="Policy"
    )

    installation_ids = fields.One2many(
        'account.installation.line',
        'installation_id'
    )

