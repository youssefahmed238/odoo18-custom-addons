from odoo import models, fields


class InsurancePolicyPremiumSummary(models.Model):
    _name = 'insurance.policy.premium.summary'
    _description = 'Insurance Policy Premium Summary'

    name = fields.Char(string='Item', required=True)
    value = fields.Float(string='Value', required=True)

    medical_policy_id = fields.Many2one("medical.policy")
    life_policy_id = fields.Many2one("life.policy")
    motor_policy_id = fields.Many2one("motor.policy")
    fire_policy_id = fields.Many2one("fire.policy")
    engineering_policy_id = fields.Many2one("engineering.policy")
    misc_policy_id = fields.Many2one("misc.policy")
    marine_policy_id = fields.Many2one("marine.policy")
