# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale


class SkipHideAddressController(WebsiteSale):

    @http.route(['/shop/address'], type='http', methods=['GET', 'POST'], auth='public', website=True, sitemap=False)
    def shop_address(self, **kwargs):
        """Block address page - redirect to checkout."""
        return request.redirect('/shop/checkout')

    @http.route(['/shop/address/submit'], type='http', methods=['POST'], auth='public', website=True, sitemap=False)
    def shop_address_submit(self, **kwargs):
        """Block address submission - redirect to checkout."""
        return request.redirect('/shop/checkout')

    def _check_cart_and_addresses(self, order_sudo):
        """Override to skip address validation, ensure same billing/delivery address, and only check cart."""
        cart_check = self._check_cart(order_sudo)
        if cart_check:
            return cart_check

        # Ensure delivery address is same as billing address when skipping address validation
        if order_sudo.partner_id and order_sudo.partner_shipping_id != order_sudo.partner_invoice_id:
            order_sudo.partner_invoice_id = order_sudo.partner_shipping_id

        return None

    def _check_addresses(self, order_sudo):
        """Override to always pass address validation."""
        return None

    def _check_billing_address(self, partner_sudo):
        """Override to always pass billing validation."""
        return None

    def _check_delivery_address(self, partner_sudo):
        """Override to always pass delivery validation."""
        return None
