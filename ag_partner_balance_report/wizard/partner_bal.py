# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.translate import _


class PartnerBalanceReport(models.TransientModel):
    _name = 'partner.balance.report'

    start_date = fields.Date('Start Date',required=True)
    end_date = fields.Date('End Date',required=True)
    type = fields.Selection([
        ('Payables Accounts', 'Payables Accounts'),
        ('Receivables Accounts', 'Receivables Accounts'),
        ('Payables and Receivables Accounts', 'Payables and Receivables Accounts'),
        ], string='Type',required=True, default='Payables and Receivables Accounts')
    partner_ids = fields.Many2many('res.partner', string='Partners')

    
    def get_report(self):
        pro = []
        partner_ids = self.partner_ids

        if not partner_ids:
            partner_ids = self.env['res.partner'].search([])

        for l in partner_ids:
            proj = {
                'id':l.id,
                'name':l.name,
            }
            pro.append(proj)
        data = {
            'model': self._name,
            'ids': self.ids,
            'form': {
                'start_date': self.start_date,'end_date': self.end_date,'type': self.type, 'partner': pro,
            },
        }
        # if data['form']['patient_id']:
        #     selected_patient = data['form']['patient_id'][0]
        #     appointments = self.env['hospital.appointment'].search([('patient_id', '=', selected_patient)])
        # else:
        #     appointments = self.env['hospital.appointment'].search([])
        # appointment_list = []
        # for app in appointments:
        #     vals = {
        #         'name': app.name,
        #         'notes': app.notes,
        #         'appointment_date': app.appointment_date
        #     }
        #     appointment_list.append(vals)
        # # print("appointments", appointments)
        # data['appointments'] = appointment_list
        # # print("Data", data)
        return self.env.ref('ag_partner_balance_report.partner_balance_report').report_action(self, data=data)

    def get_excel_report(self):
        url = f'/partner/balance/excel?start_date={self.start_date}&end_date={self.end_date}&type={self.type}'

        partner_ids = self.partner_ids

        if not partner_ids:
            partner_ids = self.env['res.partner'].search([])

        if partner_ids:
            ids = ','.join(str(p.id) for p in partner_ids)
            url += f'&partner_ids={ids}'
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }

    # @api.multi
    # def next_stage_6(self):
    #     pur = self.env['crm.lead'].browse(self.env.context.get('active_ids'))
    #     pur.write({'stage_id': 8})
