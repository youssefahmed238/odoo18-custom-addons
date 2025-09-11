/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { rpc } from "@web/core/network/rpc";

publicWidget.registry.WebsiteHelpdeskNewFields = publicWidget.Widget.extend({
    selector: '#helpdesk_ticket_form',
    events: {
        'change #helpdesk_project': '_onProjectChange',
    },

    start: async function () {
        this.projectSelect = $('#helpdesk_project');
        this.assetSelect = $('#helpdesk_asset');
        this.locationSelect = $('#helpdesk_location');

        this.projects = [];
        this.assets = [];
        this.locations = [];

        await this._getProjects();

        await this._getAssets(this.projectSelect.val());
        await this._getLocations(this.projectSelect.val());
    },

    _getProjects: async function () {
        try {
            this.projects = await rpc('/project_task_projects/get_projects', {});
            this.projectSelect.empty();

            for (const project of this.projects) {
                this.projectSelect.append(new Option(project.name, project.id));
            }

        } catch (error) {
            console.error("Error fetching projects:", error);
            this.projectSelect.empty().append(new Option('Error loading projects', ''));
        }
    },

    _getAssets: async function (projectId) {
        try {
            this.assets = await rpc('/project_task_assets/get_assets', { project_id: projectId });
            this.assetSelect.empty();

            for (const asset of this.assets) {
                this.assetSelect.append(new Option(asset.name, asset.id));
            }

        } catch (error) {
            console.error("Error fetching assets:", error);
            this.assetSelect.empty().append(new Option('Error loading assets', ''));
        }
    },

    _getLocations: async function (projectId) {
        try {
            this.locations = await rpc('/project_task_locations/get_locations', { project_id: projectId });
            this.locationSelect.empty();

            for (const location of this.locations) {
                this.locationSelect.append(new Option(location.name, location.id));
            }

        } catch (error) {
            console.error("Error fetching locations:", error);
            this.locationSelect.empty().append(new Option('Error loading locations', ''));
        }
    },

    _onProjectChange: async function () {
        const selectedProjectId = this.projectSelect.val();

        await this._getAssets(selectedProjectId);
        await this._getLocations(selectedProjectId);
    },
});