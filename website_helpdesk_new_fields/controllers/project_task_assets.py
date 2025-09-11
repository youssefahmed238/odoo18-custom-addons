from odoo import http
from odoo.http import request


class ProjectTaskAssetsController(http.Controller):

    @http.route(['/project_task_assets/get_assets'], type='json', auth='public', methods=['POST'], csrf=False)
    def get_assets(self, project_id):

        assets = request.env['project.task.assets'].sudo().search([('project_id', '=', int(project_id))])

        asset_list = [{
            'id': asset.id,
            'name': asset.name,
            'location_id': asset.location_id.id if asset.location_id else False,
        } for asset in assets]

        return asset_list
