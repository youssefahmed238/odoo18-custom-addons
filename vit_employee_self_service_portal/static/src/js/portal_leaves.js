/** @odoo-module */

import {PortalHomeCounters} from '@portal/js/portal';
import publicWidget from '@web/legacy/js/public/public_widget';

PortalHomeCounters.include({
    /**
     * @override
     */
    _getCountersAlwaysDisplayed() {
        return this._super(...arguments).concat(['leaves_count']);
    },
});

publicWidget.registry.PortalLeaves = publicWidget.Widget.extend({
    selector: '.o_request_leave_details',

    events: {
        'change #leave_attach': '_onChangeLeaveAttachFile',
    },

    start() {
        return this._super(...arguments);
    },

    _onChangeLeaveAttachFile(ev) {
        const fileInput = ev.currentTarget;
        if (!fileInput.files || !fileInput.files[0]) {
            return;
        }
        const reader = new FileReader();
        reader.onload = (e) => {
            // Store base64 in a hidden input for your controller to read
            $('.leave_attach_class').val(e.target.result);
        };
        reader.readAsDataURL(fileInput.files[0]);
    },
});
