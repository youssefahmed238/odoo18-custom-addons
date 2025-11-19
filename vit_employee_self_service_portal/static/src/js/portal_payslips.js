/** @odoo-module */

import publicWidget from "@web/legacy/js/public/public_widget";
import PortalSidebar from "@portal/js/portal_sidebar";
import {PortalHomeCounters} from '@portal/js/portal';

PortalHomeCounters.include({
    _getCountersAlwaysDisplayed() {
        return this._super(...arguments).concat(['payslips_count']);
    },
});

publicWidget.registry.PayslipsPortalSidebar = PortalSidebar.extend({
    selector: '.o_portal_payslip_sidebar',
    events: {
        'click .o_portal_payslip_print': '_printPayslipReport',
    },
    _printPayslipReport: function (ev) {
        ev.preventDefault();
        let report_url = $(ev.currentTarget).attr('report_url');
        this.printPdf(report_url);
    }
})