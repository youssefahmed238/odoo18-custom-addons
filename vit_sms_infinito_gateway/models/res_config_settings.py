# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    infinito_enabled = fields.Boolean(
        string="Use Infinito SMS Gateway",
        help="If enabled, Odoo 18 will send sms.sms via Infinito Unified API.",
    )
    infinito_client_id = fields.Char(string="Infinito Client ID")
    infinito_client_password = fields.Char(string="Infinito Client Password")
    infinito_sender_id = fields.Char(
        string="Infinito Sender ID",
        help="Approved sender ID / mask configured in Infinito.",
    )

    @api.model
    def get_values(self):
        res = super().get_values()
        icp = self.env["ir.config_parameter"].sudo()
        res.update(
            infinito_enabled=icp.get_param("sms_infinito.enabled", "False") == "True",
            infinito_client_id=icp.get_param("sms_infinito.client_id", "") or "",
            infinito_client_password=icp.get_param("sms_infinito.client_password", "") or "",
            infinito_sender_id=icp.get_param("sms_infinito.sender_id", "") or "",
        )
        return res

    def set_values(self):
        super().set_values()
        icp = self.env["ir.config_parameter"].sudo()
        icp.set_param(
            "sms_infinito.enabled",
            "True" if self.infinito_enabled else "False",
        )
        icp.set_param("sms_infinito.client_id", self.infinito_client_id or "")
        icp.set_param("sms_infinito.client_password", self.infinito_client_password or "")
        icp.set_param("sms_infinito.sender_id", self.infinito_sender_id or "")
