from odoo import fields, models

class ApprovalPortal(models.Model):
    _name = "approval.request"
    _inherit = ['approval.request', 'portal.mixin']

    def _compute_access_url(self):
        super(ApprovalPortal, self)._compute_access_url()
        for rec in self:
            rec.access_url = '/my/approvals/%s' % rec.id

    def _get_report_base_filename(self):
        self.ensure_one()
        return self.name or 'Approval'
