/** @odoo-module **/
import { ListController } from "@web/views/list/list_controller";
import { patch } from "@web/core/utils/patch";
import { rpc } from "@web/core/network/rpc";

patch(ListController.prototype, {
    _qrCameraState: {
        stream: null,
        scanning: false,
        scanningLoop: null,
    },

    async onScanAsset(ev) {
        ev.preventDefault();

        if (typeof window.jsQR !== "function") {
            alert("QR library not loaded.");
            return;
        }

        const videoEl = document.getElementById('camera_video');
        const modalEl = document.getElementById('qrCameraModal');
        const closeBtn = document.getElementById('close_camera_btn');

        const state = this._qrCameraState;

        // Stop any previous camera & loop
        if (state.scanningLoop) {
            cancelAnimationFrame(state.scanningLoop);
            state.scanningLoop = null;
        }
        if (state.stream) {
            state.stream.getTracks().forEach(track => track.stop());
            state.stream = null;
        }
        videoEl.srcObject = null;

        state.scanning = false; // reset for new scan

        // Show modal
        modalEl.style.display = 'flex';

        // Remove old click listeners
        closeBtn.replaceWith(closeBtn.cloneNode(true));
        const newCloseBtn = document.getElementById('close_camera_btn');
        newCloseBtn.addEventListener('click', () => {
            modalEl.style.display = 'none';
            if (state.stream) {
                state.stream.getTracks().forEach(track => track.stop());
                state.stream = null;
            }
            if (state.scanningLoop) {
                cancelAnimationFrame(state.scanningLoop);
                state.scanningLoop = null;
            }
            state.scanning = false;
        });

        // Click outside modal to close
        modalEl.addEventListener('click', (e) => {
            if (e.target === modalEl) {
                newCloseBtn.click();
            }
        }, { once: true });

        // Start camera
        try {
            state.stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } });
            videoEl.srcObject = state.stream;
            await videoEl.play();
        } catch (error) {
            alert("Unable to access camera: " + error.message);
            newCloseBtn.click();
            return;
        }

        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d', { willReadFrequently: true });

        // Scan loop
        const scanLoop = async () => {
            if (videoEl.readyState === videoEl.HAVE_ENOUGH_DATA) {
                canvas.width = videoEl.videoWidth;
                canvas.height = videoEl.videoHeight;
                ctx.drawImage(videoEl, 0, 0, canvas.width, canvas.height);
                const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
                const code = window.jsQR(imageData.data, imageData.width, imageData.height);

                if (code && code.data && !state.scanning) {
                    state.scanning = true;
                    const qrData = this._parseQRData(code.data);
                    if (!qrData['ASSET']) {
                        alert("No ASSET code found in QR data.");
                        newCloseBtn.click();
                        return;
                    }

                    const asset = await this._getAsset(qrData['ASSET']);

                    // Hide modal and stop camera
                    newCloseBtn.click();

                    const searchInput = document.querySelector('.o_searchview_input');
                    if (searchInput) {
                        searchInput.value = asset['name'] || '';
                        searchInput.dispatchEvent(new Event('input', { bubbles: true }));
                        searchInput.dispatchEvent(new KeyboardEvent('keydown', { key: "Enter" }));
                    }

                    return;
                }
            }
            state.scanningLoop = requestAnimationFrame(scanLoop);
        };

        state.scanningLoop = requestAnimationFrame(scanLoop);
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

    async _getAsset(assetId) {
        try {
            const asset = await rpc('/project_task_assets/getAsset', { asset_id: assetId });

            if (asset) {
                return asset;
            } else {
                alert("Asset not found.");
                return null;
            }
        } catch (error) {
            alert("Error fetching asset: " + error.message);
            return null;
        }
    },
});
