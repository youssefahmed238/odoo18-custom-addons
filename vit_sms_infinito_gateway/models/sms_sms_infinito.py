# -*- coding: utf-8 -*-
import logging
import requests

from odoo import api, models

_logger = logging.getLogger(__name__)


class SmsSmsInfinito(models.Model):
    """
    Integrate Infinito Unified API with the core Odoo 18 SMS workflow.

    This implementation:
    - Hooks into sms.sms._send()
    - Respects Odoo's native SMS queues, marketing, and record-based SMS
    - Uses system parameters configured from Settings to route via Infinito
    """

    _inherit = "sms.sms"

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------
    def _infinito_is_enabled(self):
        icp = self.env["ir.config_parameter"].sudo()
        return icp.get_param("sms_infinito.enabled", "False") == "True"

    def _infinito_get_creds(self):
        icp = self.env["ir.config_parameter"].sudo()
        return {
            "client_id": icp.get_param("sms_infinito.client_id") or "",
            "client_password": icp.get_param("sms_infinito.client_password") or "",
            "sender_id": icp.get_param("sms_infinito.sender_id") or "",
        }

    def _infinito_call(self, number, text, creds):
        """
        Single HTTPS call to Infinito using query parameters, as per guide.
        """
        base_url = "https://api.goinfinito.me/unified/v2/send"
        params = {
            "clientid": creds["client_id"],
            "clientpassword": creds["client_password"],
            "from": creds["sender_id"],
            "to": number,
            "text": text,
        }

        resp = requests.get(base_url, params=params, timeout=15)
        body = resp.text or ""
        low = body.lower()

        _logger.info("Infinito SMS Request URL: %s", getattr(resp, "url", "N/A"))
        _logger.info("Infinito SMS Response: %s", body)

        # Success patterns from documentation: statuscode=0, statustext=Success, JSON with 200
        success = (
            resp.status_code == 200
            and (
                "statuscode=0" in low
                or "statustext=success" in low
                or '"statuscode":200' in low
                or '"status":"success"' in low
            )
        )

        msg_id = None
        if "guid=" in body:
            try:
                msg_id = body.split("guid=")[1].split("&")[0].strip()
            except Exception:  # noqa: BLE001
                msg_id = None

        return success, resp.status_code, body, msg_id

    # -------------------------------------------------------------------------
    # Core override
    # -------------------------------------------------------------------------
    def _send(self, unlink_failed=True, raise_exception=False, **kwargs):
        """
        Override of the sms.sms core send method.

        If Infinito is enabled & configured:
            -> send through Infinito
        Otherwise:
            -> fallback to original behavior via super()
        """
        # Work on a copy of recordset to avoid side effects
        msgs = self.filtered(lambda m: m.state in ("outgoing", "draft"))

        if not msgs:
            return super(SmsSmsInfinito, self)._send()

        if not self._infinito_is_enabled():
            # Use Odoo's default SMS sending (could be another provider)
            return super(SmsSmsInfinito, self)._send()

        creds = self._infinito_get_creds()
        if not (creds["client_id"] and creds["client_password"] and creds["sender_id"]):
            _logger.error(
                "Infinito SMS: Enabled but missing credentials/sender. "
                "Falling back to default SMS behavior."
            )
            return super(SmsSmsInfinito, self)._send()

        for sms in msgs:
            number = sms.number or ""
            text = sms.body or sms.body_html or sms.body_preview or ""

            if not number:
                _logger.warning("Infinito SMS: sms.sms(%s) has no number.", sms.id)
                sms.write(
                    {
                        "state": "error",
                        "error_code": "server_error",
                    }
                )
                continue

            if not text:
                _logger.warning("Infinito SMS: sms.sms(%s) has empty body.", sms.id)
                sms.write(
                    {
                        "state": "error",
                        "failure_type": "sms_server",
                        # "failure_reason": "Empty SMS body for Infinito.",
                    }
                )
                continue

            try:
                success, status, body, msg_id = self._infinito_call(number, text, creds)
                if success:
                    vals = {
                        "state": "sent",
                    }
                    if msg_id:
                        vals["message_id"] = msg_id
                    sms.write(vals)
                else:
                    sms.write(
                        {
                            "state": "error",
                            "failure_type": "sms_server",
                            # "failure_reason": body or f"Infinito HTTP {status}",
                        }
                    )
            except Exception as e:  # noqa: BLE001
                _logger.exception(
                    "Infinito SMS: Exception sending sms.sms(%s) to %s: %s",
                    sms.id,
                    number,
                    e,
                )
                sms.write(
                    {
                        "state": "error",
                        "failure_type": "sms_server",
                        # "failure_reason": str(e),
                    }
                )

        # Return True like core implementation
        return True
