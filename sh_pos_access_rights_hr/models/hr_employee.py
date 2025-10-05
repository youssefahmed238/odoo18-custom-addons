# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import fields, models, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    disable_payment_id = fields.Boolean(string="POS - Disable Payment")
    group_select_customer = fields.Boolean(string='POS - Disable Customer Selection')
    group_disable_discount = fields.Boolean(string='POS - Disable Discount Button')
    group_disable_qty = fields.Boolean(string='POS - Disable Qty Button')
    group_disable_price = fields.Boolean(string='POS - Disable Price Button')
    group_disable_plus_minus = fields.Boolean(string='POS - Disable Plus-Minus')
    group_disable_numpad = fields.Boolean(string='POS - Disable Numpad')
    hr_group_disable_hide_orders = fields.Boolean(string='POS - Disable New Orders')
    hr_group_disable_remove = fields.Boolean(string='POS - Disable Remove Button')
    hr_group_remove_delete_button = fields.Boolean(string='POS - Disable Delete Orders')

    @api.model
    def _load_pos_data_fields(self, config_id):
        result = super(HrEmployee, self)._load_pos_data_fields(config_id)

        custom_fields = [
            'disable_payment_id', 'group_select_customer',
            'group_disable_discount', 'group_disable_qty', 'group_disable_price',
            'group_disable_plus_minus', 'group_disable_numpad',
            'hr_group_disable_hide_orders', 'hr_group_disable_remove',
            'hr_group_remove_delete_button'
        ]

        result.extend(custom_fields)
        return result
