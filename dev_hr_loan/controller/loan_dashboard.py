# -*- coding: utf-8 -*-
##############################################################################
#
#
###############################################################################
import datetime
from odoo import http
from odoo.http import request
from odoo import models, fields, api, _
from operator import itemgetter
import itertools
import operator
from datetime import date, timedelta


class ProjectFilter(http.Controller):
    """The ProjectFilter class provides the filter option to the js.
    When applying the filter returns the corresponding data."""

    @http.route('/hr/loan/all_filter', auth='public', type='json')
    def all_filter(self):
        user_list = []
        hr_list = []
        loan_type_list=[]
        user_ids = request.env['res.users'].search([])

        hr_ids = request.env['hr.employee'].search([])
        loan_type_ids=request.env['employee.loan.type'].search([])
        for loan_type_id in loan_type_ids:
            dict = {'name': loan_type_id.name, 'id': loan_type_id.id}
            loan_type_list.append(dict)
        for hr_id in hr_ids:
            dict = {'name': hr_id.name, 'id': hr_id.id}
            hr_list.append(dict)

        for user_id in user_ids:
            if user_id.has_group("dev_hr_loan.group_department_manager"):
                dic = {'name': user_id.name,
                       'id': user_id.id}
                user_list.append(dic)
        return [user_list, hr_list,loan_type_list]

    @http.route('/get/hr/loan/data', auth='public', type='json')
    def get_tiles_data(self, **kwargs):
        today = date.today()
        hr_loan_domain=[]
        if not kwargs.get('duration'):
            hr_loan_domain += [('date', '=', today)]
        if kwargs:
            if kwargs['user_id']:
                if kwargs['user_id'] != 'all':
                    user_id = int(kwargs['user_id'])
                    hr_loan_domain += [('user_id', '=', user_id)]
            if kwargs['employee_id']:
                if kwargs['employee_id'] != 'all':
                    employee_id = int(kwargs['employee_id'])
                    hr_loan_domain += [('employee_id', '=', employee_id)]
            if kwargs['type_id']:
                if kwargs['type_id'] != 'all':
                    type_id = int(kwargs['type_id'])
                    hr_loan_domain += [('loan_type_id', '=', type_id)]
            if kwargs['duration']:
                duration = kwargs['duration']
                if duration != "all":
                    duration = int(duration)
                    filter_date = today - timedelta(days=duration)
                    hr_loan_domain += [('date', '>=', filter_date), ('date', '<=', today)]
        draft_lst=[]
        submit_request_lst=[]
        department_approve_lst=[]
        paid_loan_lst=[]
        done_lst=[]
        close_lst=[]
        all_loan_ids = request.env['employee.loan'].search(hr_loan_domain)
        for loan in all_loan_ids:
            if loan.state == 'draft':
                draft_lst.append(loan.id)
            if loan.state == 'request':
                submit_request_lst.append(loan.id)
            if loan.state in ['dep_approval', 'hr_approval']:
                department_approve_lst.append(loan.id)
            if loan.state == 'paid':
                paid_loan_lst.append(loan.id)
            if loan.state  == 'done':
                done_lst.append(loan.id)
            if loan.state  == 'close':
                close_lst.append(loan.id)

        user_name = request.env.user.name
        user_img = request.env.user.image_1920
        return {
            'draft_lst': draft_lst,
            'submit_request_lst': submit_request_lst,
            'department_approve_lst': department_approve_lst,
            'paid_loan_lst': paid_loan_lst,
            'done_lst': done_lst,
            'close_lst': close_lst,
            'user_img': user_img,
            'user_name': user_name,
        }

    @http.route('/paid/loan/chart/data', auth='public', type='json')
    def installment_loan_chart_data(self, **kw):
        today = date.today()
        hr_loan_domain = []
        data = kw['data']
        if not data.get('duration'):
            hr_loan_domain += [('date', '=', today)]
        if data:
            if data['user']:
                if data['user'] != 'all':
                    user_id = int(data['user'])
                    hr_loan_domain += [('user_id', '=', user_id)]
            if data['hr']:
                if data['hr'] != 'all':
                    employee_id = int(data['hr'])
                    hr_loan_domain += [('employee_id', '=', employee_id)]
            if data['type']:
                if data['type'] != 'all':
                    type_id = int(data['type'])
                    hr_loan_domain += [('loan_type_id', '=', type_id)]

            if data['duration']:
                duration = data['duration']
                if duration != "all":
                    duration = int(duration)
                    filter_date = today - timedelta(days=duration)
                    hr_loan_domain += [('date', '>=', filter_date), ('date', '<=', today)]

        all_loan_ids = request.env['employee.loan'].search(hr_loan_domain)
        emp_loan_ids = all_loan_ids.read_group(hr_loan_domain,['employee_id'],groupby='employee_id')
        employee_lst =[]
        employee_name=[]
        for data in emp_loan_ids:
            employee_lst.append(data['employee_id'][0])
            employee_name.append(data['employee_id'][1])
        total_paid_lst=[]
        total_unpaid_lst=[]
        total_installment_lst=[]
        total_unpaid_data=[]
        all_paid_installment=[]
        all_unpaid_installment=[]
        installment_ids = request.env['installment.line'].search([])
        for data in employee_lst:
            paid_lst = []
            unpaid_lst = []
            installment_lst=[]
            for installment in installment_ids:
                if installment.employee_id.id == data:
                    installment_lst.append(installment.id)
                    if installment.is_paid:
                        paid_lst.append(installment.id)
                    else:
                        unpaid_lst.append(installment.id)
            total_paid_lst.append(len(paid_lst))
            total_unpaid_lst.append(len(unpaid_lst))
            total_installment_lst.append(len(installment_lst))
            all_paid_installment.append(paid_lst)
            all_unpaid_installment.append(unpaid_lst)
        for i in range(len(total_installment_lst)):
            total_unpaid_data.append(0-(total_installment_lst[i] - total_paid_lst[i]))

        hr_loan_installment = {
                'labels': employee_name,
                'datasets': [
                    {
                    'backgroundColor':'rgba(75, 192, 192, 0.2)',
                    'borderColor':'rgb(75, 192, 192)',
                    'borderWidth': 1,
                    'data':total_paid_lst,
                    'label': 'Paid Loan',
                    'borderRadius': 3,
                    'borderSkipped': False,
                    'detail':all_paid_installment
                    },
                    {
                        'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                        'borderColor':'rgb(255, 99, 132)',
                        'data': total_unpaid_data,
                        'borderWidth': 1,
                        'label': 'Unpaid Loan',
                        'borderRadius': 3,
                        'borderSkipped': False,
                        'detail':all_unpaid_installment,
                    }
                ]
            }

        result = {
            'hr_loan_installment': hr_loan_installment
        }
        return result

    @http.route('/loan/type/chart/data', auth='public', type='json')
    def loan_amount_chart_data(self, **kw):
        all_color_list = ['#966ca2', '#e2d65e', '#d56e80', '#c99a5c','#00daa3', '#f06c67', '#0c9fa1', '#cf9ab5',
                          '#bce459', '#3f8eae', '#ed843f', '#00c4aa','#61e180', '#bf784b', '#fec863', '#7269ad']
        today = date.today()
        hr_loan_domain = [('state','=','paid')]
        data = kw['data']
        if not data.get('duration'):
            hr_loan_domain += [('date', '=', today)]
        if data:
            if data['user']:
                if data['user'] != 'all':
                    user_id = int(data['user'])
                    hr_loan_domain += [('user_id', '=', user_id)]
            if data['hr']:
                if data['hr'] != 'all':
                    employee_id = int(data['hr'])
                    hr_loan_domain += [('employee_id', '=', employee_id)]
            if data['type']:
                if data['type'] != 'all':
                    type_id = int(data['type'])
                    hr_loan_domain += [('loan_type_id', '=', type_id)]

            if data['duration']:
                duration = data['duration']
                if duration != "all":
                    duration = int(duration)
                    filter_date = today - timedelta(days=duration)
                    hr_loan_domain += [('date', '>=', filter_date), ('date', '<=', today)]

        all_hr_loan=request.env['employee.loan'].search_read(hr_loan_domain,fields=['name', 'employee_id', 'loan_type_id','loan_amount'])
        loan_with_type_id = [hr_loan for hr_loan in all_hr_loan if hr_loan.get('loan_type_id')]
        loan_lines = sorted(loan_with_type_id, key=itemgetter('loan_type_id'))
        inv_groups = itertools.groupby(loan_lines, key=operator.itemgetter('loan_type_id'))
        loan_type_lines = [{'loan_type_id': k, 'values': [x for x in v]} for k, v in inv_groups]
        loan_amount_data = []
        for hr_loan in loan_type_lines:
            loan_type = hr_loan.get('loan_type_id')[1]
            loan_lst = []
            for id in hr_loan['values']:
                loan_lst.append(id['id'])
            total_loan_amount = sum([l.get('loan_amount') for l in hr_loan.get('values')])
            loan_amount_data.append({'loan_type_id': loan_type, 'loan_amount': total_loan_amount, 'id': loan_lst})
        final_loan_amount_chart_record = (sorted(loan_amount_data, key=lambda i: i['loan_amount'], reverse=True))
        loan_type_lst=[]
        loan_amount_lst=[]
        hr_id_lst=[]
        for due_chart_record_data in final_loan_amount_chart_record:
            loan_type_lst.append(due_chart_record_data.get('loan_type_id'))
            loan_amount_lst.append(due_chart_record_data.get('loan_amount'))
            hr_id_lst.append(due_chart_record_data.get('id'))
        loan_type_chart_data = {
            'labels': loan_type_lst,
            'datasets': [{
                'label': "Loan Type",
                'backgroundColor': all_color_list[:len(loan_type_lst)],
                'data': loan_amount_lst,
                'detail': hr_id_lst
            }]
        }
        return {
            'loan_type_chart_data':loan_type_chart_data,
        }

    @http.route('/hr/loan/chart/data', auth='public', type='json')
    def hr_loan_chart_data(self, **kw):
        all_color_list = ['#00daa3', '#f06c67', '#0c9fa1', '#cf9ab5', '#bce459', '#3f8eae', '#ed843f', '#00c4aa',
                          '#966ca2', '#e2d65e', '#d56e80', '#c99a5c', '#61e180', '#bf784b', '#fec863', '#7269ad']
        today = date.today()
        hr_loan_domain = [('state', '=', 'paid')]
        data = kw['data']
        if not data.get('duration'):
            hr_loan_domain += [('date', '=', today)]
        if data:
            if data['user']:
                if data['user'] != 'all':
                    user_id = int(data['user'])
                    hr_loan_domain += [('user_id', '=', user_id)]
            if data['hr']:
                if data['hr'] != 'all':
                    employee_id = int(data['hr'])
                    hr_loan_domain += [('employee_id', '=', employee_id)]
            if data['type']:
                if data['type'] != 'all':
                    type_id = int(data['type'])
                    hr_loan_domain += [('loan_type_id', '=', type_id)]

            if data['duration']:
                duration = data['duration']
                if duration != "all":
                    duration = int(duration)
                    filter_date = today - timedelta(days=duration)
                    hr_loan_domain += [('date', '>=', filter_date), ('date', '<=', today)]

        all_hr_loan=request.env['employee.loan'].search_read(hr_loan_domain,fields=['name', 'employee_id', 'loan_type_id','loan_amount'])
        loan_with_employee_id = [hr_loan for hr_loan in all_hr_loan if hr_loan.get('employee_id')]
        loan_lines = sorted(loan_with_employee_id, key=itemgetter('employee_id'))
        inv_groups = itertools.groupby(loan_lines, key=operator.itemgetter('employee_id'))
        hr_loan_lines = [{'employee_id': k, 'values': [x for x in v]} for k, v in inv_groups]
        loan_amount_data = []
        for hr_loan in hr_loan_lines:
            loan_type = hr_loan.get('employee_id')[1]
            loan_lst = []
            for id in hr_loan['values']:
                loan_lst.append(id['id'])
            total_loan_amount = sum([l.get('loan_amount') for l in hr_loan.get('values')])
            loan_amount_data.append({'employee_id': loan_type, 'loan_amount': total_loan_amount, 'id': loan_lst})
        final_loan_amount_chart_record = (sorted(loan_amount_data, key=lambda i: i['loan_amount'], reverse=True))
        hr_lst=[]
        loan_amount_lst=[]
        hr_id_lst=[]
        for due_chart_record_data in final_loan_amount_chart_record:
            hr_lst.append(due_chart_record_data.get('employee_id'))
            loan_amount_lst.append(due_chart_record_data.get('loan_amount'))
            hr_id_lst.append(due_chart_record_data.get('id'))
        hr_loan_chart_data = {
            'labels': hr_lst,
            'datasets': [{
                'backgroundColor': all_color_list[:len(hr_lst)],
                'data': loan_amount_lst,
                'detail': hr_id_lst
            }]
        }
        return {
            'hr_loan_chart_data':hr_loan_chart_data,
        }

    @http.route('/loan/list/data', auth='public', type='json')
    def get_loan_list_data(self, **kw):
        today = date.today()
        hr_loan_domain = [('state', '=', 'request')]
        data = kw['data']
        if not data.get('duration'):
            hr_loan_domain += [('date', '=', today)]
        if data:
            if data['user']:
                if data['user'] != 'all':
                    user_id = int(data['user'])
                    hr_loan_domain += [('user_id', '=', user_id)]
            if data['hr']:
                if data['hr'] != 'all':
                    employee_id = int(data['hr'])
                    hr_loan_domain += [('employee_id', '=', employee_id)]
            if data['type']:
                if data['type'] != 'all':
                    type_id = int(data['type'])
                    hr_loan_domain += [('loan_type_id', '=', type_id)]

            if data['duration']:
                duration = data['duration']
                if duration != "all":
                    duration = int(duration)
                    filter_date = today - timedelta(days=duration)
                    hr_loan_domain += [('date', '>=', filter_date), ('date', '<=', today)]
        hr_loan_list = request.env['employee.loan'].search_read(hr_loan_domain ,
                                                                   fields=['name', 'employee_id', 'job_id','loan_amount','loan_type_id','term','interest_rate','date'],
                                                                   order="id desc")
        return{
        'hr_loan_list':hr_loan_list,
        }

    @http.route('/loan/filter-apply', auth='public', type='json')
    def loan_filter_apply(self, **kw):
        data = kw['data']
        user_id = data['user']
        employee_id = data['hr']
        type_id = data['type']
        duration = data['duration']
        result = self.get_tiles_data(user_id=user_id, employee_id=employee_id,type_id=type_id,duration=duration)
        return result
