from odoo import models, fields, api


class HelpdeskTicketConvertWizard(models.TransientModel):
    _inherit = 'helpdesk.ticket.convert.wizard'

    @api.model
    def _default_project_id(self):
        ticket_id = self.env.context.get('active_id', False)

        if ticket_id:
            ticket = self.env['helpdesk.ticket'].browse(ticket_id)
            if ticket.project_task_id:
                return ticket.project_task_id.id

        return False
