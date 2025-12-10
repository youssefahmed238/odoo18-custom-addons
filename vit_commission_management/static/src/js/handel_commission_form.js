/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { ListController } from "@web/views/list/list_controller";

patch(ListController.prototype, {

    async openRecord(record, force = false) {

        if (record.resModel === "commission.line") {
            const invoice_id = record.data.invoice_id?.[0];

            if (invoice_id) {
                await this.actionService.doAction({
                    type: "ir.actions.act_window",
                    res_model: "account.move",
                    res_id: invoice_id,
                    views: [[false, "form"]],
                    target: "current",
                });
                return;
            }
        }

        return await super.openRecord(record, force);
    }

});
