from odoo import models, fields

class MarineRisks(models.Model):
    _name = "marine.risks"
    _description = "Marine Risks"

    name = fields.Char(string="Marine Risks")






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

