from odoo import models, fields


class ResUsers(models.Model):
    _inherit = 'res.users'

    thermal_size = fields.Selection([
        ('58mm', '2 Inch (58 mm)'),
        ('80mm', '3 Inch (80 mm)'),
        ('104mm', '4 Inch (104 mm)'),
    ], string='Printer Size', default='80mm', required=True)
