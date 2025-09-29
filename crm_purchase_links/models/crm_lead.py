from odoo import models, fields, api


class CrmLeadInherit(models.Model):
    _inherit = 'crm.lead'

    rfq_order_count = fields.Integer(
        string="RFQs", compute='_compute_rfq_order_count')

    purchase_order_ids = fields.One2many(
        'purchase.order', 'crm_lead_id', string="Purchase Orders"
    )

    purchase_order_count = fields.Integer(string="Number of Purchase Orders", compute="_compute_purchase_order_data")

    purchase_order_total = fields.Monetary(
        string="Purchase Orders",
        compute="_compute_purchase_order_data",
        currency_field='company_currency',
    )

    @api.depends('purchase_order_ids.amount_total', 'purchase_order_ids.state')
    def _compute_purchase_order_data(self):
        for lead in self:
            confirmed_orders = lead.purchase_order_ids.filtered(lambda po: po.state == 'purchase')
            print(confirmed_orders)
            lead.purchase_order_total = sum(confirmed_orders.mapped('amount_total'))
            lead.purchase_order_count = len(confirmed_orders)

    @api.depends('purchase_order_ids.state')
    def _compute_rfq_order_count(self):
        for lead in self:
            lead.rfq_order_count = len(lead.purchase_order_ids.filtered(lambda po: po.state == 'draft'))

    def action_view_rfqs(self):
        self.ensure_one()

        action = {
            'type': 'ir.actions.act_window',
            'name': 'Requests for Quotation',
            'res_model': 'purchase.order',
            'view_mode': 'list,form',
            'domain': [('crm_lead_id', '=', self.id), ('state', '=', 'draft')],
            'context': {'default_crm_lead_id': self.id},
        }

        draft_orders = self.purchase_order_ids.filtered(lambda o: o.state == 'draft')
        if len(draft_orders) == 1:
            action['view_mode'] = 'form'
            action['res_id'] = draft_orders.id
            action['views'] = [(False, 'form')]

        return action

    def action_view_purchase_orders(self):
        self.ensure_one()

        action = {
            'type': 'ir.actions.act_window',
            'name': 'Purchase Orders',
            'res_model': 'purchase.order',
            'view_mode': 'list,form',
            'domain': [('crm_lead_id', '=', self.id), ('state', '=', 'purchase')],
            'context': {'default_crm_lead_id': self.id},
        }

        confirmed_orders = self.purchase_order_ids.filtered(lambda o: o.state == 'purchase')
        if len(confirmed_orders) == 1:
            action['view_mode'] = 'form'
            action['res_id'] = confirmed_orders.id
            action['views'] = [(False, 'form')]

        return action

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
