/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { ProductList } from "@sale/js/product_list/product_list";

patch(ProductList.prototype, {
    setup() {
        super.setup();
        // Override title if provided in props
        if (this.props.title) {
            this.optionalProductsTitle = this.props.title;
        }
    }
});

// Extend the props to include title
Object.assign(ProductList.props, {
    title: { type: String, optional: true },
});
