from odoo import models, fields

class PolicyRisks(models.Model):
    _name = "policy.risks"
    _description = "Policy Risks"

    name = fields.Char(string="Name")
    risk_name = fields.Char(string="Risk Name")

    cover_line_id = fields.One2many('policy.cover.line', 'risks_id', string='Cover Line')

    # Fields Line
    curr = fields.Char(string="Curr")
    cover = fields.Char(string="Cover")
    si_now = fields.Float(string="SI Now")
    rate = fields.Float(string="Rate (%)")
    net_premium = fields.Float(string="Net Premium")





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