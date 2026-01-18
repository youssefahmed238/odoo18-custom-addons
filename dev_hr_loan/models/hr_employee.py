# -*- coding: utf-8 -*-
##############################################################################
#
#
##############################################################################

from odoo import models, fields, api, _


class hr_employee(models.Model):
    _inherit = 'hr.employee'

    loan_request = fields.Integer('Loan Request Per Year', default=1, required="1")

class hr_employee_public(models.Model):
    _inherit = 'hr.employee.public'

    loan_request = fields.Integer('Loan Request Per Year', default=1, required="1")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
