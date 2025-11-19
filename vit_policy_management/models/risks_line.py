from odoo import models, fields

class RisksLine(models.Model):
    _name = "risks.line"
    _description = "Risks Line"

    risks_number = fields.Char("Risks Number")
    risks_id = fields.Char("Risks ID")
    currency = fields.Many2one("res.currency", string="Currency")
    lob = fields.Many2one("account.analytic.account", string="Lob")
    si_before =fields.Float("Si Before")
    si_addition =fields.Float("Si +/-")
    si_now =fields.Float("Si Now")
    premium =fields.Float("Premium")

    medical_risks_id = fields.Many2one("medical.policy", string="Medical")
    life_risks_id = fields.Many2one("medical.policy", string="Life")
    motor_risks_id = fields.Many2one("medical.policy", string="motor")
    fire_risks_id = fields.Many2one("medical.policy", string="fire")
    misc_risks_id = fields.Many2one("medical.policy", string="misc")
    marine_risks_id = fields.Many2one("medical.policy", string="marine")
    end_risks_id = fields.Many2one("medical.policy", string="marine")


