# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime
from dateutil import relativedelta
import calendar
import time


class HrLoanOperation(models.Model):
    _name = 'hr.loan.operation'
    _description = 'Loan Operation'
    _inherit = ["analytic.mixin"]

    def _get_employee(self):
        loan_ids = self.env['hr.loan'].search([('state', '=', 'approve')])
        employee_id = []
        for loan in loan_ids:
            employee_id.append(loan.employee_id.id)
        return employee_id

    name = fields.Char('Name', required=True, copy=False, readonly=True, states={'draft': [('readonly', False)]},
                       index=True, default=lambda self: _('New'))
    loan_operation_type = fields.Selection([('skip_installment', 'Skip Installment'),
                                            ('increase_amount', 'Increase Loan Amount'),
                                            ('decrease_amount', 'Decrease Loan Amount'),
                                            ('loan_payment', 'Loan Payment')], required=True,
                                           default='skip_installment')
    decrease_mechanism_type = fields.Selection([('reschedule', 'Reschedule'), ('extend_months', 'Extend Period')],
                                               default='reschedule')
    skip_reason = fields.Char('Reason to Skip')
    loan_id = fields.Many2one('hr.loan', 'Loan', domain="[('employee_id','=',employee_id), ('state','=', 'approve')]",
                              required=True)
    employee_id = fields.Many2one('hr.employee', 'Employee', required=True,
                                  domain=lambda self: self._get_employee_domain())
    department_id = fields.Many2one('hr.department', string="Department", related='employee_id.department_id',
                                    store=True)
    effective_date = fields.Date('Effective Date', default=fields.Date.today)
    current_loan_amount = fields.Float('Current Loan Amount', related='loan_id.loan_amount', readonly=True)
    amount_to_pay = fields.Float('Amount to Pay', related='loan_id.amount_to_pay', readonly=True)
    loan_amount = fields.Float('Increase Loan Amount', copy=False)
    loan_payment_type = fields.Selection([('fully', 'Fully Payment'), ('partially', 'Partially Payment')],
                                         default='fully', copy=False)
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=False,
                                 default=lambda self: self.env.user.company_id)
    payment_amount = fields.Float('Payment Amount')
    payment_type = fields.Selection([('by_payslip', 'By Payslip')], default='by_payslip')
    state = fields.Selection([('draft', 'Draft'),
                              ('confirm', 'Confirm'),
                              ('open', 'Waiting Approval'),
                              ('approve', 'Approved'),
                              ('cancel', 'Cancelled'),
                              ('refuse', 'Refused'),
                              ('done', 'Done')],
                             default='draft', copy=False)
    approved_by = fields.Many2one('res.users', 'Approved by', readonly=True, copy=False)
    refused_by = fields.Many2one('res.users', 'Refused by', readonly=True, copy=False)
    approved_date = fields.Datetime(string='Approved on', readonly=True, copy=False)
    refused_date = fields.Datetime(string='Refused on', readonly=True, copy=False)
    operation_applied = fields.Boolean('Effect Applied on Loan?', default=False)
    accounting_info = fields.Boolean('Accounting Info', default=False, compute='compute_accounting_info')

    def _get_employee_domain(self):
        domain = []
        leave_allocation_obj = self.env['hr.loan']
        employees = leave_allocation_obj.search([('state', '=', 'approve')]).mapped('employee_id')
        domain.append(('id', 'in', employees.ids))
        return domain

    @api.depends('loan_operation_type', 'state', 'payment_type')
    def compute_accounting_info(self):
        for rec in self:
            if rec.state in ['open', 'approve'] and rec.loan_operation_type == 'increase_amount':
                rec.accounting_info = True
            else:
                rec.accounting_info = False

    def check_loan_operation_req(self, employee, effective_date, type):
        loan_operation_ids = self.search(
            [('state', 'in', ['confirm', 'open', 'approve']), ('employee_id', '=', employee.id), ('id', '!=', self.id)])
        for rec in loan_operation_ids:
            if rec.loan_operation_type == 'increase_amount' and type != 'increase_amount' and rec.effective_date.month == effective_date.month and rec.effective_date.year == effective_date.year:
                raise ValidationError(
                    _('During this month %s has already request for incrase amount so kindly check loan operation request!!' % employee.name))
            if rec.loan_operation_type == 'decrease_amount' and type != 'decrease_amount' and rec.effective_date.month == effective_date.month and rec.effective_date.year == effective_date.year:
                raise ValidationError(
                    _('During this month %s has already request for decrease amount so kindly check loan operation request!!' % employee.name))
            elif rec.loan_operation_type == 'skip_installment' and rec.effective_date.month == effective_date.month and rec.effective_date.year == effective_date.year:
                raise ValidationError(
                    _('During this month %s has already request for skip installment so kindly check loan operation request!!' % employee.name))
            elif rec.loan_operation_type == 'loan_payment' and rec.effective_date.month == effective_date.month and rec.effective_date.year == effective_date.year:
                raise ValidationError(
                    _('During this month %s has already request for loan payment so kindly check loan operation request!!' % employee.name))

    @api.constrains('loan_amount', 'payment_amount')
    def check_loan_amount(self):
        """
            Check increase loan amount 0 or not
        """
        for rec in self:
            if rec.loan_operation_type == 'increase_amount' and rec.loan_amount <= 0:
                raise ValidationError(_('Increase Loan Amount Must be Greater than 0!!'))
            if rec.loan_operation_type == 'decrease_amount' and rec.loan_amount <= 0:
                raise ValidationError(_('Decrease Loan Amount Must be Greater than 0!!'))
            elif rec.loan_operation_type == 'loan_payment' and rec.loan_payment_type == 'partially' and rec.payment_amount < 0:
                raise ValidationError(_('Pay Loan Amount Must be Greater than 0!!'))

    @api.onchange('loan_payment_type')
    def onchange_loan_payment_type(self):
        if self.loan_payment_type:
            self.payment_amount = False

    @api.onchange('employee_id')
    def _onchange_employee(self):
        if self.employee_id:
            loan_id = self.env['hr.loan'].search([('state', '=', 'approve'), ('employee_id', '=', self.employee_id.id)])
            if not loan_id:
                raise UserError(_('%s has not any running loan request.' % self.employee_id.name))

    @api.onchange('loan_operation_type')
    def _onchange_loan_operation_type(self):
        if self.loan_operation_type:
            self.skip_reason = False
            self.loan_amount = False
            self.loan_payment_type = 'fully'

    @api.model_create_multi
    def create(self, values):
        for val in values:
            if val.get('name', _('New')) == _('New'):
                seq_date = None
                if 'company_id' in val:
                    val['name'] = self.env['ir.sequence'].with_context(force_company=val['company_id']).next_by_code(
                        'hr.loan.operation') or _('New')
                else:
                    val['name'] = self.env['ir.sequence'].next_by_code('hr.loan.operation') or _('New')
        res = super(HrLoanOperation, self).create(values)
        if res.employee_id and res.loan_id and res.effective_date:
            if res.loan_operation_type == 'loan_payment' and res.loan_payment_type == 'partially':
                if res.payment_amount >= res.loan_id.amount_to_pay:
                    print(res.payment_amount, res.loan_id.amount_to_pay)
                    raise UserError(_('Payment amount should be less then loan amount to pay!'))
        return res

    def write(self, values):
        for res in self:
            if values.get('loan_operation_type') == 'loan_payment' or values.get(
                    'loan_payment_type') == 'partially' or values.get('payment_amount'):
                if values.get('payment_amount') and values.get('payment_amount') > res.loan_id.amount_to_pay:
                    raise UserError(_('Payment amount should be less then loan amount to pay!'))
        return super(HrLoanOperation, self).write(values)

    def confirm_loan_operation(self):
        """
            sent the status of generating his/her loan operation in Confirm state
        """
        self.ensure_one()
        if self.loan_id.is_loan_freeze:
            raise UserError(_('Please Unfreeze Your Loan.'))
        self.check_loan_operation_req(self.employee_id, self.effective_date, self.loan_operation_type)
        self.state = 'confirm'

    def waiting_approval_loan_operation(self):
        """
            sent the status of generating his/her loan operation in Open state
        """
        self.ensure_one()
        self.state = 'open'

    def approve_loan_operation(self):
        """
            sent the status of generating his/her loan operation in Approve state
        """
        self.ensure_one()
        self.approved_by = self.env.uid
        self.approved_date = datetime.today()
        timenow = time.strftime('%Y-%m-%d')
        for loan in self:
            if loan.loan_operation_type == 'increase_amount':
                amount = loan.loan_amount
                if loan.loan_operation_type == 'loan_payment':
                    if loan.loan_payment_type == 'fully':
                        amount = loan.loan_id.loan_amount
                        loan.loan_id.state = 'done'
                    else:
                        amount = loan.payment_amount
        self.state = 'approve'

    def set_to_cancel(self):
        """
            sent the status of loan operation in cancel state
        """
        self.ensure_one()
        self.state = 'cancel'

    def set_to_draft(self):
        """
            sent the status of loan operation in draft state
        """
        self.ensure_one()
        self.state = 'draft'
        self.operation_applied = False

    def refuse_loan_operation(self):
        """
            sent the status of generating his/her loan operation in Refuse state
        """
        self.ensure_one()
        self.refused_by = self.env.uid
        self.refused_date = datetime.today()
        self.state = 'refuse'

    def unlink(self):
        """
            To remove the record, which is not in 'draft' and 'cancel' states
        """
        for rec in self:
            if rec.state not in ['draft', 'cancel']:
                raise ValidationError(
                    _('You cannot delete a request to Loan Operation which is in %s state.') % (rec.state))
        return super(HrLoanOperation, self).unlink()

    def apply_loan_operation(self):
        if self._context.get('run_manually'):
            loan_operation_ids = self
        else:
            loan_operation_ids = self.env['hr.loan.operation'].search([('state', '=', 'approve'),
                                                                       ('effective_date', '=', fields.Date.today()),
                                                                       ('operation_applied', '=', False),
                                                                       ('loan_operation_type', 'in',
                                                                        ['increase_amount', 'loan_payment',
                                                                         'decrease_amount'])
                                                                       ])
        print("Loan Operations = ", loan_operation_ids)
        for rec in loan_operation_ids:
            if rec.loan_operation_type == 'increase_amount':
                # diff = relativedelta.relativedelta(rec.loan_id.due_date, rec.effective_date)
                # months = diff.months
                # if diff.days > 0:
                #     months = months + 1
                # amount_to_pay = rec.loan_id.amount_to_pay + rec.loan_amount
                loan_amount = rec.loan_amount + rec.loan_id.loan_amount
                # rec.loan_id.write({'loan_amount': loan_amount, 'amount_to_pay': amount_to_pay,
                #                   'deduction_amount': amount_to_pay / months})
                rec.loan_id.write({'loan_amount': loan_amount})
                if rec.loan_id.emi_based_on == 'amount':
                    rec.loan_id._calculate_due_date()
                else:
                    rec.loan_id._calculate_amounts()
                rec.loan_id.make_calculation()
                rec.operation_applied = True
            if rec.loan_operation_type == 'decrease_amount':
                loan_amount = rec.loan_id.loan_amount - rec.loan_amount
                # rec.loan_id.write({'loan_amount': loan_amount, 'amount_to_pay': amount_to_pay,
                #                   'deduction_amount': amount_to_pay / months})
                rec.loan_id.write({'loan_amount': loan_amount})
                if rec.decrease_mechanism_type == 'reschedule':
                    if rec.loan_id.emi_based_on == 'amount':
                        rec.loan_id._calculate_due_date()
                    else:
                        rec.loan_id._calculate_amounts()
                    rec.loan_id.make_calculation()
                    rec.operation_applied = True
                else:
                    pass
                    # paid_amount = 0.0
                    # for installment in rec.loan_id.installment_lines:
                    #     paid_amount += installment.amount
                    # rec.amount_paid = paid_amount
                    # rec.amount_to_pay = rec.loan_amount - paid_amount