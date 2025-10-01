/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { rpc } from "@web/core/network/rpc";

publicWidget.registry.WebsiteHelpdeskNewFields = publicWidget.Widget.extend({
    selector: '#helpdesk_ticket_form',
    events: {
        'change select[name="project_task_id"]': '_onProjectChange',
        'change select[name="location_id"]': '_onLocationChange',
    },

    start: async function () {
        this.projectSelect = this.$el.find('select[name="project_task_id"]');
        this.assetSelect = this.$el.find('select[name="asset_id"]');
        this.locationSelect = this.$el.find('select[name="location_id"]');

        this.projectSelect.empty();
        this.locationSelect.empty();
        this.assetSelect.empty();

        this.assetField = this.assetSelect.closest('.s_website_form_field');

        this.projects = [];
        this.assets = [];
        this.locations = [];

        this.removeLocationEmptyOption = false;

        await this._getProjects();

        const initialProjectId = this.projectSelect.val();
        if (initialProjectId) {
            await this._getLocations(initialProjectId);
        }
    },

    _getProjects: async function () {
        try {
            this.projects = await rpc('/project_task_projects/get_projects', {});

            for (const project of this.projects) {
                this.projectSelect.append(new Option(project.name, project.id));
            }

        } catch (error) {
            console.error("Error fetching projects:", error);
            this.projectSelect.empty().append(new Option('Error loading projects', ''));
        }
    },

    _getLocations: async function (projectId) {
        try {
            this.locations = await rpc('/project_task_locations/get_locations', { project_id: projectId });

            this.locationSelect.append(new Option('', ''));
            this.removeLocationEmptyOption = true;

            for (const location of this.locations) {
                this.locationSelect.append(new Option(location.name, location.id));
            }

        } catch (error) {
            console.error("Error fetching locations:", error);
            this.locationSelect.empty().append(new Option('Error loading locations', ''));
        }
    },

    _getAssets: async function (projectId, locationId) {
        try {
            this.assets = await rpc('/project_task_assets/get_assets', { project_id: projectId, location_id: locationId });

            for (const asset of this.assets) {
                this.assetSelect.append(new Option(asset.name, asset.id));
            }

        } catch (error) {
            console.error("Error fetching assets:", error);
            this.assetSelect.empty().append(new Option('Error loading assets', ''));
        }
    },

    _onProjectChange: async function () {
        const selectedProjectId = this.projectSelect.val();

        this.assetField.hide();

        this.locationSelect.empty();
        await this._getLocations(selectedProjectId);
    },

    _onLocationChange: function () {
        const selectedLocationId = this.locationSelect.val();

        if (this.removeLocationEmptyOption) {
            this.locationSelect.find('option[value=""]').remove();
            this.removeLocationEmptyOption = false;
        }

        this.assetSelect.empty();
        this._getAssets(this.projectSelect.val(), selectedLocationId);

        if (selectedLocationId) {
            this.assetField.show();
        } else {
            this.assetField.hide();
        }
    },
});