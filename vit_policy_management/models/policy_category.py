from odoo import models, fields

class PolicyCategory(models.Model):
    _name = "policy.category"

    name = fields.Char(required=True)

