/** @odoo-module **/

import {_t} from "@web/core/l10n/translation";
import {
    StateSelectionField,
    stateSelectionField,
} from "@web/views/fields/state_selection/state_selection_field";
import {useCommand} from "@web/core/commands/command_hook";
import {formatSelection} from "@web/views/fields/formatters";
import {registry} from "@web/core/registry";
import {useState} from "@odoo/owl";

export class CustomStageState extends StateSelectionField {
    static template = "stage_state.CustomStageState";

    static props = {
        ...stateSelectionField.component.props,
        isToggleMode: {type: Boolean, optional: true},
        viewType: {type: String, optional: true},
        iconsMap: {type: Object, optional: true},
        colorIconsMap: {type: Object, optional: true},
        colorButtonMap: {type: Object, optional: true},
        toggleStates: {type: Array, optional: true},
    };

    setup() {
        this.state = useState({
            isStateButtonHighlighted: false,
        });

        // Set up icons and colors from props
        this.icons = this.props.iconsMap || {};
        this.colorIcons = this.props.colorIconsMap || {};
        this.colorButton = this.props.colorButtonMap || {};

        // Setup command palette for form view
        if (this.props.viewType !== 'form') {
            super.setup();
        } else {
            const commandName = _t("Set state as...");
            useCommand(
                commandName,
                () => {
                    return {
                        placeholder: commandName,
                        providers: [
                            {
                                provide: () =>
                                    this.options.map(subarr => ({
                                        name: subarr[1],
                                        action: () => {
                                            this.updateRecord(subarr[0]);
                                        },
                                    })),
                            },
                        ],
                    };
                },
                {
                    category: "smart_action",
                    hotkey: "alt+s",
                    isAvailable: () => !this.props.readonly && !this.props.isDisabled,
                }
            );
        }
    }

    get availableOptions() {
        // Include current option in dropdown
        return this.options;
    }

    get label() {
        return formatSelection(this.currentValue, {
            selection: this.options,
        });
    }

    stateIcon(value) {
        return this.icons[value] || "";
    }

    statusColor(value) {
        return this.colorIcons[value] || "";
    }

    get isToggleMode() {
        return this.props.isToggleMode;
    }

    isView(viewNames) {
        return viewNames.includes(this.props.viewType);
    }

    async toggleState() {
        if (!this.props.toggleStates || this.props.toggleStates.length < 2) return;
        const toggleVal = this.currentValue === this.props.toggleStates[1]
            ? this.props.toggleStates[0]
            : this.props.toggleStates[1];
        await this.updateRecord(toggleVal);
    }

    getDropdownPosition() {
        if (this.isView(['activity', 'kanban', 'list', 'calendar']) || this.env.isSmall) {
            return '';
        }
        return 'bottom-end';
    }

    getTogglerClass(currentValue) {
        if (this.isView(['activity', 'kanban', 'list', 'calendar']) || this.env.isSmall) {
            return 'btn btn-link d-flex p-0';
        }
        return 'o_state_button btn rounded-pill ' + (this.colorButton[currentValue] || 'btn-outline-secondary');
    }

    async updateRecord(value) {
        const result = await super.updateRecord(value);
        this.state.isStateButtonHighlighted = false;
        if (result) {
            return result;
        }
    }

    onMouseEnterStateButton(ev) {
        if (!this.env.isSmall) {
            this.state.isStateButtonHighlighted = true;
        }
    }

    onMouseLeaveStateButton(ev) {
        this.state.isStateButtonHighlighted = false;
    }
}

export const customStageState = {
    ...stateSelectionField,
    component: CustomStageState,
    supportedOptions: [
        ...stateSelectionField.supportedOptions,
        {label: _t("Is toggle mode"), name: "is_toggle_mode", type: "boolean"},
        {label: _t("Icons map"), name: "icons_map", type: "object"},
        {label: _t("Color icons map"), name: "color_icons_map", type: "object"},
        {label: _t("Color button map"), name: "color_button_map", type: "object"},
        {label: _t("Toggle states"), name: "toggle_states", type: "array"},
    ],
    extractProps({options, viewType}) {
        const props = stateSelectionField.extractProps(...arguments);
        props.isToggleMode = Boolean(options.is_toggle_mode);
        props.viewType = viewType;
        props.iconsMap = options.icons_map || {};
        props.colorIconsMap = options.color_icons_map || {};
        props.colorButtonMap = options.color_button_map || {};
        props.toggleStates = options.toggle_states || [];
        return props;
    },
};

registry.category("fields").add("custom_stage_state", customStageState);