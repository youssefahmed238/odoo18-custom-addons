# -*- coding: utf-8 -*-
##############################################################################
#
##############################################################################

from odoo import models


class LoanOutstandingLetter(models.AbstractModel):
    _name = 'report.dev_loan_outstanding_letter.tmpl_loan_letter'

    def _get_report_values(self, docids, data=None):
        docs = self.env['employee.loan'].browse(docids)
        return {
            'doc_ids': docs.ids,
            'doc_model': 'employee.loan',
            'docs': docs,
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
