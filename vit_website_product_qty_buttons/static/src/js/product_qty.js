/** @odoo-module **/

import publicWidget from '@web/legacy/js/public/public_widget';
import { rpc } from '@web/core/network/rpc';

publicWidget.registry.WebsiteProductQtyButtons = publicWidget.Widget.extend({
    selector: '.o_wsale_qty_wrapper',
    events: {
        'click .o_qty_plus': '_onAdd',
        'click .o_qty_minus': '_onSubtract',
        'change .o_product_qty': '_onChange',
    },

    start() {
        this._super(...arguments);
        this._isUpdating = false;
    },

    async willStart() {
        await this._super(...arguments);
        if (!window.cartLoaded) {
            window.cartLoaded = true;
            await this._loadCartQuantities();
        }
    },

    async _loadCartQuantities() {
        try {
            const result = await rpc('/shop/cart/info', {});
            console.log('Cart info loaded:', result);
            const cartItems = result.cart_items || {};

            document.querySelectorAll('.o_wsale_qty_wrapper').forEach((wrapper) => {
                const pid = parseInt(wrapper.dataset.productId);
                const input = wrapper.querySelector('.o_product_qty');
                if (pid) {
                    for (const key in cartItems) {
                        if (cartItems[key].product_id === pid) {
                            input.value = parseInt(cartItems[key].quantity);
                            break;
                        }
                    }
                } else {
                    input.value = 0;
                }
            });
        } catch (error) {
            console.error('Error loading cart quantities:', error);
        }
    },

    _getProductId(ev) {
        const wrapper = ev.currentTarget.closest('.o_wsale_qty_wrapper');
        if (wrapper && wrapper.dataset.productId) {
            return parseInt(wrapper.dataset.productId);
        }
        return null;
    },

    async _onAdd(ev) {
        if (this._isUpdating) return;

        const wrapper = ev.currentTarget.closest('.o_wsale_qty_wrapper');
        const input = wrapper.querySelector('.o_product_qty');
        const productId = this._getProductId(ev);

        if (!productId) {
            console.error('Product ID not found');
            return;
        }

        const currentQty = parseInt(input.value || 0);
        input.value = currentQty + 1;

        await this._updateCart(productId, 1);
    },

    async _onSubtract(ev) {
        if (this._isUpdating) return;

        const wrapper = ev.currentTarget.closest('.o_wsale_qty_wrapper');
        const input = wrapper.querySelector('.o_product_qty');
        const productId = this._getProductId(ev);

        if (!productId) {
            console.error('Product ID not found');
            return;
        }

        const currentQty = parseInt(input.value || 0);
        if (currentQty <= 0) return;

        input.value = currentQty - 1;
        await this._updateCart(productId, -1);
    },

    _onChange(ev) {
        const val = parseInt(ev.target.value || 0);
        if (val < 0) ev.target.value = 0;
    },

    async _updateCart(productId, addQty, productInfo, event) {
        this._isUpdating = true;

        try {
            const result = await rpc('/shop/cart/update_json', {
                product_id: parseInt(productId),
                add_qty: addQty,
            });

            if (result.cart_quantity !== undefined) {
                this._updateCartBadge(result.cart_quantity);
            } else {
                this._updateCartBadge(0);
            }

        } catch (error) {
            console.error('Error updating cart:', error);
        } finally {
            this._isUpdating = false;
        }
    },

    _updateCartBadge(quantity) {
        const cardQuantity = document.querySelector('.my_cart_quantity');
        cardQuantity.textContent = quantity;

        if (quantity > 0) {
            cardQuantity.style.display = '';
            cardQuantity.classList.remove('d-none');
            cardQuantity.parentElement?.classList.remove('d-none');
        } else {
            cardQuantity.style.display = 'none';
        }

        window.dispatchEvent(new CustomEvent('update_cart_quantity', {
            detail: { cart_quantity: quantity }
        }));
    },
});

export default publicWidget.registry.WebsiteProductQtyButtons;