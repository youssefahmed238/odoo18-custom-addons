from odoo import models, fields

class PolicyPaymentMethod(models.Model):
    _name = "policy.payment.method"

    name = fields.Char(required=True)