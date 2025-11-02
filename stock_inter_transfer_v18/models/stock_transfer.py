# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.tools import float_is_zero
from odoo.exceptions import UserError
from collections import defaultdict

# from enterprise.test_convert.tests.test_env import record


class StockTransfer(models.Model):
    _name = "stock.transfer"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'product.catalog.mixin']
    _order = 'id desc'
    _description = "Stock Transfer"
    _check_company_auto = True

    def _compute_picking_count(self):
        for rec in self:
            rec.picking_count = len(rec.picking_ids)

    @api.depends('picking_ids', 'picking_ids.state')
    def check_status(self):
        for rec in self:
            state = rec.state or 'pending'
            if rec.approval_required and rec.is_confirm:
                state = 'confirm'
            if rec.approval_required and rec.is_approved:
                state = 'approved'
            source_picking = rec.sudo().picking_ids.filtered(
                lambda l: l.state != 'cancel' and (l.picking_type_id.id == rec.picking_type_id.id))
            if rec.picking_ids and source_picking and source_picking[0].state == 'done':
                state = 'deliver_transit'
            dest_picking = rec.sudo().picking_ids.filtered(
                lambda l: l.state != 'cancel' and (l.location_dest_id.id == rec.location_dest_id.id))
            if rec.picking_ids and dest_picking and dest_picking[0].state == 'done':
                state = 'deliver_dest'

            dest_picking = rec.sudo().picking_ids.filtered(
                lambda l: l.state != 'cancel' and (l.location_dest_id.id == rec.location_id.id))
            if rec.picking_ids and dest_picking:
                state = 'deliver_transit_source'
            if rec.picking_ids and dest_picking and dest_picking[0].state == 'done':
                state = 'deliver_source'

            if rec.is_cancel:
                state = 'cancel'
            rec.state = state

            if state == 'deliver_transit' and rec.transfer_type == 'transfer_with_transit':
                rec.notify_destination_users()

    def notify_destination_users(self):
        """ Notify users in the destination location when the transfer is in 'deliver_transit' state. """
        activity_type = self.env.ref('mail.mail_activity_data_todo')
        model_id = self.env['ir.model']._get_id('stock.transfer')

        users = self.env['res.users'].search([('restrict_locations', '=', True)])

        users_destination = users.filtered(lambda u: self.location_dest_id.id in u.stock_location_ids.ids)

        message = _("The transfer (%s) has reached the transit stage. You need to receive the products.") % (self.name)

        for user in users_destination:
            self.env['mail.activity'].sudo().create({
                'res_id': self.id,
                'res_model_id': model_id,
                'activity_type_id': activity_type.id,
                'summary': "Stock Transfer - Receive Products",
                'note': message,
                'automated': True,
                'user_id': user.id,
                'chaining_type': 'suggest',
            })

    name = fields.Char('Referencia', default=lambda self: _('New'), copy=False, index=True, readonly=True)
    is_confirm = fields.Boolean(string="It is confirmed", default=False, copy=False)
    is_cancel = fields.Boolean(string="It's canceled", default=False, copy=False)
    picking_count = fields.Integer(compute='_compute_picking_count', string='Number of transfers')
    partner_id = fields.Many2one('res.partner', 'Owner', tracking=True)
    transfer_type = fields.Selection(
        [('direct_transfer', 'Direct Transfer'), ('transfer_with_transit', 'Transfer With Transit')],
        string="Transfer Type", default="direct_transfer")
    location_id = fields.Many2one('stock.location', "Source", tracking=True, check_company=True, domain=lambda self: self._get_location_domain())
    location_dest_id = fields.Many2one('stock.location', "Destination", tracking=True, domain=lambda self: self._get_location_domain())
    transit_location_id = fields.Many2one('stock.location', "Transit Location", tracking=True, check_company=True, domain=lambda self: self._get_location_domain())
    picking_type_id = fields.Many2one('stock.picking.type', 'Operation Type', tracking=True, check_company=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id, index=True, required=True, tracking=True)
    state = fields.Selection(
        [('pending', 'Pending'), ('confirm', 'Waiting for approval'), ('approved', 'Approved'), ('cancel', 'Canceled'),
         ('deliver_transit', 'Sent To Transit'), ('deliver_dest', 'Delivered To Destination')
            , ('deliver_transit_source', 'Returned To Source'), ('deliver_source', 'Delivered To Source'), ('source_approved','Source Approved'),],
        string="state", compute="check_status", copy=False, store=True)
    note = fields.Text('Notes')
    transfer_lines = fields.One2many('stock.transfer.line', 'transfer_id', string="Lines")
    picking_ids = fields.One2many('stock.picking', 'transfer_id', string="dispatches")
    approval_required = fields.Boolean("approval required")
    is_approved = fields.Boolean("Approved", default=False, help="transfer approved.", copy=False)
    user_id = fields.Many2one("res.users", string="Responsible", tracking=True, default=lambda self: self.env.user)
    first_dispatch_done = fields.Boolean(string="Dispatches Done")
    second_dispatch_progress = fields.Boolean(string="Dispatches Done")
    second_dispatch_done = fields.Boolean(string="Dispatches Done")
    transferred_to_source = fields.Boolean(string="Transferred To Source")
    _sql_constraints = [
        ('name_uniq', 'unique(name, company_id)', 'Reference must be unique per company!'),
    ]
    current_package_level_id = fields.Many2one('stock.package_level', 'Package Level')
    fields.One2many('stock.package_level', 'picking_id')

    # ----------------------------------------------------------------------------------------------------------------------------------------------
    #order type
    order_type = fields.Selection([
        ('sale_order', 'Sales Order'),
        ('purchase_order', 'Purchase Order'),
        ('negative_forecast', 'Negative Forecasted Products')
    ], string="Order Type", default=False)

    sale_order_id = fields.Many2one('sale.order', string="Sales Order")
    purchase_order_id = fields.Many2one('purchase.order', string="Purchase Order")

    @api.onchange('order_type', 'sale_order_id', 'purchase_order_id')
    def _onchange_order_type(self):
        """Handles changes in order type, clearing irrelevant fields and loading transfer lines"""

        if self.order_type == 'sale_order':
            self.purchase_order_id = False
        elif self.order_type == 'purchase_order':
            self.sale_order_id = False
        else:
            self.sale_order_id = False
            self.purchase_order_id = False

        self.transfer_lines = [(5, 0, 0)]

        if self.order_type == 'sale_order' and self.sale_order_id:
            self._load_sales_order_lines()
        elif self.order_type == 'purchase_order' and self.purchase_order_id:
            self._load_purchase_order_lines()
        elif self.order_type == 'negative_forecast':
            self._load_negative_forecasted_products()



    def _load_sales_order_lines(self):
        """Loads sales order lines into transfer lines, handling kit products by product_id"""
        transfer_lines = []
        for line in self.sale_order_id.order_line:
            product = line.product_id

            # bom = self.env['mrp.bom'].sudo().search([
                # '|',
                # ('product_id', '=', product.id),
                # ('product_tmpl_id', '=', product.product_tmpl_id.id),
                # ('type', '=', 'phantom')
            # ], limit=1)
            bom = self.env['mrp.bom'].sudo().search([
                ('product_id', '=', product.id),
                ('type', '=', 'phantom')
            ], limit=1)

            if not bom:
                bom = self.env['mrp.bom'].sudo().search([
                    ('product_tmpl_id', '=', product.product_tmpl_id.id),
                    ('type', '=', 'phantom')
                ], limit=1)
            if bom:
                for component in bom.bom_line_ids:
                    transfer_lines.append((0, 0, {
                        'product_id': component.product_id.id if component.product_id else component.product_tmpl_id.product_variant_id.id,
                        'product_uom_qty': component.product_qty * line.product_uom_qty,
                        'product_uom': component.product_uom_id.id,
                        'name': component.product_id.display_name,
                        'price_unit': component.product_id.lst_price,
                    }))
            else:
                transfer_lines.append((0, 0, {
                    'product_id': product.id,
                    'product_uom_qty': line.product_uom_qty,
                    'product_uom': product.uom_id.id,
                    'name': product.display_name,
                    'price_unit': line.price_unit,
                }))

        self.transfer_lines = transfer_lines

    def _load_purchase_order_lines(self):
        """Loads purchase order lines into transfer lines, handling kit products by product_id"""
        transfer_lines = []
        for line in self.purchase_order_id.order_line:
            product = line.product_id

            # bom = self.env['mrp.bom'].sudo().search([
                # '|',
                # ('product_id', '=', product.id),
                # ('product_tmpl_id', '=', product.product_tmpl_id.id),
                # ('type', '=', 'phantom')
            # ], limit=1)
            bom = self.env['mrp.bom'].sudo().search([
                ('product_id', '=', product.id),
                ('type', '=', 'phantom')
            ], limit=1)

            # if not bom:
                # bom = self.env['mrp.bom'].sudo().search([
                    # ('product_tmpl_id', '=', product.product_tmpl_id.id),
                    # ('type', '=', 'phantom')
                # ], limit=1)

            if bom:
                for component in bom.bom_line_ids:
                    transfer_lines.append((0, 0, {
                        'product_id': component.product_id.id if component.product_id else component.product_tmpl_id.product_variant_id.id,
                        'product_uom_qty': component.product_qty * line.product_qty,
                        'product_uom': component.product_uom_id.id,
                        'name': component.product_id.display_name,
                        'price_unit': component.product_id.lst_price,
                    }))
            else:
                transfer_lines.append((0, 0, {
                    'product_id': product.id,
                    'product_uom_qty': line.product_qty,
                    'product_uom': product.uom_id.id,
                    'name': product.display_name,
                    'price_unit': line.price_unit,
                }))

        self.transfer_lines = transfer_lines

    def _load_negative_forecasted_products(self):
        """Finds and loads negative forecasted products in the warehouse of location_dest_id, expanding kit products into their components"""
        transfer_lines = []

        if not self.location_dest_id or not self.location_dest_id.warehouse_id:
            return

        warehouse_id = self.location_dest_id.warehouse_id.id

        products = self.env['product.product'].sudo().search([])

        negative_products = products.filtered(
            lambda p: p.with_context(warehouse=warehouse_id).virtual_available < 0
        )

        for product in negative_products:
            forecasted_qty = abs(product.with_context(warehouse=warehouse_id).virtual_available)

            # bom = self.env['mrp.bom'].sudo().search([
                # '|',
                # ('product_id', '=', product.id),
                # ('product_tmpl_id', '=', product.product_tmpl_id.id),
                # ('type', '=', 'phantom')
            # ], limit=1)
            bom = self.env['mrp.bom'].sudo().search([
                ('product_id', '=', product.id),
                ('type', '=', 'phantom')
            ], limit=1)

            if not bom:
                bom = self.env['mrp.bom'].sudo().search([
                    ('product_tmpl_id', '=', product.product_tmpl_id.id),
                    ('type', '=', 'phantom')
                ], limit=1)

            if bom:
                for component in bom.bom_line_ids:
                    transfer_lines.append((0, 0, {
                        'product_id': component.product_id.id if component.product_id else component.product_tmpl_id.product_variant_id.id,
                        'product_uom_qty': component.product_qty * forecasted_qty,
                        'product_uom': component.product_uom_id.id,
                        'name': component.product_id.display_name,
                    }))
            else:
                transfer_lines.append((0, 0, {
                    'product_id': product.id,
                    'product_uom_qty': forecasted_qty,
                    'product_uom': product.uom_id.id,
                    'name': product.display_name,
                }))

        self.transfer_lines = transfer_lines

    # ----------------------------------------------------------------------------------------------------------------------------------------------
    @api.onchange('location_id')
    def _onchange_location_id_set_picking_type(self):
        if self.location_id:
            internal_transfer_picking_type = self.env['stock.picking.type'].sudo().search([
                ('code', '=', 'internal'),
                ('warehouse_id', '=', self.location_id.warehouse_id.id)
            ], limit=1).id
            print('internal_transfer_picking_type',internal_transfer_picking_type)
            if internal_transfer_picking_type:
                self.picking_type_id = internal_transfer_picking_type
            else:
                self.picking_type_id = False
                warning = {
                    'title': _("Picking Type Not Found"),
                    'message': _("No 'Internal Transfers' picking type found for the selected warehouse."),
                }
                return {'warning': warning}

    def copy(self, default=None):
        if default is None:
            default = {}
        default['first_dispatch_done'] = False
        default['second_dispatch_progress'] = False
        default['second_dispatch_done'] = False
        default['transferred_to_source'] = False
        new_transfers = []
        for transfer in self:
            new_transfer = super(StockTransfer, transfer).copy(default)

            for line in transfer.transfer_lines:
                self.env['stock.transfer.line'].create({
                    'name': line.name,
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.product_uom_qty,
                    'product_uom': line.product_uom.id,
                    'transfer_id': new_transfer.id,
                })

            new_transfers.append(new_transfer)

        return new_transfers if len(new_transfers) > 1 else new_transfers[0]

    date_order = fields.Datetime(string='Order Date', readonly=True, copy=False, states={'pending': [('readonly', False)]}, default=fields.Date.context_today)
    currency_id = fields.Many2one('res.currency', 'Currency', required=True, default=lambda self: self.env.company.currency_id.id)
    pricelist_id = fields.Many2one(
        comodel_name='product.pricelist',
        string="Pricelist",
        compute='_compute_pricelist_id',
        store=True, readonly=False, precompute=True, check_company=True,
        tracking=1,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help="If you change the pricelist, only newly added lines will be affected.")

    @api.depends('partner_id', 'company_id')
    def _compute_pricelist_id(self):
        for order in self:
            if order.state != 'pending':
                continue
            if not order.partner_id:
                order.pricelist_id = False
                continue
            order = order.with_company(order.company_id)
            order.pricelist_id = order.partner_id.property_product_pricelist

    def _get_product_catalog_order_data(self, products, **kwargs):
        pricelist = self.pricelist_id._get_products_price(
            quantity=1.0,
            products=products,
            currency=self.currency_id,
            date=self.date_order,
            **kwargs,
        )
        res = super()._get_product_catalog_order_data(products, **kwargs)

        for product in products:
            res[product.id]['price'] = pricelist.get(product.id, 0.0)
            if product.sale_line_warn != 'no-message' and product.sale_line_warn_msg:
                res[product.id]['warning'] = product.sale_line_warn_msg
            if product.sale_line_warn == "block":
                res[product.id]['readOnly'] = True
        return res

    # def _get_product_catalog_record_lines(self, product_ids, child_field=None):
    #     grouped_lines = defaultdict(lambda: self.env['stock.transfer.line'])
    #     for line in self.transfer_lines:
    #         if line.product_id.id not in product_ids:
    #             continue
    #         grouped_lines[line.product_id] |= line
    #     return grouped_lines
    def _get_product_catalog_record_lines(self, product_ids, child_field=None, **kwargs):
        grouped_lines = defaultdict(lambda: self.env['stock.transfer.line'])

        # Add your logic here if 'child_field' is required.
        if child_field:
            # You can add logic to handle the 'child_field' here
            pass

        # Existing logic to group the lines by product_id
        for line in self.transfer_lines:
            if line.product_id.id not in product_ids:
                continue
            grouped_lines[line.product_id] |= line

        return grouped_lines

    def _update_order_line_info(self, product_id, quantity, **kwargs):
        print("Product ID:", product_id, "Quantity:", quantity)
        stl = self.transfer_lines.filtered(lambda line: line.product_id.id == product_id)
        if stl:
            if quantity != 0:
                stl.product_uom_qty = quantity
            elif self.state in ['pending', 'confirm','cancel']:
                price_unit = self.pricelist_id._get_product_price(
                    product=stl.product_id,
                    quantity=1.0,
                    currency=self.currency_id,
                    date=self.date_order,
                    **kwargs,
                )
                stl.unlink()
                return price_unit
            else:
                stl.product_uom_qty = 0
        elif quantity > 0:
            product = self.env['product.product'].search([('id', '=', product_id)])
            if not product:
                raise UserError(_('Product with ID %s not found!' % product_id))
            stl = self.env['stock.transfer.line'].create({
                'name': product.name,
                'transfer_id': self.id,
                'product_id': product_id,
                'product_uom_qty': quantity,
                'product_uom': product.uom_id.id,
            })

        price_unit = self.pricelist_id._get_product_price(
            product=stl.product_id,
            quantity=1.0,
            currency=self.currency_id,
            date=self.date_order,
            **kwargs,
        )
        return price_unit

    def _check_source_location_restriction(self, source_location):
        """Check if the user has restrictions on the source location and if the requested products are available."""
        user = self.env.user.sudo()

        if user.restrict_locations:
            allowed_locations = user.stock_location_ids.sudo()
            if source_location.id not in allowed_locations.ids:
                raise UserError(
                    _("You are not allowed to approve this operation for the source location: %s.") % source_location.complete_name
                )

        insufficient_products = []

        warehouse = source_location.warehouse_id

        for line in self.transfer_lines:
            product = line.product_id
            requested_qty = line.product_uom_qty

            stock_quant = self.env['stock.quant'].sudo().search([
                ('product_id', '=', product.id),
                ('location_id', '=', source_location.id),
                ('quantity', '>', 0)
            ])

            available_qty = sum(stock_quant.mapped('quantity'))

            if available_qty < requested_qty:
                warehouse_locations = self.env['stock.location'].sudo().search([
                    ('id', '!=', source_location.id),
                    ('warehouse_id', '=', warehouse.id)
                ])

                for location in warehouse_locations:
                    stock_quant_warehouse = self.env['stock.quant'].sudo().search([
                        ('product_id', '=', product.id),
                        ('location_id', '=', location.id),
                        ('quantity', '>', 0)
                    ])
                    available_qty += sum(stock_quant_warehouse.mapped('quantity'))

                if available_qty < requested_qty:
                    insufficient_products.append(
                        _("Product: %s (Requested: %s, Available: %s)") % (
                            product.display_name, requested_qty, available_qty)
                    )

        if insufficient_products:
            error_message = _("The following products do not have enough stock in the source location:\n") + "\n".join(
                insufficient_products)
            raise UserError(error_message)

    def _check_destination_location_restriction(self, destination_location):
        """ Check if the user has restrictions on the destination location and if it is allowed. """
        user = self.env.user.sudo()
        if user.restrict_locations:
            allowed_locations = user.stock_location_ids.sudo()

            print('Allowed destination locations:', allowed_locations.mapped('complete_name'))

            if destination_location.sudo().id not in allowed_locations.ids:
                raise UserError(
                    _("You are not allowed to approve this operation for the destination location: %s.") % destination_location.complete_name
                )

    def action_source_approval(self):
        """Handle source approval by validating only the source location."""
        self._check_source_location_restriction(self.location_id)
        self.state = 'source_approved'

        if self.transfer_type == 'direct_transfer':
            activity_type = self.env.ref('mail.mail_activity_data_todo')
            model_id = self.env['ir.model']._get_id('stock.transfer')

            users = self.env['res.users'].search([('restrict_locations', '=', True)])

            users_destination = users.filtered(lambda u: self.location_dest_id.id in u.stock_location_ids.ids)

            message = _("The transfer (%s) has been approved by the source and is now waiting for your approval.") % (
                self.name)

            for user in users_destination:
                self.env['mail.activity'].sudo().create({
                    'res_id': self.id,
                    'res_model_id': model_id,
                    'activity_type_id': activity_type.id,
                    'summary': "Stock Transfer Waiting for Your Approval",
                    'note': message,
                    'automated': True,
                    'user_id': user.id,
                    'chaining_type': 'suggest',
                })

    def action_destination_approval(self):
        """Handle destination approval by validating only the destination location."""
        insufficient_products = []

        for line in self.transfer_lines:
            product = line.product_id
            requested_qty = line.product_uom_qty

            available_qty = sum(self.env['stock.quant'].sudo().search([
                ('product_id', '=', product.id),
                ('location_id', '=', self.location_id.id),
                ('quantity', '>', 0)
            ]).mapped('quantity'))
            if available_qty < requested_qty:
                insufficient_products.append(
                    _("Product: %s (Requested: %s, Available: %s)") % (
                        product.display_name, requested_qty, available_qty
                    )
                )
        self._check_destination_location_restriction(self.location_dest_id)
        self.sudo().create_stock_picking_record()

        if not insufficient_products and self.sudo().picking_ids:
            self.sudo().picking_ids.action_assign()
            self.sudo().picking_ids.button_validate()

    def create_stock_picking_record(self):
        self = self.sudo()
        picking_data = {
            'origin': self.name,
            'partner_id': self.partner_id.id,
            'picking_type_id': self.picking_type_id.id,
            'company_id': self.company_id.id,
            'note': self.note or "",
            'location_id': self.location_id.id,
            'location_dest_id': self.location_dest_id.id or "",
            'transfer_id': self.id,
        }

        new_picking = self.env['stock.picking'].sudo().create(picking_data)

        for line in self.transfer_lines:
            move_data = {
                'name': self.name,
                'state': 'confirmed',
                'product_id': line.product_id.id,
                'product_uom': line.product_uom.id,
                'product_uom_qty': line.product_uom_qty,
                'product_packaging_id': line.product_packaging_id.id,
                'picking_id': new_picking.id,
                'picking_type_id': self.picking_type_id.id,
                'location_id': self.location_id.id,
                'location_dest_id': self.location_dest_id.id or "",
                'price_unit': line.price_unit,
                'company_id': self.company_id.id,
            }
            self.env['stock.move'].sudo().create(move_data)

        self.state = 'confirm'

        return new_picking
    # ----------------------------------------------------------------------------------------------------------------------------------------------

    @api.model
    def default_get(self, fields):
        res = super(StockTransfer, self).default_get(fields)
        default_approval_required = self.env['ir.config_parameter'].sudo().get_param('transfer_approval_required',False)
        res['approval_required'] = default_approval_required
        return res

    def _get_location_domain(self):
        user = self.env.user.sudo()
        allowed_locations = user.location_ids.sudo()
        return [('id', 'in', allowed_locations.ids), ('usage', '=', 'internal')]

    @api.model_create_multi
    def create(self, vals_list):
        activity_type = self.env.ref('mail.mail_activity_data_todo')
        model_id = self.env['ir.model']._get_id('stock.transfer')
        transfers = self.env['stock.transfer']

        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                if 'company_id' in vals:
                    vals['name'] = self.env['ir.sequence'].with_context(with_company=vals['company_id']).next_by_code(
                        'stock.transfer') or _('New')
                else:
                    vals['name'] = self.env['ir.sequence'].next_by_code('stock.transfer') or _('New')
            res = super(StockTransfer, self.sudo()).create(vals)
            transfers += res

            res.message_subscribe([res.partner_id.id])

            if res.transfer_type in ['direct_transfer', 'transfer_with_transit']:
                users = self.env['res.users'].search([('restrict_locations', '=', True)])

                users_source = users.filtered(lambda u: res.location_id.id in u.stock_location_ids.ids and u.id != res.create_uid.id)

                users_destination = users.filtered(
                    lambda u: res.location_dest_id.id in u.stock_location_ids.ids and u.id != res.create_uid.id
                )

                message = _("A new transfer (%s) was created. You are in the source location.") % (res.name)
                message2 = _("A new transfer (%s) was created. You are in the destination location.") % (res.name)

                for user in users_source:
                    self.env['mail.activity'].sudo().create({
                        'res_id': res.id,
                        'res_model_id': model_id,
                        'activity_type_id': activity_type.id,
                        'summary': "Stock Transfer Notification",
                        'note': message,
                        'automated': True,
                        'user_id': user.id,
                        'chaining_type': 'suggest',
                    })

                for user in users_destination:
                    self.env['mail.activity'].sudo().create({
                        'res_id': res.id,
                        'res_model_id': model_id,
                        'activity_type_id': activity_type.id,
                        'summary': "Stock Transfer Notification",
                        'note': message2,
                        'automated': True,
                        'user_id': user.id,
                        'chaining_type': 'suggest',
                    })

        return transfers

    def write(self, vals):
        res = super(StockTransfer, self).write(vals)
        if self.partner_id.id not in self.message_partner_ids.ids:
            self.message_subscribe([self.partner_id.id])
        return res

    def unlink(self):
        for transfer in self:
            if transfer.picking_ids:
                raise UserError(_('You cannot delete a transfer. You must first delete the Dispatch Orders.'))
        return super(StockTransfer, self).unlink()

    @api.onchange('company_id')
    def onchange_company_id(self):
        self.picking_type_id = False
        self.location_id = False
        self.location_dest_id = False
        self.transit_location_id = False

    def create_picking(self, location_id, location_dest_id, main_picking=None, picking_type_id=False):
        Picking = self.env['stock.picking']
        Move = self.env['stock.move']
        if self.picking_type_id and picking_type_id:
            picking_vals = {
                'origin': self.name,
                'partner_id': self.partner_id.id,
                'date_done': fields.Datetime.now(),
                'picking_type_id': picking_type_id.id,
                'company_id': self.company_id.id,
                'move_type': 'direct',
                'note': self.note or "",
                'location_id': location_id.id,
                'location_dest_id': location_dest_id.id or "",
                'transfer_id': self.id,
                'picking_seq': self.picking_count + 1,
            }
            picking_id = Picking.create(picking_vals.copy())
            if not main_picking:
                print('not main picking ')
                for line in self.transfer_lines.filtered(
                        lambda l: l.product_id.type in ['product', 'consu'] and not float_is_zero(l.product_uom_qty,precision_rounding=l.product_id.uom_id.rounding)):
                    print('first move: ')

                    Move.create({
                        'name': line.name,
                        'product_uom': line.product_uom.id,
                        'picking_id': picking_id.id,
                        'picking_type_id': picking_type_id.id,
                        'product_id': line.product_id.id,
                        'product_uom_qty': abs(line.product_uom_qty),
                        'state': 'confirmed',
                        'location_id': location_id.id,
                        'location_dest_id': location_dest_id.id or "",
                        'company_id': self.company_id.id,
                        'picking_type_entire_packs': True,
                        'stock_valuation_layer_ids': False,
                    })
            else:
                print('else main picking ')
                for line in main_picking.move_ids.filtered(lambda l: l.product_id.type in ['product', 'consu'] and not float_is_zero(l.product_uom_qty,precision_rounding=l.product_id.uom_id.rounding)):
                    Move.create({
                        'name': line.name,
                        'product_uom': line.product_uom.id,
                        'picking_id': picking_id.id,
                        'picking_type_id': picking_type_id.id,
                        'product_id': line.product_id.id,
                        'product_uom_qty': abs(line.quantity),
                        'state': 'confirmed',
                        'location_id': location_id.id,
                        'location_dest_id': location_dest_id.id or "",
                        'company_id': self.company_id.id,
                        'package_level_id': self.current_package_level_id.id or False,
                        'stock_valuation_layer_ids': False,
                    })
        return True

    def generate_transfer(self):
        if not self.transfer_lines:
            raise UserError(_('Please create Detail lines'))
        picking_type_id = self.picking_type_id
        self.state = 'confirm'
        self.sudo().create_picking(self.location_id, self.transit_location_id, picking_type_id=picking_type_id)

    def seperate_moves_into_new_picking(self, location_dest_id, main_picking, picking_type_id=False):
        Picking = self.env['stock.picking']
        move = self.env['stock.move']
        print('location_dest_id : ', location_dest_id)
        print(' : ', )
        if self.picking_type_id and picking_type_id:
            picking_vals = {
                'origin': self.name,
                'partner_id': self.partner_id.id,
                'date_done': fields.Datetime.now(),
                'picking_type_id': picking_type_id.id,
                'company_id': self.company_id.id,
                'move_type': 'direct',
                'note': self.note or "",
                'location_id': self.transit_location_id.id,
                'location_dest_id': location_dest_id.id or "",
                'transfer_id': self.id,
                'picking_seq': self.picking_count + 1,
            }
            picking_id = Picking.create(picking_vals.copy())

            for line in main_picking.move_ids.filtered(lambda l: l.product_id.type in ['product', 'consu'] and not float_is_zero(l.product_uom_qty, precision_rounding=l.product_id.uom_id.rounding)):
                move.create({
                    'name': line.name,
                    'product_uom': line.product_uom.id,
                    'picking_id': picking_id.id,
                    'picking_type_id': picking_type_id.id,
                    'product_id': line.product_id.id,
                    'product_uom_qty': abs(line.product_uom_qty - line.quantity),
                    'state': 'confirmed',
                    'location_id': self.transit_location_id.id,
                    'location_dest_id': location_dest_id.id or "",
                    'company_id': self.company_id.id,
                    'picking_type_entire_packs': True,
                    'package_level_id': self.current_package_level_id.id or False,
                    'stock_valuation_layer_ids': False,
                })
        return True

    def create_picking_transit_to_source(self, main_picking, source_picking):
        Move = self.env['stock.move']
        picking_vals = {
            'origin': self.name,
            'partner_id': self.partner_id.id,
            'date_done': fields.Datetime.now(),
            'picking_type_id': self.picking_type_id.id,
            'company_id': self.company_id.id,
            'move_type': 'direct',
            'note': self.note or "",
            'location_id': main_picking.location_id.id,
            'location_dest_id': self.location_id.id or "",
            'transfer_id': self.id,
        }
        picking_id = self.env['stock.picking'].sudo().create(picking_vals.copy())
        for line in main_picking.move_ids.filtered(
                lambda l: l.product_id.type in ['product', 'consu'] and not float_is_zero(l.product_uom_qty,
                                                                                          precision_rounding=l.product_id.uom_id.rounding) and l.quantity > 0):
            source_picking_line = source_picking.move_ids.filtered(
                lambda sl: sl.product_id.id == line.product_id.id and sl.quantity > 0)
            Move.sudo().create({
                'name': line.name,
                'product_uom': line.product_uom.id,
                'picking_id': picking_id.id,
                'picking_type_id': self.picking_type_id.id,
                'product_id': line.product_id.id,
                'product_uom_qty': abs(source_picking_line.quantity - line.quantity),
                'state': 'confirmed',
                'location_id': main_picking.location_id.id,
                'location_dest_id': self.location_id.id or "",
                'company_id': self.company_id.id,
                'stock_valuation_layer_ids': False,
            })

    def action_view_pickings(self):
        pickings = self.mapped('picking_ids')
        action = self.env['ir.actions.act_window']._for_xml_id('stock.action_picking_tree_all')
        if len(pickings) > 1:
            action['domain'] = [('id', 'in', pickings.ids)]
        elif len(pickings) == 1:
            action['views'] = [(self.env.ref('stock.view_picking_form').id, 'form')]
            action['res_id'] = pickings.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def action_approve(self):
        self.is_approved = True
        self.user_id = self.env.uid
        return True

    def action_confirm(self):
        if not self.transfer_lines:
            raise UserError(_('Please create Detail lines.'))
        self.is_confirm = True

    def action_cancel(self):
        print('picking_ids: ', self.picking_ids)
        print('picking_ids: ', self.picking_ids.ids)
        print('approval_required: ', self.approval_required)
        print('state: ', self.state)
        self.state = 'cancel'
        self.is_cancel = True

# ----------------------------------------------------------------------------------------------------------------------------------------------
# kit product
    def action_open_kit_wizard(self):
        """Opens the wizard to select a kit product, BoM, and quantity."""
        return {
            'name': "Add Kit Product",
            'type': 'ir.actions.act_window',
            'res_model': 'stock.transfer.kit.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_transfer_id': self.id}
        }