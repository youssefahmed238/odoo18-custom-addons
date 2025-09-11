from odoo import http
from odoo.http import request


class ProjectTaskProjectsController(http.Controller):

    @http.route(['/project_task_projects/get_projects'], type='json', auth='public', methods=['POST'], csrf=False)
    def get_projects(self):
        user_partner = request.env.user.partner_id

        projects = request.env['project.project'].sudo().search([
            '|',
            ('collaborator_ids.partner_id', '=', user_partner.id),
            ('message_partner_ids', 'in', [user_partner.id]),
        ])

        project_list = [{
            'id': project.id,
            'name': project.name,
        } for project in projects]

        return project_list
