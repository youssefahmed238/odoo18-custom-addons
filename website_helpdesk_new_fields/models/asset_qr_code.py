from odoo import models, fields, api
import base64
from io import BytesIO
import qrcode

class ProjectTaskAssets(models.Model):
    _inherit = 'project.task.assets'

    asset_qr_image = fields.Binary("Asset QR", compute="_compute_asset_qr_image", store=False)

    @api.depends('asset_code', 'location_id', 'project_id')
    def _compute_asset_qr_image(self):
        for rec in self:
            if rec.asset_code or rec.location_id or rec.project_id:
                # Build the data string for the QR
                qr_data = []
                if rec.asset_code:
                    qr_data.append(f"ASSET:{rec.asset_code}")
                if rec.location_id:
                    qr_data.append(f"LOCATION:{rec.location_id.display_name}")
                if rec.project_id:
                    qr_data.append(f"PROJECT:{rec.project_id.display_name}")

                # Join all parts with a delimiter (//)
                qr_text = " || ".join(qr_data)

                # Generate the QR code
                qr = qrcode.QRCode(version=1, box_size=10, border=2)
                qr.add_data(qr_text)
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")

                # Convert image to base64
                buffer = BytesIO()
                img.save(buffer, format="PNG")
                qr_image = base64.b64encode(buffer.getvalue())
                rec.asset_qr_image = qr_image
            else:
                rec.asset_qr_image = False
