from odoo import models


class CrmLeadInherit(models.Model):
    _inherit = 'crm.lead'

    def action_create_rfq(self):
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'view_mode': 'form',
            'target': 'current',
        }
