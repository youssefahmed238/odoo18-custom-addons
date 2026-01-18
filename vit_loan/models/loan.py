from odoo import models, fields, api


class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    loan_amount = fields.Float(
        string="Loan Amount",
        compute="_compute_loan_amount",
        store=False
    )

    def _compute_loan_amount(self):
        for payslip in self:
            loan_lines = payslip.input_line_ids.filtered(
                lambda l: l.input_type_id
                          and l.input_type_id.name
                          and l.input_type_id.name.lower() == 'loan'
            )
            payslip.loan_amount = sum(loan_lines.mapped('amount')) if loan_lines else 0.0


class HrSalaryAttachment(models.Model):
    _inherit = "hr.salary.attachment"

    total_loan = fields.Float(
        string="Total Paid",
        compute="_compute_total_loan",
        store=True
    )

    payslip_ids = fields.Many2many(
        "hr.payslip",
        string="Related Payslips",
        compute="_compute_total_loan",
        store=True
    )

    total_remain = fields.Float(
        string="Amount to Pay ",
        compute="_compute_remaining_amount",
        store=True
    )

    @api.depends("employee_ids")
    def _compute_total_loan(self):
        for attachment in self:
            payslip_records = self.env["hr.payslip"]
            if attachment.employee_ids:
                payslip_records = self.env["hr.payslip"].search([
                    ("employee_id", "in", attachment.employee_ids.ids)
                ])
            attachment.total_loan = sum(payslip_records.mapped("loan_amount"))
            attachment.payslip_ids = payslip_records.ids

    @api.depends("total_loan", "total_amount")
    def _compute_remaining_amount(self):
        print("=== DEBUG: Starting _compute_remaining_amount ===")
        for record in self:
            print(f"[DEBUG] Record ID: {record.id}")
            print(f"[DEBUG] total_amount: {record.total_amount}")
            print(f"[DEBUG] total_loan: {record.total_loan}")

            record.total_remain = record.total_amount - record.total_loan

            print(f"[DEBUG] Computed total_remain: {record.total_remain}")
        print("=== DEBUG: Finished _compute_remaining_amount ===")
