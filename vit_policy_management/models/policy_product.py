from odoo import models, fields


class PolicyProduct(models.Model):
    _name = 'policy.product'


    name = fields.Char(string="Product Name", required=True)
    category_id = fields.Many2one('policy.category', string="Category" ,required=True)