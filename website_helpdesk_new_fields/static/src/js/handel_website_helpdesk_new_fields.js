/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { rpc } from "@web/core/network/rpc";

publicWidget.registry.WebsiteHelpdeskNewFields = publicWidget.Widget.extend({
    selector: '#helpdesk_ticket_form',
    events: {
        'click #scan_qr_btn': '_onScanQRClick',
        'change select[name="project_task_id"]': '_onProjectChange',
        'change select[name="location_id"]': '_onLocationChange',
    },

    start: async function () {
        this.projectSelect = this.$el.find('select[name="project_task_id"]');
        this.assetSelect = this.$el.find('select[name="asset_id"]');
        this.locationSelect = this.$el.find('select[name="location_id"]');
        this.qrResult = this.$el.find('#qr_result');

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

    // -------------------- QR SCAN HANDLER --------------------
    _onScanQRClick: async function (ev) {
        ev.preventDefault();

        if (typeof window.jsQR !== "function") {
            alert("QR library not loaded. Please verify jsQR asset inclusion.");
            return;
        }

        const videoEl = document.getElementById('camera_video');
        const modalEl = document.getElementById('qrCameraModal');
        const closeBtn = document.getElementById('close_camera_btn');
        let stream;

        $('#qrCameraModal').off('shown.bs.modal');
        $('#qrCameraModal').off('hidden.bs.modal');

        // Start camera when modal opens
        $('#qrCameraModal').on('shown.bs.modal', async () => {
            try {
                stream = await navigator.mediaDevices.getUserMedia({video: {facingMode: "environment"}});
                videoEl.srcObject = stream;
                await videoEl.play();

                const canvas = document.createElement('canvas');
                const ctx = canvas.getContext('2d');

                const scan = () => {
                    if (videoEl.readyState === videoEl.HAVE_ENOUGH_DATA) {
                        canvas.width = videoEl.videoWidth;
                        canvas.height = videoEl.videoHeight;
                        ctx.drawImage(videoEl, 0, 0, canvas.width, canvas.height);
                        const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
                        const code = window.jsQR(imageData.data, imageData.width, imageData.height);
                        if (code) {
                            this.qrResult.val(code.data);
                            const assetCode = this._parseQRData(code.data)['ASSET']
                            if (assetCode)
                                this._getAsset();
                            else
                                alert("No ASSET code found in QR data.");
                            stopCamera();
                            $('#qrCameraModal').modal('hide');
                            return;
                        }
                    }
                    requestAnimationFrame(scan);
                };
                scan();

            } catch (error) {
                alert("Unable to access camera: " + error.message);
                $('#qrCameraModal').modal('hide');
            }
        });

        // Stop camera when modal closes
        const stopCamera = () => {
            if (stream) {
                stream.getTracks().forEach(t => t.stop());
            }
            videoEl.srcObject = null;
        };

        $('#qrCameraModal').on('hidden.bs.modal', stopCamera);
    },

    _parseQRData(qrData) {
        const parts = qrData.split(/\s*\|\|\s*/);
        const data = {};
        let currentKey = null;

        for (const part of parts) {
            if (!part) continue;
            if (part.includes(':')) {
                const [key, ...valueParts] = part.split(':');
                currentKey = key.trim();
                data[currentKey] = valueParts.join(':').trim();
            } else if (currentKey) {
                data[currentKey] += ' ' + part.trim();
            }
        }
        return data;
    },

    // -------------------- EXISTING LOGIC --------------------
    async _getProjects() {
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

    async _getLocations(projectId) {
        try {
            this.locations = await rpc('/project_task_locations/get_locations', { project_id: projectId });

            this.locationSelect.empty().append(new Option('', ''));
            this.removeLocationEmptyOption = true;

            for (const location of this.locations) {
                this.locationSelect.append(new Option(location.name, location.id));
            }
        } catch (error) {
            console.error("Error fetching locations:", error);
            this.locationSelect.empty().append(new Option('Error loading locations', ''));
        }
    },

    async _getAssets(projectId, locationId) {
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

    async _getAsset(assetCode) {
        try{
            const asset = await rpc('/project_task_assets/get_asset', { asset_code: assetCode });

            if (this.projectSelect.val() !== String(asset.project_id)) {
                this.projectSelect.val(String(asset.project_id));
                await this._onProjectChange();
            }

            if (this.locationSelect.val() !== String(asset.location_id)) {
                this.locationSelect.val(String(asset.location_id));
                this._onLocationChange();
            }

            this.assetSelect.val(String(asset.id));

        } catch (error) {
            console.error("Error fetching asset by code:", error);
            this.assetSelect.empty().append(new Option('Error loading asset', ''));
        }
    },

    async _onProjectChange() {
        const selectedProjectId = this.projectSelect.val();

        this.assetField.hide();

        this.locationSelect.empty();
        await this._getLocations(selectedProjectId);
    },

    _onLocationChange() {
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
