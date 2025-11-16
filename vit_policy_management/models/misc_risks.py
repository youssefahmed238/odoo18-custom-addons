from odoo import models, fields

class MiscRisks(models.Model):
    _name = "misc.risks"
    _description = "Misc Risks"

    name = fields.Char(string="Misc Risks")






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

