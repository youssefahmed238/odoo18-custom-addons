import base64
from collections import OrderedDict
from datetime import datetime
import time
from dateutil.relativedelta import relativedelta
from odoo import fields, http, _
from odoo.http import request
from odoo.addons.portal.controllers import portal
from odoo.addons.portal.controllers.portal import pager as portal_pager
from odoo.exceptions import AccessError, MissingError, ValidationError
from odoo.osv.expression import AND, OR
import json
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT


class PortalLeaves(portal.CustomerPortal):

    # -------------------------
    # Helpers
    # -------------------------

    def _alloc_domain_for_employee(self, emp_id):
        """Build a domain for hr.leave.allocation that works on both schemas:
        - v18 core: uses employee_id only
        - older/custom: may also have employee_ids (M2M)
        """
        Allocation = request.env['hr.leave.allocation']
        dom = [('employee_id', '=', emp_id)]
        # Keep compatibility with DBs that still have employee_ids
        if 'employee_ids' in Allocation._fields:
            dom = ['|', ('employee_id', '=', emp_id), ('employee_ids', 'in', [emp_id])]
        return dom

    def _leaves_get_page_view_values(self, leave, access_token, **kwargs):
        values = {
            'leave': leave,
            'page_name': 'leave',
            'report_type': 'html',
        }
        history = 'my_leaves_history'
        return self._get_page_view_values(leave, access_token, values, history, False, **kwargs)

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id
        employee_id = request.env['hr.employee'].sudo().search([('work_contact_id', '=', partner.id)], limit=1) or False
        Leaves = request.env['hr.leave']
        if 'leaves_count' in counters:
            if employee_id:
                values['leaves_count'] = Leaves.sudo().search_count([
                    ('employee_id', '=', employee_id.id),
                    ('state', '!=', 'draft'),
                ])
            else:
                values['leaves_count'] = 0
        return values

    def _get_leaves_search_domain(self, search_in, search):
        search_domain = []
        if search_in in ('all', 'name'):
            search_domain = OR([search_domain, [('holiday_status_id.name', 'ilike', search)]])
        if search_in in ('all', 'status'):
            search_domain = OR([search_domain, [('state', 'ilike', search)]])
        return search_domain

    def _render_portal_leaves(self, template, page, date_begin, date_end, sortby, filterby, domain, searchbar_filters,
                              default_filter, url, history, page_name, key, search=None, search_in='all'):
        values = self._prepare_portal_layout_values()
        Leaves = request.env['hr.leave'].sudo()
        partner = request.env.user.partner_id
        employee_id = request.env['hr.employee'].sudo().search([('work_contact_id', '=', partner.id)], limit=1)

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        searchbar_sortings = {
            'date_from': {'label': _('Start Date'), 'leave': 'request_date_from asc'},
            'date_to': {'label': _('End Date'), 'leave': 'request_date_to desc'},
            'name': {'label': _('Leave Type'), 'leave': 'holiday_status_id asc'},
            'state': {'label': _('Status'), 'leave': 'state desc'},
        }
        searchbar_inputs = {
            'all': {'label': _('Search in All'), 'input': 'all'},
            'name': {'label': _('Search in Time Off Name'), 'input': 'name'},
            'state': {'label': _('Search in Status'), 'input': 'state'},
        }
        # default sort
        if not sortby:
            sortby = 'date_from'
        leave = searchbar_sortings[sortby]['leave']

        if searchbar_filters:
            # default filter
            if not filterby:
                filterby = default_filter
            domain += searchbar_filters[filterby]['domain']

        if search and search_in:
            domain = AND([domain, self._get_leaves_search_domain(search_in, search)])

        if employee_id:
            # SAFE allocation query (works on v18 & older/custom DBs)
            paid_time_off = request.env['hr.leave.allocation'].sudo().search(
                self._alloc_domain_for_employee(employee_id.id)
            )

            leaves_of_employee = Leaves.search([
                ('employee_id', '=', employee_id.id),
            ])

            if leaves_of_employee:
                # count for pager
                domain += [('id', 'in', leaves_of_employee.ids)]
                count = len(leaves_of_employee)
                # make pager
                pager = portal_pager(
                    url=url,
                    url_args={'date_begin': date_begin, 'date_end': date_end, 'search_in': search_in, 'search': search,
                              'sortby': sortby, 'filterby': filterby},
                    total=count,
                    page=page,
                    step=self._items_per_page
                )

                # search the leaves to display, according to the pager data
                leaves = Leaves.search(
                    domain,
                    order=leave,
                    limit=self._items_per_page,
                    offset=pager['offset']
                )
                request.session[history] = leaves.ids[:100]

                values.update({
                    'date': date_begin,
                    key: leaves,
                    'page_name': page_name,
                    'pager': pager,
                    'searchbar_sortings': searchbar_sortings,
                    'sortby': sortby,
                    'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
                    'filterby': filterby,
                    'search_in': search_in,
                    'search': search,
                    'searchbar_inputs': searchbar_inputs,
                    'default_url': url,
                    'employee_id': employee_id,              # <-- fixed
                })
            else:
                # count for pager
                count = 0
                # make pager
                pager = portal_pager(
                    url=url,
                    url_args={'date_begin': date_begin, 'date_end': date_end, 'search_in': search_in, 'search': search,
                              'sortby': sortby, 'filterby': filterby},
                    total=count,
                    page=page,
                    step=self._items_per_page
                )
                leaves = Leaves
                values.update({
                    'date': date_begin,
                    key: leaves,
                    'page_name': page_name,
                    'pager': pager,
                    'searchbar_sortings': searchbar_sortings,
                    'sortby': sortby,
                    'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
                    'filterby': filterby,
                    'search_in': search_in,
                    'search': search,
                    'searchbar_inputs': searchbar_inputs,
                    'default_url': url,
                    'employee_id': employee_id,              # <-- fixed
                })
            values.update({
                'paid_time_off': paid_time_off,
            })
        return request.render(template, values)

    @http.route(['/my/leaves', '/my/leaves/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_leaves(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None,
                         search_in='all', **kw):
        return self._render_portal_leaves(
            "vit_employee_self_service_portal.portal_my_leaves",
            page, date_begin, date_end, sortby, filterby,
            [],
            {
                'all': {'label': _('All'), 'domain': [('state', 'in', ['confirm', 'refuse', 'validate1', 'validate'])]},
                'confirm': {'label': _('Approved Time Off'), 'domain': [('state', '=', 'validate')]},
                'to_approve': {'label': _('To Approve'), 'domain': [('state', '=', 'confirm')]},
                'refuse': {'label': _('Refused'), 'domain': [('state', '=', 'refuse')]},
            },
            'all',
            "/my/leaves",
            'my_leaves_history',
            'leave',
            'leaves',
            search, search_in
        )

    @http.route(['/my/leaves/<int:leave_id>'], type='http', auth="public", website=True)
    def portal_my_leave_detail(self, leave_id=None, access_token=None, **kw):
        try:
            leave_sudo = self._document_check_access('hr.leave', leave_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        values = self._leaves_get_page_view_values(leave_sudo, access_token, **kw)
        if leave_sudo.company_id:
            values['res_company'] = leave_sudo.company_id
        return request.render("vit_employee_self_service_portal.portal_my_leave", values)

    @http.route(['/request_new_leave'], type='http', auth='public', website=True)
    def request_new_leave(self, **kw):
        partner = request.env.user.partner_id
        employee_id = request.env['hr.employee'].sudo().search([('work_contact_id', '=', partner.id)], limit=1)
        Leaves = request.env['hr.leave'].sudo()
        HrLeaveTypeObj = request.env['hr.leave.type'].sudo()
        leave_types = HrLeaveTypeObj.search([])

        # SAFE allocation query (works on v18 & older/custom DBs)
        paid_time_off = request.env['hr.leave.allocation'].sudo().search(
            self._alloc_domain_for_employee(employee_id.id)
        )

        values = {
            'partner': partner,
            'employee_id': employee_id,
            'leave': Leaves,
            'leave_type': leave_types,
            'paid_time_off': paid_time_off,
        }
        return request.render("vit_employee_self_service_portal.portal_request_leave_page", values)

    @http.route(['/create_new_leave'], type='http', auth="public", website=True)
    def create_new_leave_request(self, **kw):
        partner = request.env.user.partner_id
        employee_id = request.env['hr.employee'].sudo().search([('work_contact_id', '=', partner.id)], limit=1)
        values = {
            'partner': partner,
            'employee_id': employee_id,
            'leave_type': request.env['hr.leave.type'].sudo().search([]),
            'error_list': [],
        }
        values.update(kw)
        try:
            # Validate the leave request
            error_list = self._validate_leave_request(kw)
            if not error_list:
                # Process leave request
                self._process_leave_request(kw)
                return request.render("vit_employee_self_service_portal.new_leave_success", {})
            else:
                values['error_list'] = error_list
                return request.render("vit_employee_self_service_portal.portal_request_leave_page", values)
        except Exception as e:
            values['error_list'] = [str(e)]
            return request.render("vit_employee_self_service_portal.portal_request_leave_page", values)

    def _validate_leave_request(self, kw):
        # Validate the leave request data provided in `kw`.
        error_list = []
        try:
            # Parse dates
            date_from = datetime.strptime(kw.get('leave_from'), "%m/%d/%Y")
            date_to = datetime.strptime(kw.get('leave_to'), "%m/%d/%Y")

            # Date validation
            if date_to < date_from:
                error_list.append("تاريخ نهاية الاجازة لا يمكن ان يسبق تاريخ بداية الاجازة")

        except Exception as e:
            error_list.append(str(e))

        return error_list

    def _process_leave_request(self, kw):
        # Create or update a leave request based on the data provided in `kw`.
        partner = request.env.user.partner_id
        employee_id = request.env['hr.employee'].sudo().search([('work_contact_id', '=', partner.id)], limit=1)
        date_from = datetime.strptime(kw.get('leave_from'), "%m/%d/%Y")
        date_to = datetime.strptime(kw.get('leave_to'), "%m/%d/%Y")
        leave_type_id = request.env['hr.leave.type'].sudo().browse(int(kw.get('leave_type_detail')))

        if kw.get('leave_id'):
            leave_id = request.env['hr.leave'].sudo().browse(int(kw.get('leave_id')))
            leave_id.sudo().write({
                'holiday_status_id': leave_type_id.id,
                'date_from': date_from,
                'date_to': date_to,
                'request_date_from': date_from,
                'request_date_to': date_to,
                'name': kw.get('reason'),
                'private_name': kw.get('reason'),
            })
            # Upload Attachments
            self.process_leave_attachment(kw, leave_id)
        else:
            created_leave = request.env['hr.leave'].sudo().create({
                # 'holiday_type': 'employee',
                'employee_id': employee_id.id,
                'holiday_status_id': leave_type_id.id,
                'date_from': date_from,
                'date_to': date_to,
                'request_date_from': date_from,
                'request_date_to': date_to,
                'name': kw.get('reason'),
                'private_name': kw.get('reason'),
                'company_id': request.env.company.id,
            })
            created_leave.sudo().message_subscribe(partner_ids=partner.ids)
            self.process_leave_attachment(kw, created_leave)

    def process_leave_attachment(self, kw, leave):
        if 'sick_leave_attach' in request.params or kw.get('sick_leave_attach'):
            if request.httprequest and request.httprequest.files:
                attachment_list = []
                for attach in request.httprequest.files.getlist('sick_leave_attach'):
                    attach_file = attach.read()
                    if attach_file:
                        attachment = request.env['ir.attachment'].sudo().create({
                            'name': attach.filename,
                            'res_model': 'hr.leave',
                            'type': 'binary',
                            'datas': base64.b64encode(attach_file),
                            'mimetype': attach.mimetype,
                            'res_id': leave.id,
                        })
                        attachment_list.append(attachment.id)

                if attachment_list:
                    message = 'Leave Attachment for %s' % leave.employee_id.name
                    leave.message_post(body=message, subject="Leave Attach",
                                       message_type="notification", attachment_ids=attachment_list)

    @http.route('/new_leave_success', type='http', auth="public", website=True)
    def leave_success(self, **kw):
        return request.render("vit_employee_self_service_portal.new_leave_success")

    @http.route('/edit_leave/<int:leave_id>', type='http', auth="public", website=True)
    def edit_leave(self, leave_id=None, **kw):
        leave_res_id = request.env['hr.leave'].sudo().search([('id', '=', leave_id)], limit=1)
        partner = request.env.user.partner_id
        employee_id = request.env['hr.employee'].sudo().search([('work_contact_id', '=', partner.id)], limit=1)
        if leave_res_id:
            values = {
                'partner': partner,
                'leave_type': request.env['hr.leave.type'].sudo().search([]),
                'leave_type_detail': leave_res_id.holiday_status_id.id,
                'leave_from': leave_res_id.request_date_from,
                'leave_to': leave_res_id.request_date_to,
                'reason': leave_res_id.private_name or leave_res_id.name,
                'leave_id': leave_res_id.id,
            }
            return request.render("vit_employee_self_service_portal.portal_request_leave_page", values)
        return request.redirect('/my/leaves')

    # --------------------------------------------------------------------------------------------------------------------------
    @http.route(['/my/timeoff/<int:leave_id>'], type='http', auth="user", website=True)
    def timeoff_leave(self, leave_id, **kw):
        HrLeaveTypeObj = request.env['hr.leave.type'].sudo()
        leave_type = HrLeaveTypeObj.browse(leave_id)
        partner = request.env.user.partner_id
        employee_id = request.env['hr.employee'].sudo().search([('work_contact_id', '=', partner.id)])
        allocations_leaves_consumed, extra_data = employee_id.sudo()._get_consumed_leaves(leave_type, False)

        values = {
            "allocated": 0,
            "accrual": 0,
            "approved": 0,
            "planned": 0,
            "available": 0
        }
        for allocation, data in allocations_leaves_consumed[employee_id][leave_type].items():
            values['allocated'] += data['max_leaves']
            values['accrual'] += data['accrual_bonus']
            values['approved'] += data['leaves_taken']
            values['planned'] += data['virtual_leaves_taken'] - data['leaves_taken']
            values['available'] += data['virtual_remaining_leaves']

        return request.render("vit_employee_self_service_portal.request_details_page", values)
