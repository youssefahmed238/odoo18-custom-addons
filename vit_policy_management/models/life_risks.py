from odoo import models, fields

class LifeRisks(models.Model):
    _name = "life.risks"
    _description = "Life Risks"

    name = fields.Char(string="Life Risks")


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