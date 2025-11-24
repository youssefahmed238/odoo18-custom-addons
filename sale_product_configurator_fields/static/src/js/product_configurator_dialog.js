/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { ProductConfiguratorDialog } from "@sale/js/product_configurator_dialog/product_configurator_dialog";
import { useSubEnv } from "@odoo/owl";
import { rpc } from "@web/core/network/rpc";

patch(ProductConfiguratorDialog.prototype, {
    setup() {
        super.setup();

        // Override the URLs to use our custom routes
        this.getValuesUrl = '/sale/product_configurator/get_costume_values';
        this.getOptionalProductsUrl = '/sale/product_configurator/get_costume_optional_products';

        this.state.accessoryProducts = [];
        this.state.alternativeProducts = [];
    },

    async _loadData(onlyMainProduct) {
        const result = await super._loadData(onlyMainProduct);

        // Add the new product lists to the state
        this.state.accessoryProducts = result.accessory_products || [];
        this.state.alternativeProducts = result.alternative_products || [];

        return result;
    },

    async onConfirm() {
        const mainProduct = this.state.products[0];

        // Get all selected products (optional, accessory, alternative)
        const selectedOptionalProducts = this.state.optionalProducts.filter(product => product.quantity > 0);
        const selectedAccessoryProducts = this.state.accessoryProducts.filter(product => product.quantity > 0);
        const selectedAlternativeProducts = this.state.alternativeProducts.filter(product => product.quantity > 0);

        // Combine all optional-type products
        const allOptionalProducts = [
            ...selectedOptionalProducts,
            ...selectedAccessoryProducts,
            ...selectedAlternativeProducts
        ];

        await this.props.save(mainProduct, allOptionalProducts);
        this.props.close();
    },

    /**
     * Override _addProduct to handle all product types
     */
    async _addProduct(productTmplId) {
        // Check if it's an accessory product
        let index = this.state.accessoryProducts.findIndex(
            p => p.product_tmpl_id === productTmplId
        );
        if (index >= 0) {
            this.state.products.push(...this.state.accessoryProducts.splice(index, 1));
            // Fetch all product types from the server with the parent combination.
            const product = this._findProduct(productTmplId);
            try {
                const result = await this._getOptionalProducts(product);

                // Ensure result is properly structured and filter out products that are already loaded
                const newOptionalProducts = Array.isArray(result.optional_products)
                    ? result.optional_products.filter(p => !this._findProduct(p.product_tmpl_id))
                    : [];
                const newAccessoryProducts = Array.isArray(result.accessory_products)
                    ? result.accessory_products.filter(p => !this._findProduct(p.product_tmpl_id))
                    : [];
                const newAlternativeProducts = Array.isArray(result.alternative_products)
                    ? result.alternative_products.filter(p => !this._findProduct(p.product_tmpl_id))
                    : [];

                this.state.optionalProducts.push(...newOptionalProducts);
                this.state.accessoryProducts.push(...newAccessoryProducts);
                this.state.alternativeProducts.push(...newAlternativeProducts);
            } catch (error) {
                console.error("Error fetching optional products:", error);
            }
            return;
        }

        // Check if it's an alternative product
        index = this.state.alternativeProducts.findIndex(
            p => p.product_tmpl_id === productTmplId
        );
        if (index >= 0) {
            this.state.products.push(...this.state.alternativeProducts.splice(index, 1));
            // Fetch all product types from the server with the parent combination.
            const product = this._findProduct(productTmplId);
            try {
                const result = await this._getOptionalProducts(product);

                // Ensure result is properly structured and filter out products that are already loaded
                const newOptionalProducts = Array.isArray(result.optional_products)
                    ? result.optional_products.filter(p => !this._findProduct(p.product_tmpl_id))
                    : [];
                const newAccessoryProducts = Array.isArray(result.accessory_products)
                    ? result.accessory_products.filter(p => !this._findProduct(p.product_tmpl_id))
                    : [];
                const newAlternativeProducts = Array.isArray(result.alternative_products)
                    ? result.alternative_products.filter(p => !this._findProduct(p.product_tmpl_id))
                    : [];

                this.state.optionalProducts.push(...newOptionalProducts);
                this.state.accessoryProducts.push(...newAccessoryProducts);
                this.state.alternativeProducts.push(...newAlternativeProducts);
            } catch (error) {
                console.error("Error fetching optional products:", error);
            }
            return;
        }

        // Check if it's an optional product
        index = this.state.optionalProducts.findIndex(
            p => p.product_tmpl_id === productTmplId
        );
        if (index >= 0) {
            this.state.products.push(...this.state.optionalProducts.splice(index, 1));
            // Fetch all product types from the server with the parent combination.
            const product = this._findProduct(productTmplId);
            try {
                const result = await this._getOptionalProducts(product);

                // Ensure result is properly structured and filter out products that are already loaded
                const newOptionalProducts = Array.isArray(result.optional_products)
                    ? result.optional_products.filter(p => !this._findProduct(p.product_tmpl_id))
                    : [];
                const newAccessoryProducts = Array.isArray(result.accessory_products)
                    ? result.accessory_products.filter(p => !this._findProduct(p.product_tmpl_id))
                    : [];
                const newAlternativeProducts = Array.isArray(result.alternative_products)
                    ? result.alternative_products.filter(p => !this._findProduct(p.product_tmpl_id))
                    : [];

                this.state.optionalProducts.push(...newOptionalProducts);
                this.state.accessoryProducts.push(...newAccessoryProducts);
                this.state.alternativeProducts.push(...newAlternativeProducts);
            } catch (error) {
                console.error("Error fetching optional products:", error);
            }
            return;
        }

        // If we get here, it's not one of our tracked products - shouldn't happen
        console.warn("Product not found in any product list:", productTmplId);
    },

    /**
     * Override _removeProduct to handle accessory and alternative products
     */
    _removeProduct(productTmplId) {
        const index = this.state.products.findIndex(p => p.product_tmpl_id === productTmplId);
        if (index >= 0) {
            const product = this.state.products.splice(index, 1)[0];

            // Determine where to put the product back based on its original type
            if (product.product_type === 'accessory') {
                this.state.accessoryProducts.push(product);
            } else if (product.product_type === 'alternative') {
                this.state.alternativeProducts.push(product);
            } else {
                // Default behavior for optional products
                this.state.optionalProducts.push(product);
            }

            // Remove child products - same logic as original
            for (const childProduct of this._getChildProducts(productTmplId)) {
                this._removeProduct(childProduct.product_tmpl_id);
                this.state.optionalProducts.splice(
                    this.state.optionalProducts.findIndex(
                        p => p.product_tmpl_id === childProduct.product_tmpl_id
                    ), 1
                );
            }
        }
    },

    /**
     * Override to handle accessory and alternative products in all product searches
     */
    _findProduct(productTmplId) {
        return this.state.products.find(p => p.product_tmpl_id === productTmplId) ||
               this.state.optionalProducts.find(p => p.product_tmpl_id === productTmplId) ||
               this.state.accessoryProducts.find(p => p.product_tmpl_id === productTmplId) ||
               this.state.alternativeProducts.find(p => p.product_tmpl_id === productTmplId);
    }
});

