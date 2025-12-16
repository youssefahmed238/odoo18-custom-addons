from datetime import datetime
from odoo import http
from odoo.http import request
import io
import xlsxwriter

class XlsxPartnerBalanceReport(http.Controller):


    @http.route('/partner/balance/excel', type='http', auth='user')
    def download_partner_balance_excel_report(self, **kwargs):

        start_date = kwargs.get('start_date') or '2024-01-01'
        end_date = kwargs.get('end_date') or datetime.today().strftime('%Y-%m-%d')
        report_type = kwargs.get('type') or 'All'
        partner_id = kwargs.get('partner_ids')

        # Get selected partners
        if partner_id:
            try:
                partner_ids = [int(partner_id)]
            except ValueError:
                return request.not_found()
        else:
            partner_ids = request.env['res.partner'].search([]).ids

        partners = [{'id': pid} for pid in partner_ids]

        data = {
            'ids': [],
            'model': 'res.partner',
            'form': {
                'start_date': start_date,
                'end_date': end_date,
                'type': report_type,
                'partner': partners
            }
        }

        report_model = request.env['report.ag_partner_balance_report.partner_balance_report_view']
        report_data = report_model._get_report_values([], data)['docs']

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Partner Balance')

        # Formats
        title_format = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter', 'border': 1, 'bg_color': '#D9E1F2'})
        header_format = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter', 'border': 1})
        cell_format = workbook.add_format({'border': 1, 'align': 'center'})
        float_format = workbook.add_format({'border': 1, 'align': 'center', 'num_format': '#,##0.00'})

        # Column widths
        worksheet.set_column(0, 0, 25)
        worksheet.set_column(1, 13, 15)

        # Report meta info
        worksheet.write('A1', 'Start Date', header_format)
        worksheet.write('B1', start_date, cell_format)

        worksheet.write('A2', 'End Date', header_format)
        worksheet.write('B2', end_date, cell_format)

        worksheet.write('A3', 'Type', header_format)
        worksheet.write('B3', report_type, cell_format)

        # Header rows
        worksheet.merge_range(3, 0, 4, 0, 'Partner Name', title_format)
        worksheet.merge_range(3, 1, 3, 4, 'Initial Balance', title_format)
        worksheet.merge_range(3, 5, 3, 8, 'Transaction', title_format)
        worksheet.merge_range(3, 9, 3, 12, 'Ending Balance', title_format)

        sub_headers = ['Debit', 'Credit', 'Balance', 'Foreign Balance']
        for i, header in enumerate(sub_headers):
            worksheet.write(4, 1 + i, header, header_format)
            worksheet.write(4, 5 + i, header, header_format)
            worksheet.write(4, 9 + i, header, header_format)

        # Fill data
        for row_num, line in enumerate(report_data, start=5):
            worksheet.write(row_num, 0, line['name'], cell_format)
            worksheet.write(row_num, 1, line['init_dr'], float_format)
            worksheet.write(row_num, 2, line['init_cr'], float_format)
            worksheet.write(row_num, 3, line['init_bal'], float_format)
            worksheet.write(row_num, 4, line['init_for'], float_format)
            worksheet.write(row_num, 5, line['trn_dr'], float_format)
            worksheet.write(row_num, 6, line['trn_cr'], float_format)
            worksheet.write(row_num, 7, line['trn_bal'], float_format)
            worksheet.write(row_num, 8, line['trn_for'], float_format)
            worksheet.write(row_num, 9, line['Ending_dr'], float_format)
            worksheet.write(row_num, 10, line['Ending_cr'], float_format)
            worksheet.write(row_num, 11, line['Ending_bal'], float_format)
            worksheet.write(row_num, 12, line['ending_for'], float_format)

        workbook.close()
        output.seek(0)

        filename = 'Partner_Balance_Report.xlsx'
        return request.make_response(
            output.read(),
            headers=[
                ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                ('Content-Disposition', f'attachment; filename="{filename}"'),
            ]
        )
