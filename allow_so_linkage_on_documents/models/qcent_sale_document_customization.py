# -*- coding: utf-8 -*-
# Part of Quocent. See LICENSE file for full copyright and licensing details.

from odoo import fields, models

class SaleOrder(models.Model):
    _inherit = 'sale.order'


    document_count = fields.Integer('Document Count', compute='_compute_document_count')

    #this method is used to count the number of documents in sale order
    def _compute_document_count(self):
        read_group_var = self.env['documents.document']._read_group(
            [('custom_sale_order_id', 'in', self.ids)],
            groupby=['custom_sale_order_id'],
            aggregates=['__count'])
        document_count_dict = {order.id: count for order, count in read_group_var}
        for record in self:
            record.document_count = document_count_dict.get(record.id, 0)
            

    #it return an action to display documents linked to the current sale order
    def action_see_documents(self):
        self.ensure_one()
        return {
            'name': 'Documents',
            'domain': [('custom_sale_order_id', '=', self.id)],
            'res_model': 'documents.document',
            'type': 'ir.actions.act_window',
            'views': [(False, 'kanban')],
            'view_mode': 'kanban',
            'context': {
                "default_custom_sale_order_id": self.id,
                "searchpanel_default_folder_id": False
            },
        }

