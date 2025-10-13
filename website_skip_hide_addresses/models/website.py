# -*- coding: utf-8 -*-

from odoo import models
from odoo.tools.translate import LazyTranslate

_lt = LazyTranslate(__name__)


class Website(models.Model):
    _inherit = 'website'

    def _get_checkout_step_list(self):
        """ Override to skip and hide the delivery step.

        Returns a simplified checkout flow that goes directly from cart review to payment,
        completely bypassing the delivery/address step.
        """
        self.ensure_one()
        is_extra_step_active = self.viewref('website_sale.extra_info').active
        redirect_to_sign_in = self.account_on_checkout == 'mandatory' and self.is_public_user()

        # Start with cart step - but redirect directly to extra_info or confirm_order
        steps = [(['website_sale.cart'], {
            'name': _lt("Review Order"),
            'current_href': '/shop/cart',
            'main_button': _lt("Sign In") if redirect_to_sign_in else _lt("Checkout"),
            'main_button_href': f'{"/web/login?redirect=" if redirect_to_sign_in else ""}{"/shop/extra_info" if is_extra_step_active else "/shop/confirm_order"}',
            'back_button': _lt("Continue shopping"),
            'back_button_href': '/shop',
        })]

        # Add extra info step if active (skip delivery, go to extra info)
        if is_extra_step_active:
            steps.append((['website_sale.extra_info'], {
                'name': _lt("Extra Info"),
                'current_href': '/shop/extra_info',
                'main_button': _lt("Continue checkout"),
                'main_button_href': '/shop/confirm_order',
                'back_button': _lt("Back to cart"),
                'back_button_href': '/shop/cart',
            }))

        # Add payment step (skip delivery, back to cart or extra_info)
        steps.append((['website_sale.payment'], {
            'name': _lt("Payment"),
            'current_href': '/shop/payment',
            'back_button': _lt("Back to extra info") if is_extra_step_active else _lt("Back to cart"),
            'back_button_href': '/shop/extra_info' if is_extra_step_active else '/shop/cart',
        }))

        return steps
