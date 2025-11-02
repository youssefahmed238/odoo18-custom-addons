# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ProductRequest(models.Model):
    _name = "product.request"
    _rec_name = "order_number"

    order_number = fields.Char(string="Order Number", readonly=True, copy=False)
    created_by = fields.Many2one('res.users', string="Created By", default=lambda self: self.env.user, readonly=True)
    order_date = fields.Datetime(string="Order Date", default=fields.Datetime.now)
    source = fields.Many2one('stock.location', "Source", domain="[('usage', '=', 'internal')]")
    destination = fields.Many2one('stock.location', "Destination", domain="[('usage', '=', 'internal')]")
    line_ids = (fields.One2many('product.request.line', 'request_id', string="Details"))
    accessible_to_user = fields.Boolean(string="Accessible to User", compute="_compute_accessible_to_user", store=False)

    state = fields.Selection([
        ('to_submit', 'To Submit'),
        ('submitted', 'Submitted'),
        ('rejected', 'rejected'),
        ('approved', 'approved'),
    ], string="Status", default='to_submit', tracking=True)

    user_use_locations = fields.Boolean(
        string="User Use Locations",
        compute="_compute_user_use_locations",
        store=False
    )

    @api.depends('state')
    def _compute_user_use_locations(self):
        for record in self:
            record.user_use_locations = self.env.user.use_locations

    @api.depends('source', 'destination')
    def _compute_accessible_to_user(self):
        for record in self:
            user_locations = self.env.user.location_ids
            record.accessible_to_user = (
                    record.source in user_locations or record.destination in user_locations
            )

    def action_submitted(self):
        self.state = 'submitted'

    def action_rejected(self):
        self.state = 'rejected'

    def action_approved(self):
        self.state = 'approved'

    @api.model
    def create(self, vals):
        if not vals.get('order_number'):
            vals['order_number'] = self.env['ir.sequence'].next_by_code('product.request') or _('New')
        return super(ProductRequest, self).create(vals)


class ProductRequestLine(models.Model):
    _name = "product.request.line"

    request_id = fields.Many2one('product.request', string="Request Reference", ondelete='cascade')
    product_id = fields.Many2one('product.product', string="Product", required=True)
    product_uom_qty = fields.Float(string="Quantity", required=True)
    product_uom = fields.Many2one(
        'uom.uom',
        string="Unit of Measure",
        required=True,
        domain="[('id', 'in', available_uom_ids)]",
    )
    available_uom_ids = fields.Many2many(
        'uom.uom',
        compute="_compute_available_uom_ids",
        store=False,
    )

    @api.depends('product_id')
    def _compute_available_uom_ids(self):
        for line in self:
            if line.product_id:
                # Get all UOMs related to the selected product
                line.available_uom_ids = line.product_id.uom_id | line.product_id.uom_po_id | line.product_id.uom_id.category_id.uom_ids
            else:
                # If no product is selected, no UOMs are available
                line.available_uom_ids = self.env['uom.uom']

    @api.onchange('product_id')
    def onchange_product_id(self):
        for line in self:
            if line.product_id:
                product = line.product_id.with_context(lang=self.env.user.lang)
                # Set the default UOM to the product's UOM
                line.product_uom = product.uom_id.id
