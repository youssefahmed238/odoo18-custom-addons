from odoo import models, fields, api

class PolicyDashboard(models.Model):
    _name = 'policy.dashboard'
    _description = 'Policy Dashboard'

    medical_count = fields.Integer(string="Medical Policies", compute="_compute_counts")
    life_count = fields.Integer(string="Life Policies", compute="_compute_counts")

    @api.depends()
    def _compute_counts(self):
        for rec in self:
            rec.medical_count = self.env['medical.policy'].search_count([])
            rec.life_count = self.env['life.policy'].search_count([])
