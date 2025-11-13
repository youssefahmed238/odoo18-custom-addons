from odoo import models, api, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    signup_url = fields.Char('Signup Url', invisible=True, copy=False)

    @api.model
    def _signup_retrieve_info(self, token):
        """ retrieve the user info about the token
            :return: a dictionary with the user information if the token is valid, None otherwise:
                - 'db': the name of the database
                - 'token': the token, if token is valid
                - 'name': the name of the partner, if token is valid
                - 'login': the user login, if the user already exists
                - 'email': the partner email, if the user does not exist
        """
        res = super().signup_retrieve_info(token)
        partner = self._get_partner_from_token(token)
        if partner.user_ids[0].mobile:
            res['mobile'] = partner.user_ids[0].mobile
        return res