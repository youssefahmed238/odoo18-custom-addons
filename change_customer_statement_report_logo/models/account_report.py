from odoo import models, _


class AccountReport(models.Model):
    _inherit = 'account.report'

    def _init_options_buttons(self, options, previous_options):
        super(AccountReport, self)._init_options_buttons(options, previous_options)

        if self.custom_handler_model_name == 'account.partner.ledger.report.handler':
            options['buttons'].insert(0, {
                'name': _('Global Gate PDF'),
                'sequence': 5,
                'action': 'export_file',
                'action_param': 'export_to_pdf_global_gate',
                'file_export_type': _('PDF'),
                'branch_allowed': True,
                'always_show': True,
            })

    def export_to_pdf_global_gate(self, options):
        return self.with_context(global_gate_pdf=True).export_to_pdf(options)
