from odoo import api, fields, models


class HrLeave(models.Model):
    _name = 'hr.leave'
    _inherit = ['hr.leave', 'portal.mixin']

    def _compute_access_url(self):
        super(HrLeave, self)._compute_access_url()
        for leave in self:
            leave.access_url = '/my/leaves/%s' % leave.id
