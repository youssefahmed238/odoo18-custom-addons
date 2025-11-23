from odoo import models, fields


class InstalmentLine(models.Model):
    _name = "instalment.line"
    _description = "Instalment Line"

    instalment_date = fields.Date("Instalment Date")
    instalment_net = fields.Float("Instalment Net")
    instalment_gross = fields.Float("Instalment Gross")

    medical_policy_id = fields.Many2one("medical.policy")
    life_policy_id = fields.Many2one("life.policy")
    motor_policy_id = fields.Many2one("motor.policy")
    fire_policy_id = fields.Many2one("fire.policy")
    engineering_policy_id = fields.Many2one("engineering.policy")
    misc_policy_id = fields.Many2one("misc.policy")
    marine_policy_id = fields.Many2one("marine.policy")
