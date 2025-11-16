from odoo import models, fields

class PolicyCover(models.Model):
    _name = "policy.cover.line"
    _description = "Policy Cover"

    risks_id = fields.Many2one("policy.risks", string="Risks", readonly=True)

    name = fields.Char(string="Cover Name", required=True)

    # Fields Line
    curr = fields.Char(string="Curr")
    cover = fields.Char(string="Cover")
    si_now = fields.Float(string="SI Now")
    rate = fields.Float(string="Rate (%)")
    net_premium = fields.Float(string="Net Premium")
