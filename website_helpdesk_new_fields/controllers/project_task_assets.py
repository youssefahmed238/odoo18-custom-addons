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
