from odoo import models, fields

class MarinePolicy(models.Model):
    _name = "marine.policy"

    name = fields.Char(required=True, string="Name")
    policy_number = fields.Char(string="Policy Number")
    sum_insured = fields.Integer(string="Sum insured")
    current = fields.Boolean(default=False, string="Current Version")
    ifrs_group_name = fields.Char(string="IFRS Group Name")
    ifrs_group_code = fields.Char(string="IFRS group code")



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