from odoo import models, fields

class PolicyMedicalRisks(models.Model):
    _name = "policy.medical.risks"
    _description = "Medical Risks"

    name = fields.Char(string="Risks Name")
    risk_name = fields.Many2one('medical.policy',string=" Policy Number")

    cover_risks_ids = fields.One2many(
        'medical.risk.cover',
        'medical_id',
        string="Covers"
    )







    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('cancel', 'Cancel'),
    ],
        default='draft',
        copy=False,
    )

    def set_to_draft(self):
        self.state = 'draft'

    def set_to_cancel(self):
        self.state = 'cancel'

    def set_to_approved(self):
        self.state = 'approved'





