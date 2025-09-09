from odoo import models, fields


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    asset_id = fields.Many2one('project.task.assets', string='Asset')
    location_id = fields.Many2one('project.task.locations', string='Location')
