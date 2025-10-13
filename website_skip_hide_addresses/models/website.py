from odoo import models
from odoo.tools.translate import _lt


class Website(models.Model):
    _inherit = 'website'

    def _get_checkout_step_list(self):
        """ Return an ordered list of steps with delivery step skipped.
        Flow: Review Order -> Extra Info (optional step) -> Payment (skipping Delivery step)
        """
        self.ensure_one()
        is_extra_step_active = self.viewref('website_sale.extra_info').active
        redirect_to_sign_in = self.account_on_checkout == 'mandatory' and self.is_public_user()

        # Start with Review Order step, but modify button to go directly to payment
        steps = [(['website_sale.cart'], {
            'name': _lt("Review Order"),
            'current_href': '/shop/cart',
            'main_button': _lt("Sign In") if redirect_to_sign_in else _lt("Checkout"),
            # Skip delivery and go directly to payment (or extra info if active)
            'main_button_href': f'{"/web/login?redirect=" if redirect_to_sign_in else ""}{"/shop/extra_info" if is_extra_step_active else "/shop/payment"}',
            'back_button': _lt("Continue shopping"),
            'back_button_href': '/shop',
        })]

        # Add Extra Info step if active (optional step)
        if is_extra_step_active:
            steps.append((['website_sale.extra_info'], {
                'name': _lt("Extra Info"),
                'current_href': '/shop/extra_info',
                'main_button': _lt("Continue checkout"),
                'main_button_href': '/shop/payment',  # Go directly to payment
                'back_button': _lt("Back to cart"),  # Go back to cart since delivery is skipped
                'back_button_href': '/shop/cart',
            }))

        # Add Payment step with modified back button
        steps.append((['website_sale.payment'], {
            'name': _lt("Payment"),
            'current_href': '/shop/payment',
            'back_button': _lt("Back to cart") if not is_extra_step_active else _lt("Back to extra info"),
            'back_button_href': '/shop/cart' if not is_extra_step_active else '/shop/extra_info',
        }))

        return steps
