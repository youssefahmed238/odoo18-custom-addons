odoo.define("sh_pos_access_rights_hr.models", function (require) {
    "use strict";

    const { PosGlobalState, Order, Orderline } = require('point_of_sale.models');
    const Registries = require("point_of_sale.Registries");

    const shNotePosGlobalState = (PosGlobalState) => class shNotePosGlobalState extends PosGlobalState {

        async _processData(loadedData) {
            await super._processData(...arguments);
            var self = this
            self.db.all_employee = loadedData['hr.employee'] || [];
            self.db.employee_by_id = {};
            _.each(self.db.all_employee, function (each_employee) {
                self.db.employee_by_id[each_employee.id] = each_employee;
            });

            self.db.all_employee = JSON.parse(JSON.stringify(self.db.all_employee))
            self.db.employee_by_id = JSON.parse(JSON.stringify(self.db.employee_by_id))
            
        }
        
    }

    Registries.Model.extend(PosGlobalState, shNotePosGlobalState);

})