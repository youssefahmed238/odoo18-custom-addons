from odoo import models, fields

class MedicalPolicy(models.Model):
    _name = "medical.policy"

    name = fields.Char(required=True)


    policy_Number = fields.Char(string="Policy Number")
    sum_insured = fields.Integer(string="Sum insured")
    current = fields.Boolean(default=False, string="Current Version")
    ifrs_group_name = fields.Char(string="IFRS Group Name")
    ifrs_group_code = fields.Char(string="IFRS group code")


#   ------------------ Policy Basic Info Fields --------------------

    insurer = fields.Char(string="Insurer")
    product = fields.Many2one('product.product',string="Product")
    customer = fields.Many2one('hr.employee',string="Customer")
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
    transaction_type = fields.Selection([('new','New')])
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

