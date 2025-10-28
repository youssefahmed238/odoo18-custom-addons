/** @odoo-module **/

import { PosStore } from "@point_of_sale/app/store/pos_store";
import { patch } from "@web/core/utils/patch";

patch(PosStore.prototype, {
    async processServerData() {
        await super.processServerData(...arguments);

        const sessionRecords = this.data.records['pos.session'];

        // `sessionRecords` is a Map -> get the first record
        const firstSession = sessionRecords && [...sessionRecords.values()][0];

        const loadedData = firstSession || {};

        if (loadedData.is_allow_payment_ref !== undefined) {
            this.is_allow_payment_ref = loadedData.is_allow_payment_ref === 'True' || loadedData.is_allow_payment_ref === true;
            this.user_payment_reference = '';
        } else {
            this.is_allow_payment_ref = false;
        }
    },
});
