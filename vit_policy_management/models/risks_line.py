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
    life_risks_id = fields.Many2one("life.policy", string="Life")
    motor_risks_id = fields.Many2one("motor.policy", string="motor")
    fire_risks_id = fields.Many2one("fire.policy", string="fire")
    misc_risks_id = fields.Many2one("misc.policy", string="misc")
    marine_risks_id = fields.Many2one("marine.policy", string="marine")
    engineering_risks_id = fields.Many2one("engineering.policy", string="engineering")


    po_risks_id = fields.Many2one("policy.risks", string="Risks")

    category = fields.Many2one(
        related='po_risks_id.category',
        string="Category",
        store=True
    )

    category_name = fields.Char(
        related='po_risks_id.category.name',
        string="Category Name",
        store=True
    )



    car_name = fields.Char("Car Name")
    car_number = fields.Char("Car Number")
    fire_name = fields.Char("Fire Name")
    fire_number = fields.Char("Fire Number")
    life_name = fields.Char("Lient Name")
    life_number = fields.Char("Lient Number")


