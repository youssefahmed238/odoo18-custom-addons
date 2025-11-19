from odoo import models, fields

class FireRisks(models.Model):
    _name = "fire.risks"

    name = fields.Char(string="Fire Risks", required=True)
    policy_number = fields.Many2one(string="Policy Number")

    cover_risks_ids = fields.One2many(
        'medical.risk.cover',
        'fire_id',
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