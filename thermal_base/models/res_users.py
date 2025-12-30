from odoo import models, fields


class ResUsers(models.Model):
    _inherit = 'res.users'

    thermal_size = fields.Selection([
        ('58', '58 mm'),
        ('80', '80 mm'),
        ('112', '112 mm'),
    ], string='Thermal Size', default='80', required=True)
