from odoo import models, fields

class PolicyRisks(models.Model):
    _name = "policy.risks"
    _description = "Policy Risks"

    name = fields.Char(string="Name")
    policy_number = fields.Char(string="Policy Number")

    cover_line_id = fields.One2many('policy.cover.line', 'risks_id', string='Cover Line')




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