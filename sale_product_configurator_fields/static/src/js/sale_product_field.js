/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { SaleOrderLineProductField } from "@sale/js/sale_product_field";
import { WarningDialog } from "@web/core/errors/error_dialogs";

patch(SaleOrderLineProductField.prototype, {
    async _onProductTemplateUpdate() {
        const result = await this.orm.call(
            'product.template',
            'get_single_product_variant',
            [this.props.record.data.product_template_id[0]],
            { context: this.context }
        );

        if (result && result.product_id) {
            if (this.props.record.data.product_id != result.product_id.id) {
                if (result.is_combo) {
                    await this.props.record.update({
                        product_id: [result.product_id, result.product_name],
                    });
                    this._openComboConfigurator();
                }
                // Override to add check for optional, accessory, and alternative products
                else if (result.has_optional_products || result.has_accessory_products || result.has_alternative_products) {
                    this._openProductConfigurator();
                }
                else {
                    await this.props.record.update({
                        product_id: [result.product_id, result.product_name],
                    });
                    this._onProductUpdate();
                }
            }
        } else {
            if (result && result.sale_warning) {
                const {type, title, message} = result.sale_warning;
                if (type === 'block') {
                    this.dialog.add(WarningDialog, { title, message });
                    this.props.record.update({'product_template_id': false});
                    return;
                } else if (type === 'warning') {
                    this.notification.add(message, { title, type: "warning" });
                }
            }
            if (!result.mode || result.mode === 'configurator') {
                this._openProductConfigurator();
            } else {
                this._openGridConfigurator();
            }
        }
    }
});
