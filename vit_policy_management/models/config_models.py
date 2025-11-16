from odoo import models, fields


class PolicySubcategory(models.Model):
    _name = 'policy.subcategory'


    name = fields.Char(required=True)


