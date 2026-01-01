from odoo import models, fields, api
from dateutil.relativedelta import relativedelta


class LifePolicy(models.Model):
    _name = "life.policy"
    _inherit = ['policy.installation.mixin']

    _sequence_code = "life.policy.seq"
    _sequence_field = "life_sequences"

    name = fields.Char(required=True)

    category = fields.Many2one(
        'policy.category',
        string="Category",
        default=lambda self: self._default_life_category(), )

    life_sequences = fields.Char(string="Sequences", readonly=True)

    sum_insured = fields.Integer(string="Sum insured")
    current = fields.Boolean(default=False, string="Current Version")
    ifrs_group_name = fields.Char(string="IFRS Group Name")
    ifrs_group_code = fields.Char(string="IFRS group code")



    #   ------------------ Policy Basic Info Fields --------------------

    # -------- group 1 -------------
    insurer = fields.Many2one('res.partner',string="Insurer")
    product = fields.Many2one('policy.product', string="Product", domain=[('category_id', '=', 'Life')])
    customer = fields.Many2one('res.partner', string="Customer")
    business_source_id = fields.Many2one('res.partner',string="Business Source Id")
    kay_account = fields.Char(string="Kay Account")
    insured = fields.Many2one('res.partner', string="Insured")
    tpa_partner = fields.Many2one('res.partner',string="TPA Partner")
    in_favor_of = fields.Many2one('res.partner', string="In Favor Of")

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
    text_reason = fields.Text(string="Text Reason")

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
    payment_freq = fields.Selection([
        ('annually', 'Annually'),
        ('semiannually', 'Semiannually'),
        ('quarterly', 'Quarterly'),
        ('monthly', 'Monthly'),
    ], string="Payment Frequency")

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

    policy_risks_ids = fields.One2many('policy.risks', 'life_policy_number', domain=[('state', '=', 'approved')])

    # risks_ids = fields.One2many('risks.line', 'life_risks_id')
    # risks_policy_risks_premium_summary_ids = fields.One2many('risks.line', 'life_risks_id')
    # risks_policy_premium_summary_ids = fields.One2many('risks.line', 'life_risks_id')

    instalment_ids = fields.One2many('instalment.line', 'life_policy_id')

    policy_premium_summary_charges_ids = fields.One2many('insurance.policy.premium.summary', 'life_policy_id')

    #   ------------------- Helper Fields ----------------------

    parent_id = fields.Many2one('life.policy', string="Parent Policy")
    child_ids = fields.One2many('life.policy', 'parent_id', string="Sub Policies")
    child_count = fields.Integer(string="Children Count", compute='_compute_child_count')

    @api.model
    def create(self, vals):
        seq_code = getattr(self, "_sequence_code")
        seq_field = getattr(self, "_sequence_field")

        new_seq = self.env["ir.sequence"].next_by_code(seq_code)
        parent_id = vals.get("parent_id")

        if parent_id:
            parent = self.browse(parent_id)
            full_seq = f"{parent[seq_field]} / {new_seq}"
        else:
            full_seq = new_seq

        vals[seq_field] = full_seq
        vals["create_date"] = fields.datetime.now()
        vals["create_by"] = self.env.uid

        return super(LifePolicy, self).create(vals)

    def _default_life_category(self):
        return self.env['policy.category'].search([
            ('name', '=', 'Life')
        ], limit=1)

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
            'res_model': 'life.policy',
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
                'res_model': 'life.policy',
                'res_id': self.child_ids.id,
                'view_mode': 'form',
                'target': 'current',
            }
        else:
            return {
                'name': f'Sub Policies of {self.name}',
                'type': 'ir.actions.act_window',
                'res_model': 'life.policy',
                'view_mode': 'list,form',
                'domain': [('parent_id', '=', self.id)],
                'target': 'current',
                'context': {'default_parent_id': self.id},
            }

    def create_endorsement(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Create Endorsement",
            "res_model": "policy.endorsement.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_policy_ref": f"{self._name},{self.id}",
                "default_name": self.name,
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

            # 🔥 ONE LINE ONLY
            rec._create_installation()
    @api.depends('effective_date_from', 'effective_date_to')
    def _compute_total_days(self):
        for rec in self:
            if rec.effective_date_from and rec.effective_date_to:
                delta = rec.effective_date_to - rec.effective_date_from
                rec.period_in_days = delta.days + 1
            else:
                rec.period_in_days = 0



    def sum_item(self):
        for rec in self:
            # Fill policy_premium_summary_charges_ids
            rec.policy_premium_summary_charges_ids.unlink()
    
            summary_vals = [
                (0, 0, {
                    'name': 'Gross Premium EGP',
                    'value': rec.gross_premium_egp or 0,
                }),
                (0, 0, {
                    'name': 'Net Premium EGP',
                    'value': rec.net_premium_egp or 0,
                }),
            ]
    
            rec.write({
                'policy_premium_summary_charges_ids': summary_vals
            })
    
            # Generate instalment lines if payment_on is True
            if rec.payment_on and rec.payment_freq and rec.gross_premium_egp:
    
                # Delete old instalments
                rec.instalment_ids.unlink()
    
                # Map payment frequency to months
                freq_to_months = {
                    'annually': 1,
                    'semiannually': 2,
                    'quarterly': 4,
                    'monthly': 12,
                }
    
                # Determine the number of periods (months)
                months = freq_to_months.get(rec.payment_freq, 1)
    
                # If quarterly is selected, adjust months to 4 and ensure 4 installments
                if rec.payment_freq == 'quarterly':
                    months = 4
                    instalments_count = 4
                else:
                    instalments_count = months
    
                # Calculate instalment amount
                instalment_amount = rec.gross_premium_egp / instalments_count
                instalment_net = rec.net_premium_egp / instalments_count
    
                instalments = []
                start_date = rec.effective_date_from or fields.Date.today()
    
                for i in range(instalments_count):
                    # If quarterly, make sure the instalment date is 4 months apart
                    if rec.payment_freq == 'quarterly':
                        instalment_date = start_date + relativedelta(months=4 * i)
                    else:
                        instalment_date = start_date + relativedelta(months=i)

                    instalments.append((0, 0, {
                        'instalment_date': instalment_date,
                        'instalment_gross': instalment_amount,
                        'instalment_net': instalment_net,
                        'life_policy_id': rec.id,
                    }))

                rec.write({
                    'instalment_ids': instalments
                })
