import base64
from collections import OrderedDict
from datetime import datetime
import time
from dateutil.relativedelta import relativedelta
from odoo import fields, http, _
from odoo.http import request
from odoo.addons.portal.controllers import portal
from odoo.addons.portal.controllers.portal import pager as portal_pager
from odoo.exceptions import AccessError, MissingError


class PortalPayslips(portal.CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super()._prepare_portal_layout_values()
        partner_sudo = request.env.user.partner_id
        values.update({'partner': partner_sudo})
        return values

    def _payslip_get_page_view_values(self, payslip, access_token, **kwargs):
        values = {
            'payslip': payslip,
            'page_name': 'payslip',
            'report_type': 'html',
        }
        history = 'my_payslips_history'
        return self._get_page_view_values(payslip, access_token, values, history, False, **kwargs)

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id
        employee_id = request.env['hr.employee'].sudo().search([('work_contact_id', '=', partner.id)]) or False
        Payslips = request.env['hr.payslip']
        if 'payslips_count' in counters:
            if employee_id:
                values['payslips_count'] = Payslips.sudo().search_count([('employee_id', '=', employee_id.id)])
            else:
                values['payslips_count'] = 0
        return values

    def _render_portal_payslips(self, template, page, date_begin, date_end, sortby, filterby, domain, searchbar_filters,
                                default_filter, url, history, page_name, key):
        values = self._prepare_portal_layout_values()
        Payslips = request.env['hr.payslip'].sudo()
        partner = request.env.user.partner_id
        employee_id = request.env['hr.employee'].sudo().search([('work_contact_id', '=', partner.id)])
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'payslip': 'create_date desc, id desc'},
            'name': {'label': _('Name'), 'payslip': 'name asc, id asc'},
        }
        # default sort
        if not sortby:
            sortby = 'date'
        payslip = searchbar_sortings[sortby]['payslip']
        if searchbar_filters:
            # default filter
            if not filterby:
                filterby = default_filter
            domain += searchbar_filters[filterby]['domain']
        if employee_id:
            domain.append(('employee_id', '=', employee_id.id))
            # count for pager
            count = Payslips.search_count(domain)
            # make pager
            pager = portal_pager(
                url=url,
                url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby},
                total=count,
                page=page,
                step=self._items_per_page
            )

            # search the purchase orders to display, according to the pager data
            payslips = Payslips.search(
                domain,
                order=payslip,
                limit=self._items_per_page,
                offset=pager['offset']
            )
            request.session[history] = payslips.ids[:100]

            values.update({
                'date': date_begin,
                key: payslips,
                'page_name': page_name,
                'pager': pager,
                'searchbar_sortings': searchbar_sortings,
                'sortby': sortby,
                'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
                'filterby': filterby,
                'default_url': url,
            })
        return request.render(template, values)

    @http.route(['/my/payslips', '/my/payslips/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_payslips(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None,
                           **kw):
        return self._render_portal_payslips(
            "vit_employee_self_service_portal.portal_my_payslips",
            page, date_begin, date_end, sortby, filterby,
            [],
            {
                'all': {'label': _('All'), 'domain': []},
                'last_month': {'label': _('Last Month'), 'domain': [('date_from', '>=', datetime.strptime(
                    (datetime.today() - relativedelta(months=1)).strftime('%Y-%m-01 %H:%M:%S'),
                    '%Y-%m-01 %H:%M:%S')), ('date_to', '<', time.strftime('%Y-%m-01'))]},
                'current_month': {'label': _('Current Month'), 'domain': [('date_from', '<', datetime.strptime(
                    (datetime.today() + relativedelta(months=1)).strftime('%Y-%m-01 %H:%M:%S'),
                    '%Y-%m-01 %H:%M:%S')), ('date_to', '>=', time.strftime('%Y-%m-01'))]},
                'this_year': {'label': _('This Year'), 'domain': [('date_from', '<=', time.strftime('%Y-12-31')),
                                                                  ('date_to', '>=', time.strftime('%Y-01-01'))]},
                'last_year': {'label': _('Last Year'), 'domain': [
                    ('date_from', '>=', (datetime.today() - relativedelta(years=1)).strftime('%Y-01-01')),
                    ('date_to', '<=', time.strftime('%Y-01-01'))]}
            },
            'all',
            "/my/payslips",
            'my_payslips_history',
            'payslip',
            'payslips'
        )

    @http.route(['/my/payslips/<int:payslip_id>'], type='http', auth="public", website=True)
    def portal_my_payslip_detail(self, payslip_id=None, access_token=None, **kw):
        try:
            payslip_sudo = self._document_check_access('hr.payslip', payslip_id, access_token=access_token)

        except (AccessError, MissingError):
            return request.redirect('/my')

        report_type = kw.get('report_type')
        if report_type in ('html', 'pdf', 'text'):
            return self._show_report(model=payslip_sudo, report_type=report_type,
                                     report_ref='hr_payroll.action_report_payslip', download=kw.get('download'))

        values = self._payslip_get_page_view_values(payslip_sudo, access_token, **kw)
        if payslip_sudo.company_id:
            values['res_company'] = payslip_sudo.company_id
        return request.render("vit_employee_self_service_portal.portal_my_payslip", values)
