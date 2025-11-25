from odoo import models, fields, api


class MedicalPolicy(models.Model):
    _name = "medical.policy"
    _description = "Medical Policy"


    name = fields.Char(readonly=True)

    sum_insured = fields.Integer(string="Sum insured")
    current = fields.Boolean(default=False, string="Current Version")
    ifrs_group_name = fields.Char(string="IFRS Group Name")
    ifrs_group_code = fields.Char(string="IFRS group code")



    #   ------------------ Policy Basic Info Fields --------------------

    # -------- group 1 -------------
    insurer = fields.Many2one('res.partner',string="Insurer")
    product = fields.Many2one('policy.product', string="Product", domain=[('category_id', '=', 'Medical')])
    customer = fields.Many2one('res.partner', string="Customer")
    business_source_id = fields.Many2one('res.partner',string="Business Source Id")
    kay_account = fields.Char(string="Kay Account")
    insured = fields.Many2one('res.partner', string="Insured")
    tpa_partner = fields.Many2one('res.partner',string="TPA Partner")

    # -------- group 2 -------------
    curr = fields.Many2one('res.currency', string="Currency")
    calculation_type = fields.Selection([
        ('one_year', 'One Year'),
        ('prorata', 'Prorata'),
        ('short_period', 'Short Period'),
        ('long_term', 'Long Period'),
    ],string="Calculation Type")
    issue_date = fields.Date(string="Issue Date")
    effective_date_from = fields.Date(string="Effective Date From")
    effective_date_to = fields.Date(string="Effective Date To")
    period_in_days = fields.Integer(string="Period In Days", compute='_compute_total_days', readonly=True)
    payment_method = fields.Char(string="Payment Method")

    # -------- group 3 -------------
    branch = fields.Many2one('account.analytic.account',string="Branch")

    # -------- group 4 -------------
    create_by = fields.Many2one('res.users', string="Create By", readonly=True)
    create_date = fields.Datetime(string="Create Date", readonly=True)
    approved_by = fields.Many2one('res.users', string="Approved On", readonly=True)
    approved_on = fields.Datetime(string="Approved On", readonly=True)

    # -------- group 5 -------------
    transaction_type = fields.Selection([
        ('new', 'New'),
        ('renewal', 'Renewal'),
        ('non_technical', 'Technical Add'),
        ('technical_refund', 'Technical Refund'),
        ('technical_borndead', 'Technical Born Dead'),
        ('cancel', 'Technical Cancel With Refund'),
        ('period_extension', 'Technical Period Extension'),
        ('cancel_add_end', 'Technical Cancel Add End'),
        ('cancel_refund_end', 'Technical Cancel Refund End'),
        ('cancel_inception', 'Technical Cancel From Inception'),
        ('cancel_period_extension', 'Technical Cancel Period Extension'),
    ])
    parent = fields.Many2one('res.partner',string="Parent")
    invoice = fields.Many2one('account.move',string="Invoice")
    endorsement_reason = fields.Text(string="Endorsement Reason")

    # -------- group 6 -------------
    version = fields.Integer(string="Version")
    next_version_date = fields.Date(string="Next Version Date")
    days_to_renewal = fields.Integer(string="Days To renewal")
    loss_rate = fields.Float(string="Loss Rate")
    renewal_loss_ratio = fields.Float(string="Renewal Loss Ratio")



    #     ------------------- Policy Financial Fields ----------------------

    net_premium = fields.Float(string="Net Premium")
    net_premium_egp = fields.Float(string="Net Premium EGP")
    reg_premium = fields.Float(string="Regulator Premium")
    payment_on = fields.Boolean(string="Payment on Instalments")
    payment_freq = fields.Boolean(string="Payment Freq")
    # years = fields.Integer(string="Years")
    create_certificate_puc = fields.Boolean(string="Create Certificate PUC")

    gross_premium = fields.Integer(string="Gross Premium")
    gross_premium_egp = fields.Integer(string="Gross Premium EGP")
    gross_rate = fields.Integer(string="Gross Rate")

    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('cancel', 'Cancel'),
    ],
        default='draft',
        copy=False,
    )

    risks_ids = fields.One2many('risks.line', 'medical_risks_id')
    risks_policy_risks_premium_summary_ids = fields.One2many('risks.line', 'medical_risks_id')
    risks_policy_premium_summary_ids = fields.One2many('risks.line', 'medical_risks_id')

    instalment_ids = fields.One2many('instalment.line', 'medical_policy_id')

    policy_premium_summary_charges_ids = fields.One2many('insurance.policy.premium.summary', 'medical_policy_id')

    #   ------------------- Helper Fields ----------------------

    parent_id = fields.Many2one('medical.policy', string="Parent Policy")
    child_ids = fields.One2many('medical.policy', 'parent_id', string="Sub Policies")
    child_count = fields.Integer(string="Children Count", compute='_compute_child_count')

    @api.model
    def create(self, vals):
        name = vals.get('name', '') + self.env['ir.sequence'].next_by_code('medical.policy.seq')
        vals.update({
            'name': name,
            'create_date': fields.datetime.today(),
            'create_by': self.env.uid
        })
        res = super(MedicalPolicy, self).create(vals)

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
            'res_model': 'medical.policy',
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
                'res_model': 'medical.policy',
                'res_id': self.child_ids.id,
                'view_mode': 'form',
                'target': 'current',
            }
        else:
            return {
                'name': f'Sub Policies of {self.name}',
                'type': 'ir.actions.act_window',
                'res_model': 'medical.policy',
                'view_mode': 'list,form',
                'domain': [('parent_id', '=', self.id)],
                'target': 'current',
                'context': {'default_parent_id': self.id},
            }

    def create_sub_medical_policy(self):
        """Action to create a sub medical policy"""
        self.ensure_one()

        default_vals = {
            'name': f"{self.name} / ",
            # 'policy_Number': self.policy_Number,
            'sum_insured': self.sum_insured,
            'current': False,
            'ifrs_group_name': self.ifrs_group_name,
            'ifrs_group_code': self.ifrs_group_code,
            'insurer': self.insurer,
            'product': self.product.id if self.product else False,
            'customer': self.customer.id if self.customer else False,
            'business_source_id': self.business_source_id.id,
            'in_favor': self.in_favor,
            'kay_account': self.kay_account,
            'curr': self.curr.id,
            'calculation_type': self.calculation_type,
            'issue_date': self.issue_date,
            'effective_date_from': self.effective_date_from,
            'effective_date_to': self.effective_date_to,
            'period_in_days': self.period_in_days,
            'branch': self.branch,
            'transaction_type': self.transaction_type,
            'parent_id': self.id,
            'invoice': self.invoice.id,
            'approved_by': self.approved_by,
            'approved_only': self.approved_only,
            'version': self.version,
            'next_version_date': self.next_version_date,
            'dayes_torenewal': self.dayes_torenewal,
            'loss_rate': self.loss_rate,
            'renewal_loss_ratio': self.renewal_loss_ratio,
            'net_premium': self.net_premium,
            'net_premium_egp': self.net_premium_egp,
            'reg_premium': self.reg_premium,
            'payment_on': self.payment_on,
            'payment_freq': self.payment_freq,
            # 'years': self.years,
            'create_certificate_puc': self.create_certificate_puc,
            'gross_premium': self.gross_premium,
            'gross_premium_egp': self.gross_premium_egp,
            'gross_rate': self.gross_rate,
            'state': 'draft',
        }

        return {
            'name': 'Create Sub Medical Policy',
            'type': 'ir.actions.act_window',
            'res_model': 'medical.policy',
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
        for rec in self:
            rec.write({
                'state': 'approved',
                'approved_by': self.env.user.id,
                'approved_on': fields.Datetime.now(),
            })


    @api.depends('effective_date_from', 'effective_date_to')
    def _compute_total_days(self):
        for rec in self:
            if rec.effective_date_from and rec.effective_date_to:
                delta = rec.effective_date_to - rec.effective_date_from
                rec.period_in_days = delta.days + 1
            else:
                rec.period_in_days = 0

