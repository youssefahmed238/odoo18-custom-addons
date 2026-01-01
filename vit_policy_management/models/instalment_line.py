from odoo import models, fields


class InstalmentLine(models.Model):
    _name = "instalment.line"
    _description = "Instalment Line"

    instalment_date = fields.Date("Instalment Date")
    instalment_net = fields.Float("Instalment Net")
    instalment_gross = fields.Float("Instalment Gross")

    medical_policy_id = fields.Many2one("medical.policy",ondelete='cascade')
    life_policy_id = fields.Many2one("life.policy",ondelete='cascade')
    motor_policy_id = fields.Many2one('motor.policy',ondelete='cascade')
    fire_policy_id = fields.Many2one("fire.policy",ondelete='cascade')
    engineering_policy_id = fields.Many2one("engineering.policy",ondelete='cascade')
    misc_policy_id = fields.Many2one("misc.policy",ondelete='cascade')
    marine_policy_id = fields.Many2one("marine.policy",ondelete='cascade')
