from odoo import models, fields, api
import random
import string


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def _generate_random_otp(self):
        partners = self.search([])
        used_otps = set(self.search([]).mapped('otp_text'))

        for partner in partners:
            otp = self._generate_unique_otp(used_otps)
            partner.write({
                'otp_time': fields.Datetime.now(),
                'otp_text': otp,
            })
            used_otps.add(otp)

    def _generate_unique_otp(self, used_otps):
        while True:
            otp = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            if otp not in used_otps:
                return otp
