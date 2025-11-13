# -*- coding: utf-8 -*-
import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class InfinitoDLRController(http.Controller):
    """
    Endpoint to receive Delivery Reports from Infinito.

    Configure your DLR URL in Infinito as:
      https://YOUR_DOMAIN/infinito/dlr

    Map their parameters (MESSAGE_ID / CLIENT_GUID / MSG_STATUS, etc.)
    to the sms.sms.message_id & state.
    """

    @http.route("/infinito/dlr", type="http", auth="public", methods=["GET", "POST"], csrf=False)
    def infinito_dlr(self, **kwargs):
        _logger.info("Infinito DLR received: %s", kwargs)

        msg_status = (
            kwargs.get("MSG_STATUS")
            or kwargs.get("MESSAGE_STATUS")
            or kwargs.get("TEXT_STATUS")
            or kwargs.get("MSG_STATUS".lower())
            or ""
        )
        msg_status = (msg_status or "").strip().lower()

        message_id = (
            kwargs.get("MESSAGE_ID")
            or kwargs.get("CLIENT_GUID")
            or kwargs.get("CLIENT_SEQ_NUMBER")
        )

        if not message_id:
            # No identifier to match; acknowledge anyway to avoid retries
            return "OK"

        SmsSms = request.env["sms.sms"].sudo()
        sms_records = SmsSms.search([("message_id", "=", message_id)])

        if not sms_records:
            _logger.warning("Infinito DLR: No sms.sms found for message_id=%s", message_id)
            return "OK"

        delivered_keywords = {"delivered", "success", "000"}
        if msg_status in delivered_keywords:
            for sms in sms_records:
                try:
                    sms.write({"state": "delivered"})
                except Exception as e:  # noqa: BLE001
                    _logger.exception(
                        "Infinito DLR: Failed to mark sms.sms(%s) delivered: %s",
                        sms.id,
                        e,
                    )
        elif msg_status:
            for sms in sms_records:
                try:
                    if sms.state in ("outgoing", "sent"):
                        sms.write(
                            {
                                "state": "error",
                                "failure_type": "server_error",
                                "failure_reason": msg_status,
                            }
                        )
                except Exception as e:  # noqa: BLE001
                    _logger.exception(
                        "Infinito DLR: Failed to mark sms.sms(%s) error: %s",
                        sms.id,
                        e,
                    )

        return "OK"
