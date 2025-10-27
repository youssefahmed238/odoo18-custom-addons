from odoo import http
from odoo.http import request


class AssetSearchWithQRController(http.Controller):

    @http.route('/project_task_assets/getAsset', type='json', auth='public', methods=['POST'], csrf=False)
    def get_asset(self, asset_id):
        asset = request.env['project.task.assets'].sudo().search([('id', '=', int(asset_id))], limit=1)

        if asset:
            return {
                'id': asset.id,
                'asset_code': asset.asset_code,
                'name': asset.name,
                'location_id': asset.location_id.id,
                'project_id': asset.project_id.id,
            }
        else:
            return {'error': 'Asset not found'}
