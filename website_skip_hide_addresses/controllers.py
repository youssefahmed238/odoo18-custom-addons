# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale


class SkipHideAddressController(WebsiteSale):
    @http.route(['/shop/checkout'], type='http', auth="public", website=True, sitemap=False)
    def checkout(self, **post):
        order = request.website.sale_get_order()

        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection
        '''
        if order.partner_id.id == request.website.user_id.sudo().partner_id.id:
            return request.redirect('/shop/address')

        redirection = self.checkout_check_address(order)
        if redirection:
            return redirection
        '''
        values = self.checkout_values(**post)

        if post.get('express'):
            return request.redirect('/shop/confirm_order')

        values.update({'website_sale_order': order})

        # Avoid useless rendering if called in ajax
        if post.get('xhr'):
            return 'ok'
        return request.render("website_sale.checkout", values)

    def checkout_check_address(self, order):
        '''
        billing_fields_required = self._get_mandatory_fields_billing(order.partner_id.country_id.id)
        if not all(order.partner_id.read(billing_fields_required)[0].values()):
            return request.redirect('/shop/address?partner_id=%d' % order.partner_id.id)

        shipping_fields_required = self._get_mandatory_fields_shipping(order.partner_shipping_id.country_id.id)
        if not all(order.partner_shipping_id.read(shipping_fields_required)[0].values()):
            return request.redirect('/shop/address?partner_id=%d' % order.partner_shipping_id.id)
        '''
        
