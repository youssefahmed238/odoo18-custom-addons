# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

import time
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import json


class HrPayslipLine(models.Model):
    _inherit = "hr.payslip.line"

    loan_ids = fields.Many2many('hr.loan', string="Loans")
    loans_dict = fields.Text('Loans Dictionary')


class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    operation_applied_on_payslip = fields.Boolean(string="Operation Applied on Payslip")

    def action_pay_loan(self):
        # res = super(HrPayslip, self).action_payslip_done()
        loan_obj = self.env['hr.loan']
        skip_installment_obj = self.env['hr.skip.installment']
        slip_line_obj = self.env['hr.payslip.line']
        installment_obj = self.env['installment.line']
        loan_operation_obj = self.env['hr.loan.operation']
        for payslip in self:
            #slip_line_ids = slip_line_obj.search([('slip_id', '=', payslip.id), ('code', '=', 'LOAN')])
            #if slip_line_ids:
            #    slip_line_ids.unlink()
            loan_ids = loan_obj.search(
                [('start_date', '<=', payslip.date_to),
                 ('due_date', '>=', payslip.date_from), ('employee_id', '=', payslip.employee_id.id),
                 ('state', '=', 'approve')])
            for loan in loan_ids:
                skip_installment_ids = skip_installment_obj.search(
                    [('loan_id', '=', loan.id), ('state', '=', 'approve'), ('date', '>=', payslip.date_from),
                     ('date', '<=', payslip.date_to)])
                installment_ids = installment_obj.search([('loan_id', '=', loan.id), ('payslip_id', '=', payslip.id),
                                                          ('employee_id', '=', payslip.employee_id.id)])
                if installment_ids:
                    installment_ids.unlink()
                if skip_installment_ids:
                    due_date = loan.due_date + relativedelta(months=1)
                    loan.write({'due_date': due_date})
                    payslip.operation_applied_on_payslip = True
                else:

                    # Getting Loan Operation
                    loan_operation_ids = loan_operation_obj.search([('loan_id', '=', loan.id),
                                                                    ('state', '=', 'approve'),
                                                                    ('effective_date', '>=', payslip.date_from),
                                                                    ('effective_date', '<=', payslip.date_to),
                                                                    ('loan_operation_type', '=', 'loan_payment')])
                    # slip_line_ids = slip_line_obj.search([('slip_id', '=', payslip.id),
                    #                                       ('code', '=', 'LOAN' + str(loan.id))])
                    slip_line_ids = slip_line_obj.search([('slip_id', '=', payslip.id),
                                                          ('loan_ids', 'in', loan_ids.ids)])
                    if slip_line_ids:
                        # amount = slip_line_ids.read(['total'])[0]['total']
                        # amount = loan.deduction_amount
                        loans = slip_line_ids.read(['loans_dict'])[0].get('loans_dict')
                        loans_dict = json.loads(loans)

                        installment_data = {
                            'operation_id': loan_operation_ids[0].id if loan_operation_ids else False,
                            'loan_id': loan.id,
                            'payslip_id': payslip.id,
                            'employee_id': payslip.employee_id.id,
                            'amount': loans_dict.get(str(loan.id)),
                            'date': time.strftime('%Y-%m-%d')
                        }
                        installment_obj.create(installment_data)
                    if loan.amount_to_pay <= 0:
                        loan.write({'state': 'done'})
                    payslip.operation_applied_on_payslip = True
        return True

    def check_installments_to_pay(self):
        slip_line_obj = self.env['hr.payslip.line']
        loan_obj = self.env['hr.loan']
        rule_obj = self.env['hr.salary.rule']
        loan_operation_obj = self.env['hr.loan.operation']
        for payslip in self:
            print(" print loan in payroll")
            if not payslip.contract_id:
                raise UserError(_("Please enter Employee contract first."))
            loan_ids = loan_obj.search([('start_date', '<=', payslip.date_to),
                                        ('due_date', '>=', payslip.date_from),
                                        ('employee_id', '=', payslip.employee_id.id),
                                        ('state', 'in', ['approve']),
                                        ('is_loan_freeze', '=', False)])
            print('loan_ids: ', loan_ids)
            rule_ids = rule_obj.search([('code', '=', 'LOAN')])
            if rule_ids:
                rule = rule_ids[0]
                slip_line_ids = slip_line_obj.search([('slip_id', '=', payslip.id), ('code', '=', 'LOAN')])
                if slip_line_ids:
                    slip_line_ids.unlink()
                loan_ded_amt_sum = 0
                loans_sum_ded_dict = {}
                for loan in loan_ids:
                    if abs(loan.deduction_amount) > loan.amount_to_pay:
                        loan_ded_amt_sum += loan.amount_to_pay
                        loans_sum_ded_dict["%s" % loan.id] = loan.amount_to_pay
                    else:
                        loan_ded_amt_sum += loan.deduction_amount
                        loans_sum_ded_dict["%s" %loan.id] = loan.deduction_amount
                    # 200 , 300, 1000
                    # if abs(slip_line_data['amount']) > loan.amount_to_pay:
                    #     slip_line_data.update({'amount': loan.amount_to_pay})
                    loan_operation_ids = loan_operation_obj.search([('loan_id', '=', loan.id),
                                                                    ('state', '=', 'approve'),
                                                                    ('effective_date', '>=', payslip.date_from),
                                                                    ('effective_date', '<=', payslip.date_to)])
                    print('loan_operation_ids: ', loan_operation_ids)
                    if loan_operation_ids:
                        for loan_operation in loan_operation_ids:
                            if loan_operation.loan_operation_type == 'loan_payment':
                                if loan_operation.payment_type == 'by_payslip':
                                    if loan_operation.loan_payment_type == 'fully':
                                        amount = loan.loan_amount - loan.amount_paid
                                        loans_sum_ded_dict["%s" % loan.id] = amount
                                        # slip_line_data.update({'amount': amount})
                                    elif loan_operation.loan_payment_type == 'partially':
                                        amount = loan.deduction_amount + loan_operation.payment_amount
                                        loans_sum_ded_dict["%s" % loan.id] = amount
                                        # slip_line_data.update({'amount': amount})
                                    # slip_line_obj.create(slip_line_data)
                                    # net_ids = slip_line_obj.search(
                                    #     [('slip_id', '=', payslip.id), ('code', '=', 'NET')])
                                    # if net_ids:
                                    #     net_record = net_ids[0]
                                    #     net_ids.write({'amount': net_record.amount - slip_line_data['amount']})
                            # else:
                            #     slip_line_obj.create(slip_line_data)
                            #     net_ids = slip_line_obj.search([('slip_id', '=', payslip.id), ('code', '=', 'NET')])
                            #     if net_ids:
                            #         net_record = net_ids[0]
                            #         net_ids.write({'amount': net_record.amount - slip_line_data['amount']})
                            elif loan_operation.loan_operation_type == 'skip_installment':
                                loans_sum_ded_dict["%s" % loan.id] = loans_sum_ded_dict.get(str(loan.id), 0) - loan_operation.loan_id.deduction_amount


                print("Dict = ", json.dumps(loans_sum_ded_dict))
                loans_sum_ded_dict = {key: value for key, value in loans_sum_ded_dict.items() if value != 0}

                print("Dict = ", json.dumps(loans_sum_ded_dict))
                if loan_ids and loans_sum_ded_dict:
                    slip_line_data = {
                        'slip_id': payslip.id,
                        'salary_rule_id': rule.id,
                        'contract_id': payslip.contract_id.id,
                        'name': loan_ids[0].name + '-' + loan_ids[-1].name if len(loan_ids) > 1 else loan_ids[0].name,
                        # 'code': str('LOAN' + str(loan_ids[0].id) + ' - LOAN' + str(loan_ids[-1].id)),
                        'code': 'LOAN',
                        'category_id': rule.category_id.id,
                        'sequence': 186,
                        'appears_on_payslip': rule.appears_on_payslip,
                        'amount': sum(loans_sum_ded_dict.values()),
                        'employee_id': payslip.employee_id.id,
                        'loan_ids': [(6, 0, loan_ids.ids)],
                        'loans_dict': json.dumps(loans_sum_ded_dict)
                    }
                    slip_line = slip_line_obj.create(slip_line_data)
                    slip_line.update({
                        'total': (slip_line.amount * slip_line.rate) / 100,
                    })

                    net_ids = slip_line_obj.search([('slip_id', '=', payslip.id), ('code', '=', 'NET')])
                    if net_ids:
                        net_record = net_ids[0]
                        net_ids.write({'amount': net_record.amount - slip_line_data['amount']})
                        net_ids.write({'total': net_record.total - slip_line.total})
                    # TOTALDED
                    total_ded_ids = slip_line_obj.search([('slip_id', '=', payslip.id), ('code', '=', 'TOTAL_DED')])
                    if total_ded_ids:
                        total_ded_rec = total_ded_ids[0]
                        total_ded_ids.write({'amount': total_ded_rec.amount + slip_line_data['amount']})
        return True

    def compute_sheet(self):
        res = super(HrPayslip, self).compute_sheet()
        for payslip in self:
            payslip.check_installments_to_pay()
        return res

    def write(self, vals):
        res = super().write(vals)
        if 'state' in vals:
            if vals['state'] == 'done':
                self.action_pay_loan()
        return res
