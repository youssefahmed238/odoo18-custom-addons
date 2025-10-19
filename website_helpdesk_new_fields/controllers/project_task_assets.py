from odoo import http
from odoo.http import request


class ProjectTaskAssetsController(http.Controller):

    @http.route(['/project_task_assets/get_assets'], type='json', auth='public', methods=['POST'], csrf=False)
    def get_assets(self, project_id, location_id):
        assets = request.env['project.task.assets'].sudo().search(
            ['&', ('project_id', '=', int(project_id)), ('location_id', '=', int(location_id))])

        asset_list = [{
            'id': asset.id,
            'name': asset.name
        } for asset in assets]

        return asset_list

    @http.route(['/project_task_assets/get_asset'], type='json', auth='public', methods=['POST'], csrf=False)
    def get_asset(self, asset_code):
        asset = request.env['project.task.assets'].sudo().search([('asset_code', '=', asset_code)], limit=1)

        if asset:
            return {
                'id': asset.id,
                'name': asset.name,
                'asset_code': asset.asset_code,
                'location_id': asset.location_id.id,
                'project_id': asset.project_id.id,
            }
        else:
            return {}
