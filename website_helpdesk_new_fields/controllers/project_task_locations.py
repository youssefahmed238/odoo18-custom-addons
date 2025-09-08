from odoo import http
from odoo.http import request


class ProjectTaskLocationsController(http.Controller):

    @http.route(['/project_task_locations/get_locations'], type='json', auth='public', methods=['POST'], csrf=False)
    def get_locations(self):
        locations = request.env['project.task.locations'].search([])
        location_list = [{
            'id': location.id,
            'name': location.name,
        } for location in locations]
        return location_list
