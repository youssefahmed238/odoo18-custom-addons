odoo.define("sh_pos_access_rights_hr.screens", function (require) {
    "use strict";

    const CashierName = require("point_of_sale.CashierName");
    const Registries = require("point_of_sale.Registries");
    const ActionpadWidget = require("point_of_sale.ActionpadWidget");
    const ProductScreen = require("point_of_sale.ProductScreen");
    const PaymentScreen = require("point_of_sale.PaymentScreen");
    const NumpadWidget = require("point_of_sale.NumpadWidget");
    const TicketScreen = require('point_of_sale.TicketScreen')
    const NumberBuffer = require("point_of_sale.NumberBuffer");
    const { onMounted, onPatched, useRef } = owl;

    const ShProductScreen = (ProductScreen) =>
        class extends ProductScreen {
            async _updateSelectedOrderline(event) {
                var self = this;

                var is_Backspace = false
                const selectedLine = this.currentOrder.get_selected_orderline();
                
                if (self.env.pos.db.employee_by_id && self.env.pos.db.employee_by_id[self.env.pos.get_cashier().id] && self.env.pos.db.employee_by_id[self.env.pos.get_cashier().id].hr_group_disable_remove) {
                    if (selectedLine && event.detail.key === 'Backspace') {
                        is_Backspace = true
                    }
                }else{
                    is_Backspace = false
                }
                
                if(is_Backspace){
                    return false
                }
              
                super._updateSelectedOrderline(event);
            }

            onMounted() {
                var self = this;
                super.onMounted()
                var cashier_id = this.env.pos.get_cashier().id
                if (this.env.pos.config.module_pos_hr && this.env.pos.config.employee_ids && this.env.pos.config.employee_ids.length > 0 && cashier_id) {
                    if (self.env.pos.db.employee_by_id && self.env.pos.db.employee_by_id[self.env.pos.get_cashier().id] && self.env.pos.db.employee_by_id[self.env.pos.get_cashier().id].group_select_customer) {
                        $(".set-partner").prop("disabled", true);
                        $(".set-partner").addClass("sh_disabled");
                    } else {
                        $(".set-partner").prop("disabled", false);
                        $(".set-partner").removeClass("sh_disabled");
                    }
                    if (self.env.pos.db.employee_by_id && self.env.pos.db.employee_by_id[self.env.pos.get_cashier().id] && self.env.pos.db.employee_by_id[self.env.pos.get_cashier().id].disable_payment_id) {
                        $(".pay").prop("disabled", true);
                        $(".pay").addClass("sh_disabled");
                    } else {
                        $(".pay").prop("disabled", false);
                        $(".pay").removeClass("sh_disabled");
                    }
                    if (self.env.pos.db.employee_by_id && self.env.pos.db.employee_by_id[self.env.pos.get_cashier().id] && self.env.pos.db.employee_by_id[self.env.pos.get_cashier().id].group_disable_qty) {
                        $($(".mode-button")[0]).prop("disabled", true);
                        $($(".mode-button")[0]).addClass("sh_disabled_qty");
                    } else {
                        $($(".mode-button")[0]).prop("disabled", false);
                        $($(".mode-button")[0]).removeClass("sh_disabled_qty");
                    }
                    if (self.env.pos.db.employee_by_id && self.env.pos.db.employee_by_id[self.env.pos.get_cashier().id] && self.env.pos.db.employee_by_id[self.env.pos.get_cashier().id].group_disable_price) {
                        $($(".mode-button")[2]).prop("disabled", true);
                        $($(".mode-button")[2]).addClass("sh_disabled_qty");
                    } else {
                        $($(".mode-button")[2]).prop("disabled", false);
                        $($(".mode-button")[2]).removeClass("sh_disabled_qty");
                    }
                    if (self.env.pos.db.employee_by_id && self.env.pos.db.employee_by_id[self.env.pos.get_cashier().id] && self.env.pos.db.employee_by_id[self.env.pos.get_cashier().id].group_disable_discount) {
                        $($(".mode-button")[1]).prop("disabled", true);
                        $($(".mode-button")[1]).addClass("sh_disabled_qty");
                    } else {
                        $($(".mode-button")[1]).prop("disabled", false);
                        $($(".mode-button")[1]).removeClass("sh_disabled_qty");
                    }
                    if (self.env.pos.db.employee_by_id && self.env.pos.db.employee_by_id[self.env.pos.get_cashier().id] && self.env.pos.db.employee_by_id[self.env.pos.get_cashier().id].group_disable_plus_minus) {
                        $(".numpad-minus").prop("disabled", true);
                        $(".numpad-minus").addClass("sh_disabled");
                    } else {
                        $(".numpad-minus").prop("disabled", false);
                        $(".numpad-minus").removeClass("sh_disabled");
                    }
                    if (self.env.pos.db.employee_by_id && self.env.pos.db.employee_by_id[self.env.pos.get_cashier().id] && self.env.pos.db.employee_by_id[self.env.pos.get_cashier().id].group_disable_numpad) {
                        $(".number-char").prop("disabled", true);
                        $(".number-char").addClass("sh_disabled");
                    } else {
                        $(".number-char").prop("disabled", false);
                        $(".number-char").removeClass("sh_disabled");
                    }
                }
            }
        };
    Registries.Component.extend(ProductScreen, ShProductScreen);

    const SHPaymentScreen = (PaymentScreen) =>
        class extends PaymentScreen {
            onMounted() {
                
                var self = this;
                var cashier_id = this.env.pos.get_cashier().id
                if (this.env.pos.config.module_pos_hr && this.env.pos.config.employee_ids && this.env.pos.config.employee_ids.length > 0 && cashier_id) {
                    if (self.env.pos.db.employee_by_id && self.env.pos.db.employee_by_id[self.env.pos.get_cashier().id] && self.env.pos.db.employee_by_id[self.env.pos.get_cashier().id].group_select_customer) {
                        $(".partner-button").prop("disabled", true);
                        $(".partner-button").addClass("sh_disabled");
                    } else {
                        $(".partner-button").prop("disabled", false);
                        $(".partner-button").removeClass("sh_disabled");
                    }
                    if (self.env.pos.db.employee_by_id && self.env.pos.db.employee_by_id[self.env.pos.get_cashier().id] && self.env.pos.db.employee_by_id[self.env.pos.get_cashier().id].group_disable_plus_minus) {
                        $(".numpad-minus").prop("disabled", true);
                        $(".numpad-minus").addClass("sh_disabled");
                    } else {
                        $(".numpad-minus").prop("disabled", false);
                        $(".numpad-minus").removeClass("sh_disabled");
                    }
                }
            }
        };
    Registries.Component.extend(PaymentScreen, SHPaymentScreen);

    const ShCashierName = (CashierName) =>
        class extends CashierName {
            get username() {
                const cashier = this.env.pos.get_cashier();
                var self = this;
                if (this.env.pos.config.module_pos_hr && this.env.pos.config.employee_ids && this.env.pos.config.employee_ids.length > 0 && cashier.id) {
                    if (self.env.pos.db.employee_by_id && self.env.pos.db.employee_by_id[self.env.pos.get_cashier().id] && self.env.pos.db.employee_by_id[self.env.pos.get_cashier().id].group_select_customer) {
                        $(".set-partner").prop("disabled", true);
                        $(".set-partner").addClass("sh_disabled");
                        $(".partner-button").prop("disabled", true);
                        $(".partner-button").addClass("sh_disabled");
                    } else {
                        $(".set-partner").prop("disabled", false);
                        $(".set-partner").removeClass("sh_disabled");
                        $(".partner-button").prop("disabled", false);
                        $(".partner-button").removeClass("sh_disabled");
                    }
                    if (self.env.pos.db.employee_by_id && self.env.pos.db.employee_by_id[self.env.pos.get_cashier().id] && self.env.pos.db.employee_by_id[self.env.pos.get_cashier().id].disable_payment_id) {
                        $(".pay").prop("disabled", true);
                        $(".pay").addClass("sh_disabled");
                    } else {
                        $(".pay").prop("disabled", false);
                        $(".pay").removeClass("sh_disabled");
                    }
                    if (self.env.pos.db.employee_by_id && self.env.pos.db.employee_by_id[self.env.pos.get_cashier().id] && self.env.pos.db.employee_by_id[self.env.pos.get_cashier().id].group_disable_qty) {
                        $($(".mode-button")[0]).prop("disabled", true);
                        $($(".mode-button")[0]).addClass("sh_disabled_qty");
                    } else {
                        $($(".mode-button")[0]).prop("disabled", false);
                        $($(".mode-button")[0]).removeClass("sh_disabled_qty");
                    }
                    if (self.env.pos.db.employee_by_id && self.env.pos.db.employee_by_id[self.env.pos.get_cashier().id] && self.env.pos.db.employee_by_id[self.env.pos.get_cashier().id].group_disable_price) {
                        $($(".mode-button")[2]).prop("disabled", true);
                        $($(".mode-button")[2]).addClass("sh_disabled_qty");
                    } else {
                        $($(".mode-button")[2]).prop("disabled", false);
                        $($(".mode-button")[2]).removeClass("sh_disabled_qty");
                    }
                    if (self.env.pos.db.employee_by_id && self.env.pos.db.employee_by_id[self.env.pos.get_cashier().id] && self.env.pos.db.employee_by_id[self.env.pos.get_cashier().id].group_disable_discount) {
                        $($(".mode-button")[1]).prop("disabled", true);
                        $($(".mode-button")[1]).addClass("sh_disabled_qty");
                    } else {
                        $($(".mode-button")[1]).prop("disabled", false);
                        $($(".mode-button")[1]).removeClass("sh_disabled_qty");
                    }
                    if (self.env.pos.db.employee_by_id && self.env.pos.db.employee_by_id[self.env.pos.get_cashier().id] && self.env.pos.db.employee_by_id[self.env.pos.get_cashier().id].group_disable_plus_minus) {
                        $(".numpad-minus").prop("disabled", true);
                        $(".numpad-minus").addClass("sh_disabled");
                    } else {
                        $(".numpad-minus").prop("disabled", false);
                        $(".numpad-minus").removeClass("sh_disabled");
                    }
                    if (self.env.pos.db.employee_by_id && self.env.pos.db.employee_by_id[self.env.pos.get_cashier().id] && self.env.pos.db.employee_by_id[self.env.pos.get_cashier().id].group_disable_numpad) {
                        $(".number-char").prop("disabled", true);
                        $(".number-char").addClass("sh_disabled");
                    } else {
                        $(".number-char").prop("disabled", false);
                        $(".number-char").removeClass("sh_disabled");
                    }
                    if (self.env.pos.db.employee_by_id && self.env.pos.db.employee_by_id[self.env.pos.get_cashier().id] && self.env.pos.db.employee_by_id[self.env.pos.get_cashier().id].hr_group_disable_remove) {
                        $(".numpad-backspace").prop("disabled", true);
                        $(".numpad-backspace").addClass("sh_disabled")
                    } else {

                        $(".numpad-backspace").prop("disabled", false);
                        $(".numpad-backspace").removeClass("sh_disabled")
                    }
                }
                if (cashier) {
                    return cashier.name;
                } else {
                    return "";
                }

                return username;
            }
        };

    Registries.Component.extend(CashierName, ShCashierName);


    const ShTicketScreen = (TicketScreen) =>
        class extends TicketScreen {
            onMounted() {
                super.onMounted()
                var self = this;
                if (self.env.pos.db.employee_by_id && self.env.pos.db.employee_by_id[self.env.pos.get_cashier().id] && self.env.pos.db.employee_by_id[self.env.pos.get_cashier().id].hr_group_disable_hide_orders) {
                    $('button.highlight').hide()
                    $('.delete-button').hide()
                } else {
                    $('button.highlight').show()
                    $('.delete-button').show()
                }
                if (self.env.pos.db.employee_by_id && self.env.pos.db.employee_by_id[self.env.pos.get_cashier().id] && self.env.pos.db.employee_by_id[self.env.pos.get_cashier().id].hr_group_remove_delete_button) {
                    // $('button.highlight').hide()
                    $('.delete-button').hide()
                } else {
                    // $('button.highlight').show()
                    $('.delete-button').show()
                }
                if (self.env.pos.db.employee_by_id && self.env.pos.db.employee_by_id[self.env.pos.get_cashier().id] && self.env.pos.db.employee_by_id[self.env.pos.get_cashier().id].hr_group_disable_remove) {
                    $(".numpad-backspace").prop("disabled", true);
                    $(".numpad-backspace").addClass("sh_disabled")
                } else {
                    $(".numpad-backspace").prop("disabled", false);
                    $(".numpad-backspace").removeClass("sh_disabled")
                }
            }
        }
    Registries.Component.extend(TicketScreen, ShTicketScreen);

    return {
        NumpadWidget,
        ActionpadWidget,
        TicketScreen,
    };
});
