from odoo import models, fields

class InsuranceFor(models.Model):
    _name = "insurance.for"

    name = fields.Char(required=True)