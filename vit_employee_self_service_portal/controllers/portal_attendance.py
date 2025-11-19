import base64
from collections import OrderedDict
from datetime import datetime
import time
from dateutil.relativedelta import relativedelta
from odoo import fields, http, _
from odoo.http import request
from odoo.addons.portal.controllers import portal
from odoo.addons.portal.controllers.portal import pager as portal_pager


class PortalAttendance(portal.CustomerPortal):

    def _render_portal_attendances(self, template, page, date_begin, date_end, sortby, filterby, domain,
                                   searchbar_filters, default_filter, url, history, page_name, key):
        values = self._prepare_portal_layout_values()
        Attendances = request.env['hr.attendance'].sudo()
        partner = request.env.user.partner_id
        employee_id = request.env['hr.employee'].sudo().search([('work_contact_id', '=', partner.id)])
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        searchbar_sortings = {
            'check_in': {'label': _('Check In'), 'attendance': 'check_in asc'},
            'check_out': {'label': _('Check Out'), 'attendance': 'check_out desc'},
            'highest_work_hours': {'label': _('Highest Working Hours'), 'attendance': 'worked_hours desc,id desc'}
        }
        # default sort
        if not sortby:
            sortby = 'check_in'
        attendance = searchbar_sortings[sortby]['attendance']
        if searchbar_filters:
            # default filter
            if not filterby:
                filterby = default_filter
            domain += searchbar_filters[filterby]['domain']
        if employee_id:
            domain.append(('employee_id', '=', employee_id.id))
            # count for pager
            count = Attendances.search_count(domain)
            # make pager
            pager = portal_pager(
                url=url,
                url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby},
                total=count,
                page=page,
                step=self._items_per_page
            )

            attendances = Attendances.search(
                domain,
                order=attendance,
                limit=self._items_per_page,
                offset=pager['offset']
            )
            request.session[history] = attendances.ids[:100]
            current_year = datetime.now().year
            values.update({
                'date': date_begin,
                key: attendances,
                'page_name': page_name,
                'pager': pager,
                'searchbar_sortings': searchbar_sortings,
                'sortby': sortby,
                'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
                'filterby': filterby,
                'default_url': url,
                'current_year': current_year,
            })
        return request.render(template, values)

    @http.route(['/my/attendance', '/my/attendance/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_attendance(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None,
                             **kw):
        return self._render_portal_attendances(
            "vit_employee_self_service_portal.portal_my_attendance",
            page, date_begin, date_end, sortby, filterby,
            [],
            {
                'all': {'label': _('All'), 'domain': []},
                'last_month': {'label': _('Last Month'), 'domain': [('check_in', '>=', datetime.strptime(
                    (datetime.today() - relativedelta(months=1)).strftime('%Y-%m-01 %H:%M:%S'),
                    '%Y-%m-01 %H:%M:%S')), ('check_in', '<', time.strftime('%Y-%m-01'))]},
                'last_week': {'label': _('Last Week'), 'domain': [('check_in', '>=', datetime.strptime((
                        datetime.today() + relativedelta(weeks=2, days=1, weekday=0)).strftime(
                    '%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')), ('check_in', '<=', datetime.strptime(
                    (datetime.today() + relativedelta(weeks=1, weekday=6)).strftime(
                        '%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S'))]},
                'current_month': {'label': _('Current Month'), 'domain': [('check_in', '<', datetime.strptime(
                    (datetime.today() + relativedelta(months=1)).strftime('%Y-%m-01 %H:%M:%S'),
                    '%Y-%m-01 %H:%M:%S')), ('check_in', '>=', time.strftime('%Y-%m-01'))]},
                'this_year': {'label': _('This Year'), 'domain': [('check_in', '<=', time.strftime('%Y-12-31')),
                                                                  ('check_in', '>=', time.strftime('%Y-01-01'))]},
                'last_year': {'label': _('Last Year'), 'domain': [
                    ('check_in', '>=', (datetime.today() - relativedelta(years=1)).strftime('%Y-01-01')),
                    ('check_in', '<=', time.strftime('%Y-01-01'))]},
                'this_week': {'label': _('This Week'), 'domain': [('check_in', '<=', (
                        datetime.today() + relativedelta(weeks=0, day=7, weekday=1)).strftime('%Y-%m-%d')),
                                                                  ('check_in', '>=', (
                                                                          datetime.today() - relativedelta(
                                                                      weeks=1, weekday=0)).strftime('%Y-%m-%d'))]},
                'today': {'label': _('Today'),
                          'domain': [('check_in', '<=', datetime.today().strftime('%Y-%m-%d')),
                                     ('check_in', '>=', datetime.today().strftime('%Y-%m-%d'))]}
            },
            'all',
            "/my/attendance",
            'my_attendance_history',
            'attendance',
            'attendances'
        )
