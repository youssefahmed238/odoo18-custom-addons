from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.tools import format_datetime
import base64
from odoo import models, fields

class PortalApprovals(CustomerPortal):


    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        print(values)
        if 'approvals_count' in counters:
            domain = [('request_owner_id', '=', request.env.user.id)]
            values['approvals_count'] = request.env['approval.request'].search_count(domain)
        return values



    @http.route(['/my/approvals'], type='http', auth="user", website=True)
    def portal_my_approvals_dashboard(self, **kw):
        approvals = request.env['approval.request'].sudo().search([
            ('request_owner_id', '=', request.env.user.id)
        ])

        categories = request.env['approval.category'].sudo().search([
            '|', '|', '|', '|', '|', '|', '|',
            ('show_trip_portal', '=', True),
            ('show_borrow_portal', '=', True),
            ('show_general_portal', '=', True),
            ('show_contract_portal', '=', True),
            ('show_payment_portal', '=', True),
            ('show_car_rental_portal', '=', True),
            ('show_job_referral_portal', '=', True),
            ('show_procurement_portal', '=', True),
        ])

        categories = categories.filtered(
            lambda c: c.get_external_id().get(c.id) != 'approvals_purchase.approval_category_data_rfq'
        )

        values = {
            'approvals': approvals,
            'categories': categories,
            'page_name': 'approvals',
        }
        return request.render("vit_employee_self_service_portal.portal_my_approvals_dashboard", values)

    @http.route(['/my/approvals/category/<int:category_id>'], type='http', auth="user", website=True)
    def portal_approvals_by_category(self, category_id, **kwargs):
        # هات الكاتيجوري
        category = request.env['approval.category'].browse(category_id)

        if not category.exists():
            return request.not_found()

        approvals = request.env['approval.request'].search([('category_id', '=', category_id)])


        return request.render("vit_employee_self_service_portal.portal_my_approvals_by_category", {
            'format_datetime': lambda dt, tz='UTC': format_datetime(request.env, dt, tz=tz),
            'category': category,
            'approvals': approvals,
        })


    @http.route(['/my/approvals/<int:approval_id>'], type='http', auth="user", website=True)
    def portal_approval_detail(self, approval_id, **kwargs):
        # 1) هات الـ Approval
        approval = request.env['approval.request'].browse(approval_id)
        if not approval.exists():
            return request.not_found()

        xml_id = approval.category_id.get_external_id().get(approval.category_id.id)

        if xml_id == "approvals.approval_category_data_business_trip":
            template = "vit_employee_self_service_portal.portal_approval_detail_business_trip"

        elif xml_id == "approvals.approval_category_data_payment_application":
            template = "vit_employee_self_service_portal.portal_approval_detail_payment"

        elif xml_id == "approvals.approval_category_data_borrow_items":
            template = "vit_employee_self_service_portal.portal_approval_detail_borrow_items"

        elif xml_id == "approvals.approval_category_data_general_approval":
            template = "vit_employee_self_service_portal.portal_approval_detail_general"

        elif xml_id == "approvals.approval_category_data_contract_approval":
            template = "vit_employee_self_service_portal.portal_approval_detail_contract"

        elif xml_id == "approvals.approval_category_data_car_rental_application":
            template = "vit_employee_self_service_portal.portal_approval_detail_car_rental"

        elif xml_id == "approvals.approval_category_data_job_referral_award":
            template = "vit_employee_self_service_portal.portal_approval_detail_job_award"

        elif xml_id == "approvals.approval_category_data_procurement":
            template = "vit_employee_self_service_portal.portal_approval_detail_procurement"

        else:
            template = "vit_employee_self_service_portal.portal_approval_detail_default"

        return request.render(template, {
            'approval': approval,
        })

        # Route: show the form page for creating a new Business Trip request

    @http.route(['/request/business_trip'], type='http', auth="user", website=True)
    def new_business_trip(self, **kw):
        # Pass current partner (employee) data to the template
        return request.render("vit_employee_self_service_portal.portal_request_business_trip")

    # Route: handle form submission and create a new record
    @http.route(['/create_new_business_trip'], type='http', auth="user", methods=['POST'], website=True)
    def create_business_trip(self, **post):
        # Create a new approval.request with category = Business Trip
        file = post.get('attachment')
        category = request.env.ref("approvals.approval_category_data_business_trip")
        business_trip = request.env['approval.request'].sudo().create({
            'name': post.get('name'),
            'category_id': category.id,
            'date_start': post.get('date_start'),
            'date_end': post.get('date_end'),
            'location': post.get('location'),
        })
        # If file attached, save it as attachment
        if file and hasattr(file, 'read'):
            request.env['ir.attachment'].sudo().create({
                'name': file.filename,
                'res_model': 'approval.request',
                'res_id': business_trip.id,
                'type': 'binary',
                'datas': base64.b64encode(file.read()),
                'mimetype': file.content_type,
            })
        # Redirect to success page
        return request.render("vit_employee_self_service_portal.new_business_trip_success")



    @http.route(['/request/borrow_items'], type='http', auth="user", website=True)
    def request_borrow_items_form(self, **kw):
        return request.render("vit_employee_self_service_portal.portal_request_borrow_items")

    @http.route(['/create_new_borrow_item'], type='http', auth="user", methods=['POST'], website=True, csrf=True)
    def create_new_borrow_item(self, **post):
        file = post.get('attachment')
        category = request.env.ref("approvals.approval_category_data_borrow_items")

        borrow_item = request.env['approval.request'].sudo().create({
            'name': post.get('name'),
            'category_id': category.id,
            'date_start': post.get('date_start'),
            'date_end': post.get('date_end'),
        })
        # If file attached, save it as attachment
        if file and hasattr(file, 'read'):
            request.env['ir.attachment'].sudo().create({
                'name': file.filename,
                'res_model': 'approval.request',
                'res_id': borrow_item.id,
                'type': 'binary',
                'datas': base64.b64encode(file.read()),
                'mimetype': file.content_type,
            })
        return request.render("vit_employee_self_service_portal.new_borrow_item_success")

    # Route: show the form for creating a new Procurement request
    @http.route(['/request/procurement'], type='http', auth="user", website=True)
    def new_procurement(self, **kw):
        return request.render("vit_employee_self_service_portal.portal_request_procurement")

    # Route: handle submission and create new Procurement request
    @http.route(['/create_new_procurement'], type='http', auth="user", methods=['POST'], website=True)
    def create_procurement(self, **post):
        # Get Procurement category
        category = request.env.ref("approvals.approval_category_data_procurement")
        file = post.get('attachment')

        # Create procurement record and store it in a variable
        procurement = request.env['approval.request'].sudo().create({
            'name': post.get('name'),
            'category_id': category.id,
            'quantity': post.get('quantity'),
            'amount': post.get('amount'),
            'request_owner_id': request.env.user.id,
        })

        # If file attached, save it as attachment
        if file and hasattr(file, 'read'):
            request.env['ir.attachment'].sudo().create({
                'name': file.filename,
                'res_model': 'approval.request',
                'res_id': procurement.id,
                'type': 'binary',
                'datas': base64.b64encode(file.read()),
                'mimetype': file.content_type,
            })


        return request.render("vit_employee_self_service_portal.new_procurement_success")




    # ---------------- General ----------------
    @http.route(['/request/general_approval'], type='http', auth="user", website=True)
    def new_general(self, **kw):
        partners = request.env['res.partner'].sudo().search([], order='name')
        return request.render("vit_employee_self_service_portal.portal_request_general", {
            'partners': partners
        })

    @http.route(['/create_new_general'], type='http', auth="user", methods=['POST'], website=True)
    def create_general(self, **post):
        category = request.env.ref("approvals.approval_category_data_general_approval")
        file = post.get('attachment')

        general =  request.env['approval.request'].sudo().create({
            'name': post.get('name'),
            'category_id': category.id,
            'date': post.get('date'),
            'date_start': post.get('date_start'),
            'date_end': post.get('date_end'),
            'partner_id': post.get('partner_id'),
            'amount': post.get('amount'),
            'reference': post.get('reference'),
        })
        # If file attached, save it as attachment
        if file and hasattr(file, 'read'):
            request.env['ir.attachment'].sudo().create({
                'name': file.filename,
                'res_model': 'approval.request',
                'res_id': general.id,
                'type': 'binary',
                'datas': base64.b64encode(file.read()),
                'mimetype': file.content_type,
            })

        return request.render("vit_employee_self_service_portal.new_general_success")

    # ---------------- Contract ----------------
    @http.route(['/request/contract_approval'], type='http', auth="user", website=True)
    def new_contract(self, **kw):
        partners = request.env['res.partner'].sudo().search([], order='name')
        return request.render("vit_employee_self_service_portal.portal_request_contract", {
            'partners': partners
        })

    @http.route(['/create_new_contract'], type='http', auth="user", methods=['POST'], website=True)
    def create_contract(self, **post):
        category = request.env.ref("approvals.approval_category_data_contract_approval")
        file = post.get('attachment')
        new_contract = request.env['approval.request'].sudo().create({
            'name': post.get('name'),
            'category_id': category.id,
            'partner_id': post.get('partner_id'),
            'amount': post.get('amount'),
            'reference': post.get('reference'),
        })
        # If file attached, save it as attachment
        if file and hasattr(file, 'read'):
            request.env['ir.attachment'].sudo().create({
                'name': file.filename,
                'res_model': 'approval.request',
                'res_id': new_contract.id,
                'type': 'binary',
                'datas': base64.b64encode(file.read()),
                'mimetype': file.content_type,
            })

        return request.render("vit_employee_self_service_portal.new_contract_success")

    # ---------------- Payment ----------------
    @http.route(['/request/payment_application'], type='http', auth="user", website=True)
    def new_payment(self, **kw):
        partners = request.env['res.partner'].sudo().search([], order='name')
        return request.render("vit_employee_self_service_portal.portal_request_payment", {
            'partners': partners
        })

    @http.route(['/create_new_payment'], type='http', auth="user", methods=['POST'], website=True)
    def create_payment(self, **post):
        file = post.get('attachment')
        category = request.env.ref("approvals.approval_category_data_payment_application")
        new_payment = request.env['approval.request'].sudo().create({
            'name': post.get('name'),
            'category_id': category.id,
            'date': post.get('date'),
            'partner_id': post.get('partner_id'),
            'amount': post.get('amount'),
        })
        # If file attached, save it as attachment
        if file and hasattr(file, 'read'):
            request.env['ir.attachment'].sudo().create({
                'name': file.filename,
                'res_model': 'approval.request',
                'res_id': new_payment.id,
                'type': 'binary',
                'datas': base64.b64encode(file.read()),
                'mimetype': file.content_type,
            })

        return request.render("vit_employee_self_service_portal.new_payment_success")

    # ---------------- Car Rental ----------------
    @http.route(['/request/car_rental'], type='http', auth="user", website=True)
    def new_car_rental(self, **kw):
        return request.render("vit_employee_self_service_portal.portal_request_car_rental")

    @http.route(['/create_new_car_rental'], type='http', auth="user", methods=['POST'], website=True)
    def create_car_rental(self, **post):
        category = request.env.ref("approvals.approval_category_data_car_rental_application")
        file = post.get('attachment')
        car_rental = request.env['approval.request'].sudo().create({
            'name': post.get('name'),
            'category_id': category.id,
            'date_start': post.get('date_start'),
            'date_end': post.get('date_end'),
        })
        # If file attached, save it as attachment
        if file and hasattr(file, 'read'):
            request.env['ir.attachment'].sudo().create({
                'name': file.filename,
                'res_model': 'approval.request',
                'res_id': car_rental.id,
                'type': 'binary',
                'datas': base64.b64encode(file.read()),
                'mimetype': file.content_type,
            })

        return request.render("vit_employee_self_service_portal.new_car_rental_success")

    # ---------------- Job Referral Award ----------------
    @http.route(['/request/job_award'], type='http', auth="user", website=True)
    def new_job_award(self, **kw):
        partners = request.env['res.partner'].sudo().search([], order='name')
        return request.render("vit_employee_self_service_portal.portal_request_job_award", {
            'partners': partners
        })

    @http.route(['/create_new_job_award'], type='http', auth="user", methods=['POST'], website=True)
    def create_job_award(self, **post):
        file = post.get('attachment')
        category = request.env.ref("approvals.approval_category_data_job_referral_award")
        job_award = request.env['approval.request'].sudo().create({
            'name': post.get('name'),
            'category_id': category.id,
            'partner_id': post.get('partner_id'),
        })
        # If file attached, save it as attachment
        if file and hasattr(file, 'read'):
            request.env['ir.attachment'].sudo().create({
                'name': file.filename,
                'res_model': 'approval.request',
                'res_id': job_award.id,
                'type': 'binary',
                'datas': base64.b64encode(file.read()),
                'mimetype': file.content_type,
            })
        return request.render("vit_employee_self_service_portal.new_job_award_success")

    @http.route('/edit_approval/<int:app_id>', type='http', auth="public", website=True)
    def edit_approval(self, app_id=None, **kw):
        approval = request.env['approval.request'].sudo().browse(app_id)
        if not approval.exists():
            return request.redirect('/my/approvals')

        values = {
            'approval': approval,
            'categories': request.env['approval.category'].sudo().search([]),
            'partners': request.env['res.partner'].sudo().search([], order='name'),
        }
        return request.render("vit_employee_self_service_portal.portal_edit_approval_form", values)

    @http.route('/save_approval', type='http', auth="public", website=True, methods=['POST'], csrf=False)
    def save_approval(self, **post):
        app_id = int(post.get('app_id'))
        approval = request.env['approval.request'].sudo().browse(app_id)
        if approval.exists():
            vals = {}
            if post.get('name'):
                vals['name'] = post.get('name')
            if post.get('location'):
                vals['location'] = post.get('location')
            if post.get('date'):
                vals['date'] = post.get('date')
            if post.get('date_start'):
                vals['date_start'] = post.get('date_start')
            if post.get('date_end'):
                vals['date_end'] = post.get('date_end')
            if post.get('category_id'):
                vals['category_id'] = int(post.get('category_id'))
            # new fields
            if post.get('amount'):
                vals['amount'] = float(post.get('amount'))
            if post.get('quantity'):
                vals['quantity'] = int(post.get('quantity'))
            if post.get('reference'):
                vals['reference'] = post.get('reference')
            if post.get('partner_id'):
                vals['partner_id'] = int(post.get('partner_id'))
            # For attachment, we need to handle file upload
            if post.get('attachment'):
                attachment = request.httprequest.files.get('attachment')
                if attachment:
                    attachment_vals = {
                        'name': attachment.filename,
                        'datas': base64.b64encode(attachment.read()),
                        'res_model': 'approval.request',
                        'res_id': approval.id,
                    }
                    request.env['ir.attachment'].sudo().create(attachment_vals)

            approval.write(vals)
        return request.redirect('/my/approvals')
