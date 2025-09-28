/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { numberBufferService } from "@point_of_sale/app/utils/number_buffer_service";

patch(numberBufferService, {
    start(env, deps) {
        const numberBuffer = super.start(env, deps);

        // Patch the _handleInput method to disable Delete and minus keys
        patch(numberBuffer, {
            _handleInput(key) {
                if (key === "Delete" || key === "-") {
                    // Do nothing, effectively disabling these keys
                    return;
                }
                return super._handleInput(key);
            },
        });

        return numberBuffer;
    },
});
