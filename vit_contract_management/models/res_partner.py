from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    insurance_contract_id = fields.Many2one('insurance.contract', string='Insurance Contract')
