/** @odoo-module **/

import {ReportAction} from "@web/webclient/actions/reports/report_action";
import {patch} from "@web/core/utils/patch";

// Override the print method of ReportAction
patch(ReportAction.prototype, {

    get thermalReports() {
        return [
            'vit_html_thermal_so.report_sale_order_thermal',

            'vit_html_thermal_invoice.report_invoice_thermal',

            'vit_html_thermal_payment.report_payment_thermal',

            'vit_html_thermal_warehouse_products.report_warehouse_product_thermal',

            'vit_html_thermal_stock.report_picking_thermal',

            'vit_html_thermal_stock.report_deliveryslip_thermal',
        ]
    },

    onIframeLoaded(ev) {
        super.onIframeLoaded(ev);

        if (this.props.report_name && this.thermalReports.includes(this.props.report_name)) {
            this.print().then(() => {
                console.log("Print command executed for thermal report.");
            }).catch((error) => {
                console.error("Error executing print command for thermal report:", error);
            });
        }

    },
    /**
     * Override the print method to add custom behavior for thermal reports
     */
    async print() {
        if (this.props.report_name && this.thermalReports.includes(this.props.report_name)) {
            // this.iframe.el.contentWindow.focus();
            // this.iframe.el.contentWindow.print();
            //
            // this.iframe.el.contentWindow.onafterprint = () => {
            //     const backButton = document.querySelector('.o_back_button a');
            //     if (backButton) {
            //         window.location.href = backButton.href;
            //     }
            // }
        } else {
            super.print();
        }
    },
});
