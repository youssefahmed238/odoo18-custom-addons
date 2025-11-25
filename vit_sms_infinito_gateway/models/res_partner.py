# -*- coding: utf-8 -*-
from odoo import models, fields, api
import random
import string

class ResPartner(models.Model):
    _inherit = "res.partner"

    def action_infinito_test_sms(self):
        """
        Send a test SMS to this partner using the standard sms.sms workflow.
        This respects the Infinito integration, if enabled.
        """
        otp = ''.join(random.choices(string.digits, k=6))
        self.write({
            'otp_time': fields.Datetime.now(),
            'otp_text': otp,
        })
        SmsSms = self.env["sms.sms"].sudo()
        message = self.env["sms.template"].search([("id", "=", 8)], limit=1).body or "Message not found"
        for partner in self:
            if partner.mobile and partner.otp_text:
                message = message.replace("{{ object.otp_text }}", partner.otp_text)
                SmsSms.create(
                    {
                        "number": partner.mobile,
                        "body": message,
                        "state": "outgoing",
                    }
                )._send()
        return True


    def action_infinito_sms(self):
        """
        Send a test SMS to this partner using the standard sms.sms workflow.
        This respects the Infinito integration, if enabled.
        """
        otp = ''.join(random.choices(string.digits, k=6))
        self.write({
            'otp_time': fields.Datetime.now(),
            'otp_text': otp,
        })
        SmsSms = self.env["sms.sms"].sudo()
        message = self.env["sms.template"].search([("id", "=", 7)], limit=1).body or "Message not found"
        for partner in self:
            if partner.mobile and partner.otp_text:
                message = message.replace("{{ object.otp_text }}", partner.otp_text)
                SmsSms.create(
                    {
                        "number": partner.mobile,
                        "body": message,
                        "state": "outgoing",
                    }
                )._send()
        return True