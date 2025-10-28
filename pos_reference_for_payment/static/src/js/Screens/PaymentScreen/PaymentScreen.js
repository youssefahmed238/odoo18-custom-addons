/** @odoo-module **/

import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { TextInputPopup } from "@point_of_sale/app/utils/input_popups/text_input_popup";
import { useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

let order_list = [];

patch(PaymentScreen.prototype, {
    setup() {
        super.setup(...arguments);
        this.orm = useService("orm");
        this.state = useState({
            code: false,
        });
    },

    async onClickPaymentReference() {
        await this.dialog.add(TextInputPopup, {
            title: _t("Payment Reference"),
            startingValue: this.state.code || "",
            placeholder: _t('eg:PREF16'),
            getPayload: (value) => {
                const trimmedCode = value.trim();
                if (trimmedCode !== '') {
                    const currentOrder = this.pos.get_order();
                    this.env.services.pos.user_payment_reference = trimmedCode;
                    this.state.code = trimmedCode;
                    order_list.push({
                        'name': currentOrder.name,
                        'code': trimmedCode
                    });
                }
            },
        });
    },

    async _finalizeValidation() {
        await super._finalizeValidation(...arguments);

        console.log('order_list', order_list);

        if (order_list.length > 0) {
            await this.orm.call(
                'pos.payment',
                'get_payment_reference',
                [[], order_list],
            );
            order_list = [];
        }
    }
});