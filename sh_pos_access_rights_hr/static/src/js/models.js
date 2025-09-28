/** @odoo-module **/

import { PosStore } from "@point_of_sale/app/store/pos_store";
import { patch } from "@web/core/utils/patch";

patch(PosStore.prototype, {
    async processServerData() {
        await super.processServerData(...arguments);

        const employeeModel = this.models["hr.employee"];

        if (employeeModel) {
            this.db = this.db || {};
            this.db.all_employee = employeeModel.getAll() || [];
            this.db.employee_by_id = {};

            this.db.all_employee.forEach((employee) => {
                this.db.employee_by_id[employee.id] = employee;
            });
        }
    },
});
