from odoo import models, fields


class CrmLeadInherit(models.Model):
    _inherit = 'crm.lead'

    rfq_order_count = fields.Integer(
        string="RFQs", compute='_compute_rfq_order_count')

    def _compute_rfq_order_count(self):
        for lead in self:
            lead.rfq_order_count = self.env['purchase.order'].search_count(
                [('crm_lead_id', '=', lead.id), ('state', '=', 'draft')]
            )

    def action_view_rfqs(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Requests for Quotation',
            'res_model': 'purchase.order',
            'view_mode': 'list,form',
            'domain': [('crm_lead_id', '=', self.id), ('state', '=', 'draft')],
            'context': {'default_crm_lead_id': self.id},
        }

    def action_create_rfq(self):
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'view_mode': 'form',
            'target': 'current',
            'context': {
                'default_crm_lead_id': self.id,
                'default_origin': self.name,
            },
        }
