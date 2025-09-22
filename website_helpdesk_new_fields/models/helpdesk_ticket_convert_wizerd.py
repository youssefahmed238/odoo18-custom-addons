from odoo import models, fields, api, _

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

    def action_convert(self):
        """ Override to skip deactivating the helpdesk ticket after conversion. """
        
        tickets_to_convert = self._get_tickets_to_convert()

        created_tasks = self.env['project.task'].with_context(mail_create_nolog=True).create(
            [self._get_task_values(ticket) for ticket in tickets_to_convert]
        )

        for ticket, task in zip(tickets_to_convert, created_tasks):
            # Skip the line that sets ticket.active = False
            # ticket.active = False

            ticket_sudo, task_sudo = ticket.sudo(), task.sudo()
            ticket_sudo.message_post(body=_("Ticket converted into task %s", task_sudo._get_html_link()))
            task_sudo.message_post_with_source(
                'mail.message_origin_link',
                render_values={'self': task_sudo, 'origin': ticket_sudo},
                subtype_xmlid='mail.mt_note',
            )

        if len(created_tasks) == 1:
            return {
                'view_mode': 'form',
                'res_model': 'project.task',
                'res_id': created_tasks[0].id,
                'views': [(self.env.ref('project.view_task_form2').id, 'form')],
                'type': 'ir.actions.act_window',
            }
        return {
            'name': _('Converted Tasks'),
            'view_mode': 'list,form',
            'res_model': 'project.task',
            'views': [(self.env.ref('project.view_task_tree2').id, 'list'),
                      (self.env.ref('project.view_task_form2').id, 'form')],
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', created_tasks.ids)],
        }