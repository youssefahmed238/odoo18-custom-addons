/** @odoo-module **/

import publicWidget from '@web/legacy/js/public/public_widget';

publicWidget.registry.WebsiteProductQtyButtons = publicWidget.Widget.extend({
    selector: '.o_wsale_qty_wrapper',
    events: {
        'click .o_qty_plus': '_onAdd',
        'click .o_qty_minus': '_onSubtract',
        'change .o_product_qty': '_onChange',
    },

    async _onAdd(ev) {
        const wrapper = ev.currentTarget.closest('.o_wsale_qty_wrapper');
        const input = wrapper.querySelector('.o_product_qty');
        const productCard = wrapper.closest('[data-product-template-id]');
        const productId = productCard?.dataset?.productTemplateId;

        const newQty = parseInt(input.value || 0) + 1;
        input.value = newQty;

        if (productId) {
            await this._updateCart(productId, newQty);
        }
    },

    async _onSubtract(ev) {
        const wrapper = ev.currentTarget.closest('.o_wsale_qty_wrapper');
        const input = wrapper.querySelector('.o_product_qty');
        const productCard = wrapper.closest('[data-product-template-id]');
        const productId = productCard?.dataset?.productTemplateId;

        let newQty = parseInt(input.value || 0);
        if (newQty > 0) newQty -= 1;
        input.value = newQty;

        if (productId) {
            await this._updateCart(productId, newQty);
        }
    },

    _onChange(ev) {
        const val = parseInt(ev.target.value || 0);
        if (val < 0) ev.target.value = 0;
    },

    async _updateCart(productId, quantity) {
        try {
            const response = await fetch('/shop/cart/update_json', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    product_id: parseInt(productId),
                    set_qty: quantity,
                }),
            });

            const result = await response.json();

            // Update header cart quantity
            const cartQty = document.querySelector('.my_cart_quantity');
            if (cartQty && result.cart_quantity !== undefined) {
                cartQty.textContent = result.cart_quantity;
            }
        } catch (error) {
            console.error('Error updating cart:', error);
        }
    },
});

export default publicWidget.registry.WebsiteProductQtyButtons;
