/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.ApprovalsSearch = publicWidget.Widget.extend({
    selector: '.o_portal_approvals_container',

    events: {
        'input #approvalSearch': '_onSearchInput',
    },

    /**
     * Handle search input
     */
    _onSearchInput: function (ev) {
        const query = ev.currentTarget.value.toLowerCase();
        const rows = this.el.querySelectorAll("table tbody tr");
        let visibleCount = 0;

        rows.forEach(row => {
            // (subject, owner, location)
            const subject = row.querySelector("td:nth-child(1)")?.innerText.toLowerCase() || "";
            const owner   = row.querySelector("td:nth-child(2)")?.innerText.toLowerCase() || "";
            const location= row.querySelector("td:nth-child(7)")?.innerText.toLowerCase() || "";

            const match = subject.includes(query) || owner.includes(query) || location.includes(query);
            row.style.display = match ? '' : 'none';

            if (match) visibleCount++;
        });

        this._toggleNoResultsMessage(visibleCount === 0);
    },

    /**
     * Show/hide "No results" message
     */
    _toggleNoResultsMessage: function (show) {
        let msg = this.el.querySelector(".no-results-message");

        if (!msg) {
            msg = document.createElement("div");
            msg.className = "no-results-message text-center text-muted mt-3";
            msg.innerText = "No approvals found matching your search.";
            this.el.querySelector("table").after(msg);
        }

        msg.style.display = show ? '' : 'none';
    },
});
