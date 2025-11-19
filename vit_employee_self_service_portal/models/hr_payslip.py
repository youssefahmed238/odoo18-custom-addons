from odoo import fields, models


class HrPayslipPortal(models.Model):
    _name = "hr.payslip"
    _inherit = ['hr.payslip', 'portal.mixin']

    def _compute_access_url(self):
        super(HrPayslipPortal, self)._compute_access_url()
        for payslip in self:
            payslip.access_url = '/my/payslips/%s' % payslip.id

    def _get_report_base_filename(self):
        self.ensure_one()
        return (self.name)
