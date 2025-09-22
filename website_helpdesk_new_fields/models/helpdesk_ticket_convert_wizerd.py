from odoo import models, fields, api


class HelpdeskTicketConvertWizard(models.TransientModel):
    _inherit = 'helpdesk.ticket.convert.wizard'

    @api.model
    def _default_project_id(self):
        """ Set the default project_id based on the project_task_id field of the active helpdesk ticket. """

        ticket_id = self.env.context.get('active_id', False)

        if ticket_id:
            ticket = self.env['helpdesk.ticket'].browse(ticket_id)
            if ticket.project_task_id:
                return ticket.project_task_id.id

        return False

    @api.model
    def _get_task_values(self, ticket):
        """ Override to add asset_id and location_id fields to the task values. """

        task_values = super()._get_task_values(ticket)

        task_values.update({
            'asset_id': ticket.asset_id.id,
            'Location_id': ticket.location_id.id,
        })

        return task_values
