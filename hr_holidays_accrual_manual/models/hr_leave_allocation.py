from odoo import models, fields, _
from odoo.exceptions import UserError
from datetime import datetime, time


class HolidaysAllocation(models.Model):
    _inherit = "hr.leave.allocation"

    def _update_accrual_manual(self):
        """
        Update accrual on selected allocations manually.
        This method processes accrual plans for the selected allocation records.
        """
        if not self:
            raise UserError(_("Please select at least one allocation to process."))

        today = datetime.combine(fields.Date.today(), time(0, 0, 0))
        valid_allocations = self.search([
            ('id', 'in', self.ids),
            ('allocation_type', '=', 'accrual'), ('state', '=', 'validate'),
            ('accrual_plan_id', '!=', False), ('employee_id', '!=', False),
            '|', ('date_to', '=', False), ('date_to', '>', fields.Datetime.now()),
            '|', ('nextcall', '=', False), ('nextcall', '<=', today)
        ])

        if valid_allocations:
            valid_allocations._process_accrual_plans()

        print(valid_allocations)