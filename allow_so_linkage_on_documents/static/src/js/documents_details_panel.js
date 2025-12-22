/** @odoo-module */

import { DocumentsDetailsPanel } from "@documents/components/documents_details_panel/documents_details_panel";
import { patch } from "@web/core/utils/patch";

// Extend the DocumentsDetailsPanel to properly handle custom fields
patch(DocumentsDetailsPanel.prototype, {
    setup() {
        super.setup();
        // Ensure the custom field is properly initialized in the record
        if (this.record?.data && !this.record.fieldsInfo?.custom_sale_order_id) {
            // Add field metadata if missing
            if (this.record.fieldsInfo) {
                this.record.fieldsInfo.custom_sale_order_id = {
                    type: 'many2one',
                    relation: 'sale.order',
                    string: 'Sale Order',
                    readonly: false,
                };
            }
        }
    }
});
