/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { rpc } from "@web/core/network/rpc";

publicWidget.registry.WebsiteHelpdeskNewFields = publicWidget.Widget.extend({
    selector: '#helpdesk_ticket_form',
    events: {
        'click #helpdesk_asset': '_onAssetClick',
    },

    start: async function () {
        this.assetSelect = $('#helpdesk_asset');
        this.locationSelect = $('#helpdesk_location');

        this.assets = [];
        this.locations = [];

        await this._getAssets();
        await this._getLocations();

        this._setLocationForAsset(this.assetSelect.val());
    },

    _getAssets: async function () {
        try {
            this.assets = await rpc('/project_task_assets/get_assets', {});
            this.assetSelect.empty();

            for (const asset of this.assets) {
                this.assetSelect.append(new Option(asset.name, asset.id));
            }

        } catch (error) {
            console.error("Error fetching assets:", error);
            this.assetSelect.empty().append(new Option('Error loading assets', ''));
        }
    },

    _getLocations: async function () {
        try {
            this.locations = await rpc('/project_task_locations/get_locations', {});
            this.locationSelect.empty();

            for (const location of this.locations) {
                this.locationSelect.append(new Option(location.name, location.id));
            }

        } catch (error) {
            console.error("Error fetching locations:", error);
            this.locationSelect.empty().append(new Option('Error loading locations', ''));
        }
    },

    _onAssetClick: function () {
        const selectedAssetId = this.assetSelect.val();
        this._setLocationForAsset(selectedAssetId);
    },

    _setLocationForAsset: function (assetId) {
        const selectedAsset = this.assets.find(asset => asset.id == assetId);
        if (selectedAsset && selectedAsset.location_id) {
            this.locationSelect.val(selectedAsset.location_id);
        }
    },
});