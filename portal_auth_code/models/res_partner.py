from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    auth_code = fields.Char(string="Auth Code")
    auth_code_time = fields.Datetime(string='Auth Code Time')