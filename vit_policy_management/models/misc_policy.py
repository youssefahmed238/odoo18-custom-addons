from odoo import models, fields


class MiscPolicy(models.Model):
    _name = "misc.policy"

    name = fields.Char(string="Policy Misc", required=True)
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

    #   ------------------- Helper Fields ----------------------

    parent_id = fields.Many2one('misc.policy', string="Parent Policy")
    child_ids = fields.One2many('misc.policy', 'parent_id', string="Sub Policies")
    child_count = fields.Integer(string="Children Count", compute='_compute_child_count')

    def _compute_child_count(self):
        """Compute the number of child policies"""
        for record in self:
            record.child_count = len(record.child_ids)

    def action_view_parent_policy(self):
        """Action to view parent policy"""
        self.ensure_one()

        if not self.parent_id:
            return {'type': 'ir.actions.act_window_close'}

        return {
            'name': 'Parent Policy',
            'type': 'ir.actions.act_window',
            'res_model': 'misc.policy',
            'res_id': self.parent_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_view_child_policies(self):
        """Action to view child policies"""
        self.ensure_one()

        if not self.child_ids:
            return {'type': 'ir.actions.act_window_close'}

        if len(self.child_ids) == 1:
            return {
                'name': 'Sub Policy',
                'type': 'ir.actions.act_window',
                'res_model': 'misc.policy',
                'res_id': self.child_ids.id,
                'view_mode': 'form',
                'target': 'current',
            }
        else:
            return {
                'name': f'Sub Policies of {self.name}',
                'type': 'ir.actions.act_window',
                'res_model': 'misc.policy',
                'view_mode': 'list,form',
                'domain': [('parent_id', '=', self.id)],
                'target': 'current',
                'context': {'default_parent_id': self.id},
            }

    def create_sub_misc_policy(self):
        """Action to create a sub misc policy"""
        self.ensure_one()

        default_vals = {
            'name': f"{self.name} / ",
            'policy_number': self.policy_number,
            'sum_insured': self.sum_insured,
            'current': False,
            'ifrs_group_name': self.ifrs_group_name,
            'ifrs_group_code': self.ifrs_group_code,
            'parent_id': self.id,
            'state': 'draft',
        }

        return {
            'name': 'Create Sub Misc Policy',
            'type': 'ir.actions.act_window',
            'res_model': 'misc.policy',
            'view_mode': 'form',
            'target': 'current',
            'context': {
                'default_name': default_vals['name'],
                **default_vals,
                'default_parent_id': self.id
            },
        }

    def set_to_draft(self):
        self.state = 'draft'

    def set_to_cancel(self):
        self.state = 'cancel'

    def set_to_approved(self):
        self.state = 'approved'
