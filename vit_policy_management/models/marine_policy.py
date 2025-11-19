from odoo import models, fields, api


class MarinePolicy(models.Model):
    _name = "marine.policy"

    name = fields.Char(readonly=True, string="Name")
    sum_insured = fields.Integer(string="Sum insured")
    current = fields.Boolean(default=False, string="Current Version")
    ifrs_group_name = fields.Char(string="IFRS Group Name")
    ifrs_group_code = fields.Char(string="IFRS group code")
    create_by = fields.Many2one('res.users', string="Create By", readonly=True)
    create_date = fields.Datetime(string="Create Date", readonly=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('cancel', 'Cancel'),
    ],
        default='draft',
        copy=False,
    )

    #   ------------------- Helper Fields ----------------------

    parent_id = fields.Many2one('marine.policy', string="Parent Policy")
    child_ids = fields.One2many('marine.policy', 'parent_id', string="Sub Policies")
    child_count = fields.Integer(string="Children Count", compute='_compute_child_count')

    #   ------------------ Policy Basic Info Fields --------------------

    insurer = fields.Char(string="Insurer")
    product = fields.Many2one('product.product', string="Product")
    customer = fields.Many2one('hr.employee', string="Customer")
    business_source_id = fields.Char(string="Business Source Id")
    in_favor = fields.Char(string="Is Favor")
    kay_account = fields.Char(string="Kay Account")
    curr = fields.Selection([('egy', 'EGY')])
    calculation_type = fields.Char(string="Calculation Type")
    issue_date = fields.Date(string="Issue Date")
    effective_date_from = fields.Date(string="Effective Date From")
    effective_date_to = fields.Date(string="Effective Date To")
    period_in_days = fields.Integer(string="Period In Days")
    branch = fields.Char(string="Branch")
    transaction_type = fields.Selection([('new', 'New')])
    parent = fields.Char(string="Parent")
    invoice = fields.Char(string="Invoice")
    approved_by = fields.Char(string="Approved By")
    approved_only = fields.Date(string="Approved On")
    version = fields.Char(string="Version")
    next_version_date = fields.Date(string="Next Version Date")
    dayes_torenewal = fields.Integer(string="Dayes Torenewal")
    loss_rate = fields.Integer(string="Loss Rate")
    renewal_loss_ratio = fields.Integer(string="Renewal Loss Ratio")

    #     ------------------- Policy Financial Fields ----------------------

    net_premium = fields.Integer(string="Net Premium")
    net_premium_egp = fields.Integer(string="Net Premium EGP")
    reg_premium = fields.Integer(string="Regulator Premium")
    payment_on = fields.Boolean(string="Payment On")
    payment_freq = fields.Boolean(string="Payment Freq")
    years = fields.Integer(string="Years")
    create_certificate_puc = fields.Boolean(string="Create Certificate PUC")
    gross_premium = fields.Integer(string="Gross Premium")
    gross_premium_egp = fields.Integer(string="Gross Premium EGP")
    gross_rate = fields.Integer(string="Gross Rate")

    @api.model
    def create(self, vals):
        name = self.env['ir.sequence'].next_by_code('marine.policy.seq')
        vals.update({
            'name': name,
            'create_date': fields.datetime.today(),
            'create_by': self.env.uid
        })
        res = super(MarinePolicy, self).create(vals)

        res.name = res.parent_id.name + ' / ' + name if res.parent_id else name

        return res

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
            'res_model': 'marine.policy',
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
                'res_model': 'marine.policy',
                'res_id': self.child_ids.id,
                'view_mode': 'form',
                'target': 'current',
            }
        else:
            return {
                'name': f'Sub Policies of {self.name}',
                'type': 'ir.actions.act_window',
                'res_model': 'marine.policy',
                'view_mode': 'list,form',
                'domain': [('parent_id', '=', self.id)],
                'target': 'current',
                'context': {'default_parent_id': self.id},
            }

    def create_sub_marine_policy(self):
        """Action to create a sub marine policy"""
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
            'name': 'Create Sub Marine Policy',
            'type': 'ir.actions.act_window',
            'res_model': 'marine.policy',
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
