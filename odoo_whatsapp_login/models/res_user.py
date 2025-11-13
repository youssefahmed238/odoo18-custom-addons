from odoo import api, fields, models, _, SUPERUSER_ID
import functools
import logging
import contextlib
import re
from odoo import _, api, fields, models
from odoo.addons.base.models.res_users import check_identity
from odoo.exceptions import AccessDenied, UserError
from odoo.http import request
from datetime import datetime, timedelta
import pytz

_logger = logging.getLogger(__name__)

compress = functools.partial(re.sub, r'\s', '')

def now(**kwargs):
    return datetime.now() + timedelta(**kwargs)

class ResUsers(models.Model):
    _inherit = 'res.users'

    totp_whatsapp_enabled = fields.Boolean(string="Two-factor authentication using Whatsapp")
    
    def _mfa_type(self):
        r = super()._mfa_type()
        if r is not None:
            return r
        if self.totp_whatsapp_enabled and not request.session.get('login_by_whatsapp'):
            return 'totp_whatsapp'

    def _mfa_url(self):
        r = super()._mfa_url()
        if r is not None:
            return r
        if self._mfa_type() == 'totp_whatsapp':
            return '/web/login/whatsapp-totp'

    @check_identity
    def action_whatsapp_totp_disable(self):
        logins = ', '.join(map(repr, self.mapped('login')))
        if not (self == self.env.user or self.env.user._is_admin() or self.env.su):
            _logger.info("2FA disable: REJECT for %s (%s) by uid #%s", self, logins, self.env.user.id)
            return False

        self.revoke_all_devices()
        self.totp_whatsapp_enabled = False
        _logger.info("2FA for whatsapp disable: SUCCESS for %s (%s) by uid #%s", self, logins, self.env.user.id)
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'warning',
                'message': _("Two-factor authentication disabled for the following user(s): %s",
                             ', '.join(self.mapped('name'))),
                'next': {'type': 'ir.actions.act_window_close'},
            }
        }


    @check_identity
    def action_totp_whatsapp_enable_wizard(self):
        if self.env.user != self:
            raise UserError(_("Two-factor authentication using whatsapp can only be enabled for yourself"))

        if self.totp_whatsapp_enabled:
            raise UserError(_("Two-factor authentication using whatsapp already enabled"))

        wa_account = self.env['ir.config_parameter'].sudo().get_param('odoo_whatsapp_login.wa_account')
        wa_account_id = self.env['whatsapp.account'].sudo().browse(int(wa_account))
        wa_template_id = self.env['ir.config_parameter'].sudo().get_param('odoo_whatsapp_login.otp_whatsapp_template')
        whatsapp_template = self.env['whatsapp.template'].sudo().browse(int(wa_template_id))
        user_partner = wa_account_id.notify_user_ids and wa_account_id.notify_user_ids[0] or []
        if wa_account_id and whatsapp_template and user_partner:
            whatsapp_composer = self.env["whatsapp.composer"].with_user(user_partner.id).with_context(
                {"active_id": self.partner_id.id}).create({
                "phone": self.partner_id.mobile,
                "wa_template_id": whatsapp_template.id,
                "res_model": self.partner_id._name,
            })
            whatsapp_composer._send_whatsapp_template()
        w = self.env['whatsapp.auth.totp'].create({
            'user_id': self.id,
        })
        return {
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_model': 'whatsapp.auth.totp',
            'name': _("Two-Factor Authentication with WhatsApp Activation"),
            'res_id': w.id,
            'views': [(False, 'form')],
            'context': self.env.context,
        }

    def whatsapp_reset_password(self, mobile):
        users = self.search([]).filtered(lambda x: x.partner_id.mobile.strip('+').replace(" ", "") == mobile.strip('+') if x.partner_id.mobile else False)
        if not users:
            raise Exception(_('No account found for this mobile number'))
        if len(users) > 1:
            raise Exception(_('Multiple accounts found for this mobile number'))
        return users.action_whatsapp_reset_password()

    def action_whatsapp_reset_password(self):
        try:
            if self.filtered(lambda user: not user.active):
                raise UserError(_("You cannot perform this action on an archived user."))

            self.mapped('partner_id').signup_prepare(signup_type="reset")
            self.mapped('partner_id').signup_url = self.mapped('partner_id')._get_signup_url()

            for user in self:
                wa_account = self.env['ir.config_parameter'].sudo().get_param('odoo_whatsapp_login.wa_account')
                wa_account_id = self.env['whatsapp.account'].sudo().browse(int(wa_account))
                wa_template_id = self.env['ir.config_parameter'].sudo().get_param(
                    'odoo_whatsapp_login.reset_password_whatsapp_template')
                whatsapp_template = self.env['whatsapp.template'].sudo().browse(int(wa_template_id))
                user_partner = wa_account_id.notify_user_ids and wa_account_id.notify_user_ids[0] or []
                if not user.partner_id.mobile:
                    raise UserError(_("Cannot send whatsapp message: user linked partner %s has no mobile number.", user.partner_id.name))
                with contextlib.closing(self.env.cr.savepoint()):
                     if wa_account_id and whatsapp_template and user_partner:
                         whatsapp_composer = self.env["whatsapp.composer"].with_user(user_partner.id).with_context(
                             {"active_id": user.partner_id.id}).create({
                             "phone": user.partner_id.mobile,
                             "wa_template_id": whatsapp_template.id,
                             "res_model": user.partner_id._name,
                         })
                         whatsapp_composer._send_whatsapp_template()
                     else:
                         raise UserError(_("Reset password whatsapp template not configured"))
                _logger.info("Password reset whatsapp message sent for user <%s> to <%s>", user.login, user.partner_id.mobile)
        except Exception as e:
            raise UserError(e)

    @classmethod
    def _login(cls, db, credential, user_agent_env):
        login = credential['login']
        ip = request.httprequest.environ['REMOTE_ADDR'] if request else 'n/a'
        if request.params.get('otp'):
            credential.update({'type': 'otp'})
            try:
                with cls.pool.cursor() as cr:
                    self = api.Environment(cr, SUPERUSER_ID, {})[cls._name]
                    with self._assert_can_auth(user=login):
                        user = self.search(self._get_login_domain(login), order=self._get_login_order(), limit=1)
                        if not user:
                            raise AccessDenied()
                        user = user.with_user(user)
                        self.env.cr.execute(
                            "SELECT COALESCE(password, '') FROM res_users WHERE id=%s",
                            [user.id]
                        )
                        hashed = self.env.cr.fetchone()[0]
                        if not credential['password'] == hashed:
                            auth_info = user._check_credentials(credential['password'], user_agent_env)
                        else:
                            auth_info = {
                                'uid': user.id,
                                'auth_method': credential['type'],
                                'mfa': 'default',
                            }
                        tz = request.cookies.get('tz') if request else None
                        if tz in pytz.all_timezones and (not user.tz or not user.login_date):
                            # first login or missing tz -> set tz to browser tz
                            user.tz = tz
                        user._update_last_login()
            except AccessDenied:
                _logger.info("Login failed for db:%s login:%s from %s", db, login, ip)
                raise

            _logger.info("Login successful for db:%s login:%s from %s", db, login, ip)

            return auth_info
        else:
            return super()._login(db, credential, user_agent_env)

