from email.policy import default

from odoo import api, fields, models, _

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    wa_template_id = fields.Many2one('whatsapp.template', config_parameter='odoo_whatsapp_login.otp_whatsapp_template')
    wa_account_id = fields.Many2one('whatsapp.account', config_parameter='odoo_whatsapp_login.wa_account')
    wa_reset_password_enabled = fields.Boolean('Reset Password Using WhatsApp', config_parameter='odoo_whatsapp_login.wa_reset_password')
    wa_reset_password_template_id = fields.Many2one('whatsapp.template', config_parameter='odoo_whatsapp_login.reset_password_whatsapp_template')
