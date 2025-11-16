from odoo import models, fields

class MotorRisks(models.Model):
    _name = "motor.risks"
    _description = "Motor Risks"

    name = fields.Char(string="Motor Risks")


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