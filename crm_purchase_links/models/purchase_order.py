from odoo import models, fields


class PurchaseOrderInherit(models.Model):
    _inherit = 'purchase.order'

    crm_lead_id = fields.Many2one('crm.lead', string='CRM Lead')
