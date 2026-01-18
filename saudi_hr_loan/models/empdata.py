from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    employee_code = fields.Char(string='Employee Code', groups='hr.group_hr_user')
    employee_short_name = fields.Char(string='Employee Short Name', groups='hr.group_hr_user')
    employee_name_en = fields.Char(string='Employee Name In English', groups='hr.group_hr_user')

    def name_get(self):
        return [(record.id, "%s:%s" % (record.employee_code or "", record.name)) if record.employee_code else (
            record.id, "%s" % (record.name)) for record in self]


# class HrContractSalary(models.Model):
#     _inherit = "hr.contract.history"
#
#     struct_ids = fields.Many2one('hr.payroll.structure', _compute="_compute_struct_ids", store=True)
#
#     @api.depends("contract_ids")
#     def _compute_struct_ids(self):
#         for record in self:
#             if record.contract_ids:
#                 last_contract_active = record.contract_ids[-1]
#                 record.struct_ids = last_contract_active.struct_ids.id if last_contract_active.struct_ids else False
#             else:
#                 record.struct_ids = False
