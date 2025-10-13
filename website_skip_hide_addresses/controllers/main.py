# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale


class SkipHideAddressController(WebsiteSale):

    @http.route(['/shop/checkout'], type='http', auth="public", website=True, sitemap=False)
    def shop_checkout(self, try_skip_step=None, **query_params):
        """Override checkout to skip delivery/address step and redirect to payment."""
        order_sudo = request.website.sale_get_order()

        redirection = self._check_cart(order_sudo)
        if redirection:
            return redirection

        self._ensure_addresses_are_set(order_sudo)

        extra_step = request.website.viewref('website_sale.extra_info')
        if extra_step.active:
            return request.redirect("/shop/extra_info")
        else:
            return request.redirect("/shop/payment")

    @http.route(['/shop/address'], type='http', methods=['GET'], auth='public', website=True, sitemap=False)
    def shop_address(self, partner_id=None, address_type='billing', use_delivery_as_billing=None, **query_params):
        """Override address page to redirect to payment."""
        order_sudo = request.website.sale_get_order()
        if order_sudo:
            self._ensure_addresses_are_set(order_sudo)
        return request.redirect('/shop/payment')

    @http.route(['/shop/address/submit'], type='http', methods=['POST'], auth='public', website=True, sitemap=False)
    def shop_address_submit(self, **form_data):
        """Override address submit to redirect to payment."""
        order_sudo = request.website.sale_get_order()
        if order_sudo:
            self._ensure_addresses_are_set(order_sudo)
        return request.redirect('/shop/payment')

    def _ensure_addresses_are_set(self, order_sudo):
        """Ensure delivery address is same as billing address and addresses are properly set."""
        if not order_sudo:
            return

        if not order_sudo._is_anonymous_cart():
            current_partner = request.env.user.partner_id
            order_sudo.partner_id = current_partner
            order_sudo.partner_invoice_id = current_partner
            order_sudo.partner_shipping_id = current_partner
        elif order_sudo.partner_id:
            order_sudo.partner_invoice_id = order_sudo.partner_id
            order_sudo.partner_shipping_id = order_sudo.partner_id

        if not order_sudo.carrier_id:
            self._set_default_carrier(order_sudo)

    def _set_default_carrier(self, order_sudo):
        """Set a default shipping method if none is selected."""
        if not order_sudo or order_sudo.only_services:
            return

        # Try to get available carriers for the shipping partner
        carriers = request.env['delivery.carrier'].sudo().search([
            ('website_published', '=', True)
        ])

        if carriers:

            available_carriers = carriers.available_carriers(order_sudo.partner_shipping_id, order_sudo)

            if available_carriers:
                default_carrier = available_carriers[0]
                order_sudo.carrier_id = default_carrier.id

                try:
                    rate_result = default_carrier.rate_shipment(order_sudo)
                    if rate_result.get('success'):
                        order_sudo.set_delivery_line(default_carrier, rate_result.get('price', 0.0))
                except Exception:
                    order_sudo.set_delivery_line(default_carrier, 0.0)
            else:
                free_carriers = carriers.filtered(lambda c: c.fixed_price == 0.0 or c.delivery_type == 'fixed')
                if free_carriers:
                    order_sudo.carrier_id = free_carriers[0].id
                    order_sudo.set_delivery_line(free_carriers[0], 0.0)

    def _check_cart_and_addresses(self, order_sudo):
        """Override to skip address validation, ensure same billing/delivery address, and only check cart."""
        cart_check = self._check_cart(order_sudo)
        if cart_check:
            return cart_check

        self._ensure_addresses_are_set(order_sudo)

        return None

    def _check_shipping_method(self, order_sudo):
        """Override to ensure a shipping method is set and redirect to payment if not."""
        if not order_sudo._is_delivery_ready():
            self._set_default_carrier(order_sudo)
            return request.redirect('/shop/payment')

    def _check_addresses(self, order_sudo):
        """Override to always pass address validation and ensure addresses are set."""
        if order_sudo:
            self._ensure_addresses_are_set(order_sudo)
        return None

    def _check_billing_address(self, partner_sudo):
        """Override to always pass billing validation."""
        return True

    def _check_delivery_address(self, partner_sudo):
        """Override to always pass delivery validation."""
        return True
