/** @odoo-module **/

import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { TicketScreen } from "@point_of_sale/app/screens/ticket_screen/ticket_screen";
import { CashierName } from "@point_of_sale/app/navbar/cashier_name/cashier_name";
import { patch } from "@web/core/utils/patch";
import { onMounted, onPatched } from "@odoo/owl";

// ------------------- Helpers -------------------

function applyEmployeePermission(buttons, shouldDisable, cssClass) {
    if (!buttons) return;

    buttons.forEach(btn => {
        if (shouldDisable) {
            if (cssClass) {
                btn.disabled = true;
                btn.classList.add(cssClass);
            } else {
                btn.style.display = "none";
            }
        } else {
            if (cssClass) {
                btn.disabled = false;
                btn.classList.remove(cssClass);
            } else {
                btn.style.display = "";
            }
        }
    });
}

function getCurrentEmployee(pos) {
    if (!pos || !pos.db || !pos.db.employee_by_id) return null;
    const cashier_id = pos?.get_cashier?.()?.id;
    if (!cashier_id) return null;
    return pos.db.employee_by_id?.[cashier_id] || null;
}

function getNumpadButtonByValue(value) {
    return Array.from(document.querySelectorAll(".numpad-button")).filter(btn => btn.value === value);
}

function getNumpadButtons(excludeValues = []) {
    return Array.from(document.querySelectorAll(".numpad-button")).filter(btn => !excludeValues.includes(btn.value));
}

// ------------------- Apply all employee permissions -------------------
function applyEmployeeToAll(employee) {
    if (!employee) return;

    const buttonMap = [
        { selector: ".set-partner, .partner-button", field: "group_select_customer", class: "sh_disabled" },
        { selector: ".pay", field: "disable_payment_id", class: "sh_disabled" },
        { selector: ".list-plus-btn", field: "hr_group_disable_hide_orders", class: "sh_disabled" },
        { selector: ".delete-button", field: "hr_group_remove_delete_button" },
        { selector: getNumpadButtonByValue("Qty"), field: "group_disable_qty", class: "sh_disabled_qty" },
        { selector: getNumpadButtonByValue("%"), field: "group_disable_discount", class: "sh_disabled_qty" },
        { selector: getNumpadButtonByValue("Price"), field: "group_disable_price", class: "sh_disabled_qty" },
        { selector: getNumpadButtonByValue("+/-"), field: "group_disable_plus_minus", class: "sh_disabled" },
        { selector: getNumpadButtons(["Qty","%","Price","+/-","⌫"]), field: "group_disable_numpad", class: "sh_disabled" },
        { selector: getNumpadButtonByValue("⌫"), field: "hr_group_disable_remove", class: "sh_disabled" },
    ];

    buttonMap.forEach(item => {
        let buttons = Array.isArray(item.selector) ? item.selector : Array.from(document.querySelectorAll(item.selector));
        applyEmployeePermission(buttons, employee[item.field], item.class);
    });
}

// ------------------- Generic function for Screens -------------------
function updatePermissionsForCurrentScreen(screen) {
    if (!screen || !screen.pos) return;
    const employee = getCurrentEmployee(screen.pos);
    applyEmployeeToAll(employee);
}

// ------------------- ProductScreen -------------------
patch(ProductScreen.prototype, {
    setup() {
        super.setup();
        onMounted(() => updatePermissionsForCurrentScreen(this));
        onPatched(() => updatePermissionsForCurrentScreen(this));
    }
});

// ------------------- PaymentScreen -------------------
patch(PaymentScreen.prototype, {
    setup() {
        super.setup();
        onMounted(() => updatePermissionsForCurrentScreen(this));
        onPatched(() => updatePermissionsForCurrentScreen(this));
    }
});

// ------------------- TicketScreen -------------------
patch(TicketScreen.prototype, {
    setup() {
        super.setup();
        onMounted(() => updatePermissionsForCurrentScreen(this));
        onPatched(() => updatePermissionsForCurrentScreen(this));
    }
});

// ------------------- CashierName -------------------
patch(CashierName.prototype, {
    get username() {
        const cashier = this.pos?.get_cashier?.();
        setTimeout(() => updatePermissionsForCurrentScreen(this), 50);
        return cashier ? cashier.name : "";
    }
});
