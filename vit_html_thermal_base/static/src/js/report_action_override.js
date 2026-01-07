/** @odoo-module **/

import {ReportAction} from "@web/webclient/actions/reports/report_action";
import {patch} from "@web/core/utils/patch";

// Override the print method of ReportAction
patch(ReportAction.prototype, {
    /**
     * Override the print method to add custom behavior for thermal reports
     */
    print() {
        const thermalReports = [
            'vit_html_thermal_so.report_sale_order_thermal',

            'vit_html_thermal_invoice.report_invoice_thermal',

            'vit_html_thermal_payment.report_payment_thermal',

            'stock_thermal_reports.report_picking_thermal',
            'stock_thermal_reports.report_deliveryslip_thermal',
        ];

        if (this.props.report_name && thermalReports.includes(this.props.report_name)) {
            this.iframe.el.contentWindow.focus();
            this.iframe.el.contentWindow.print();
        } else {
            super.print();
        }
    },
});
