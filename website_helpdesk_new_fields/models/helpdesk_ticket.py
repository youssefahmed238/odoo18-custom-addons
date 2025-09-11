from odoo import models, fields


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    project_task_id = fields.Many2one('project.project', string='Project')
    asset_id = fields.Many2one('project.task.assets', string='Asset')
    location_id = fields.Many2one('project.task.locations', string='Location')
