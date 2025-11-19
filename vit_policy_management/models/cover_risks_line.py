from odoo import models, fields



class MedicalRiskCover(models.Model):
    _name = "medical.risk.cover"
    _description = "Medical Risk Cover"

    medical_id = fields.Many2one('policy.medical.risks', string="medical id")
    life_id = fields.Many2one('policy.medical.risks', string="Life id")
    motor_id = fields.Many2one('policy.medical.risks', string="Motor id")
    fire_id = fields.Many2one('policy.medical.risks', string="Fire id")
    misc_id = fields.Many2one('policy.medical.risks', string="Misc id")
    marine_id = fields.Many2one('policy.medical.risks', string="Marine id")
    engineering_id = fields.Many2one('policy.medical.risks', string="Engineering id")

    currency = fields.Many2one('res.currency', string="Currency")
    cover = fields.Char(string="Cover")
    si_before = fields.Float(string="Si Before")
    si_now = fields.Float(string="Si Now")
    rate = fields.Float(string="Rate")
    premium = fields.Float(string="NET Premium")