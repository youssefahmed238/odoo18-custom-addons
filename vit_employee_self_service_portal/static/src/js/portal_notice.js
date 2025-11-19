/** @odoo-module */

import publicWidget from "@web/legacy/js/public/public_widget";
import PortalSidebar from "@portal/js/portal_sidebar";
import {PortalHomeCounters} from '@portal/js/portal';

PortalHomeCounters.include({
    _getCountersAlwaysDisplayed() {
        return this._super(...arguments).concat(['notices_count']);
    },
});

publicWidget.registry.NoticePortalSidebar = PortalSidebar.extend({
    selector: '.o_portal_notice_sidebar',
    events: {
        'click .o_portal_notice_print': '_printNoticeReport',
    },
    _printNoticeReport: function (ev) {
        ev.preventDefault();
        let report_url = $(ev.currentTarget).attr('report_url');
        this.printPdf(report_url);
    }
})