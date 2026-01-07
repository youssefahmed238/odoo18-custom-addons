/** @odoo-module **/

import {PivotRenderer} from "@web/views/pivot/pivot_renderer";
import {patch} from "@web/core/utils/patch";
import {useService} from "@web/core/utils/hooks";
import {useState} from "@odoo/owl";
import {user} from "@web/core/user";

patch(PivotRenderer.prototype, {
    setup() {
        super.setup();

        this.orm = useService("orm");

        this.state = useState({
            showPrintButton: false,
        });

        if (this.model?.metaData?.resModel === "warehouse.product") {
            this._checkUserUsingThermalPrinter();
        }
    },

    async _checkUserUsingThermalPrinter() {
        try {
            const result = await this.orm.read(
                'res.users',
                [user.userId],
                ['using_thermal_printer']
            );

            if (result && result.length > 0) {
                this.state.showPrintButton = result[0].using_thermal_printer;
            }
        } catch (error) {
            console.log('Could not load thermal printer setting:', error);
            this.state.showPrintButton = false;
        }
    },

    async onPrintReportClicked() {
        try {
            const action = await this.orm.call(
                'warehouse.product',
                'print_warehouse_product_thermal_report',
                [[]],
                {}
            );

            if (action) {
                await this.env.services.action.doAction(action);
            }
        } catch (error) {
            console.error('Error printing thermal report:', error);
            this.env.services.notification.add(
                'Error generating thermal report: ' + error.message,
                {type: 'danger'}
            );
        }
    }
});