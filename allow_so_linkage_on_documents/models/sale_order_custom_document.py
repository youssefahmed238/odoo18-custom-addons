# -*- coding: utf-8 -*-
# Part of Quocent. See LICENSE file for full copyright and licensing details.

from odoo import fields, models

class QcentSaleDocumentCustomization(models.Model):
    _inherit = 'documents.document'
    _description = 'Qcent Sale Document Customization'

    custom_sale_order_id = fields.Many2one('sale.order', string='Sale')

