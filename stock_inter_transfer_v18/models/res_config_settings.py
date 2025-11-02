# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    transfer_approval_required = fields.Boolean(string='Transfer approval required',
                                                config_parameter='stock_inter_transfer_v18.transfer_approval_required',
                                                help='The approval of the responsible person will be needed to transfer the stock from one warehouse to another')
