from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError

class StockTransferLine(models.Model):
    _name = "stock.transfer.line"
    _description = "Detail of Internal Transfers"

    name = fields.Char('Description', index=True, required=True)
    product_id = fields.Many2one('product.product', string="Product", domain="[('type', 'in', ['product', 'consu'])]")
    transfer_id = fields.Many2one('stock.transfer', string="Transfer ID")
    product_uom_qty = fields.Float(string="Cantidad", required=True, default=1.0)
    product_uom = fields.Many2one('uom.uom', 'UOM', required=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id, index=True, required=True, tracking=True)

    _sql_constraints = [
        ('check_qty', 'CHECK(product_uom_qty > 0.0)', 'Quantity must be greater than 0.'),
    ]

    @api.constrains('product_uom')
    def _check_uom(self):
        transfer_error = self.filtered(
            lambda transfer: transfer.product_id.uom_id.category_id != transfer.product_uom.category_id)
        if transfer_error:
            user_warning = _(
                'You cannot make the transfer because the unit of measure has a different category than the unit of measure of the product.')
            for transfer in transfer_error:
                user_warning += _('\n\n%s --> Product UoM is %s (%s) - Transfer UoM is %s (%s)') % (
                    transfer.product_id.display_name, transfer.product_id.uom_id.name,
                    transfer.product_id.uom_id.category_id.name, transfer.product_uom.name,
                    transfer.product_uom.category_id.name)
            user_warning += _('\n\nBlocking: %s') % ' ,'.join(transfer_error.mapped('name'))
            raise UserError(user_warning)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        """Automatically set the default packaging and UoM when a product is selected."""
        if self.product_id:
            product = self.product_id.with_context(lang=self.env.user.lang)
            self.name = product.partner_ref
            self.product_uom = product.uom_id.id
            # Compute and set the default packaging
            self._compute_product_packaging_id()

            return {
                'domain': {
                    'product_uom': [('category_id', '=', product.uom_id.category_id.id)],
                    'product_packaging_id': [('product_id', '=', product.id)],
                }
            }

    # ----------------------------------------------------------------------------------------------------------------------------------------------
    price_unit = fields.Float(string="Unit Price", required=True, default=0.0)
    product_packaging_id = fields.Many2one(
        comodel_name='product.packaging',
        string="Packaging",
        compute='_compute_product_packaging_id',
        store=True, readonly=False, precompute=True,
        domain="[('sales', '=', True), ('product_id', '=', product_id)]",
        check_company=True
    )

    product_packaging_qty = fields.Float(
        string="Packaging Quantity",
        compute='_compute_product_packaging_qty',
        store=True, readonly=False, precompute=True
    )

    @api.depends('product_id')
    def _compute_product_packaging_id(self):
        """Automatically select default packaging for the product if available."""
        for line in self:
            if line.product_id and not line.product_packaging_id:
                packaging = self.env['product.packaging'].search(
                    [('product_id', '=', line.product_id.id), ('sales', '=', True)], limit=1
                )
                line.product_packaging_id = packaging.id if packaging else False

    @api.depends('product_packaging_id', 'product_uom_qty')
    def _compute_product_packaging_qty(self):
        """Compute how many full packaging units are needed based on product quantity."""
        for line in self:
            if line.product_packaging_id and line.product_packaging_id.qty > 0:
                line.product_packaging_qty = line.product_uom_qty / line.product_packaging_id.qty
            else:
                line.product_packaging_qty = 1.0
        transfer = self.env['stock.transfer'].browse(self.env.context.get('order_id'))
        return transfer.action_add_from_catalog()

    def action_add_from_catalog(self):
        transfer = self.env['stock.transfer'].browse(self.env.context.get('order_id'))
        return transfer.action_add_from_catalog()

    def _get_product_catalog_lines_data(self, **kwargs):
        if len(self) == 1:
            return {
                'quantity': self.product_uom_qty,
                'price': self.price_unit or 0.0,
            }
        elif self:
            self.product_id.ensure_one()
            order_line = self[0]
            order = order_line.transfer_id
            return {
                'readOnly': True,
                'price': order.pricelist_id._get_product_price(
                    product=order_line.product_id,
                    quantity=1.0,
                    currency=order.currency_id,
                    date=order.date_order,
                    **kwargs,
                ) or 0.0,
                'quantity': sum(
                    self.mapped(
                        lambda line: line.product_uom._compute_quantity(
                            qty=line.product_uom_qty,
                            to_unit=line.product_id.uom_id,
                        )
                    )
                ),
            }
        else:
            return {
                'quantity': 0,
                'price': 0.0,
            }
#-----------------------------------------------------------------------------------------------------------------------------------------
#forecast widget:

    virtual_available_at_date = fields.Float(compute='_compute_qty_at_date', digits='Product Unit of Measure')
    scheduled_date = fields.Datetime(compute='_compute_qty_at_date')
    forecast_expected_date = fields.Datetime(compute='_compute_qty_at_date')
    free_qty_today = fields.Float(compute='_compute_qty_at_date', digits='Product Unit of Measure')
    qty_available_today = fields.Float(compute='_compute_qty_at_date')
    # warehouse_id = fields.Many2one(related='order_id.warehouse_id')
    qty_to_deliver = fields.Float(compute='_compute_qty_to_deliver', digits='Product Unit of Measure')
    is_mto = fields.Boolean(compute='_compute_is_mto')
    display_qty_widget = fields.Boolean(compute='_compute_qty_to_deliver')

    warehouse_id = fields.Many2one(
        'stock.warehouse', string='Warehouse', required=True,
        compute='_compute_warehouse_id', store=True, readonly=False, precompute=True,
        check_company=True)

    @api.depends('transfer_id.user_id', 'transfer_id.company_id')
    def _compute_warehouse_id(self):
        for order in self:
            order.warehouse_id = order.transfer_id.user_id.with_company(order.transfer_id.company_id.id)._get_default_warehouse_id()

    def _compute_qty_at_date(self):
        for line in self:
            line.virtual_available_at_date = 1
            line.scheduled_date = fields.datetime.today()
            line.forecast_expected_date = fields.datetime.today()
            line.free_qty_today = 4
            line.qty_available_today = 5

    @api.depends('product_uom_qty', 'product_uom')
    def _compute_qty_to_deliver(self):
        """Compute the visibility of the inventory widget."""
        for line in self:
            line.qty_to_deliver = line.product_uom_qty
            if line.product_uom and line.qty_to_deliver > 0:
                line.display_qty_widget = True
            else:
                line.display_qty_widget = False

    @api.depends('product_id', 'warehouse_id', 'product_id.route_ids')
    def _compute_is_mto(self):
        """ Verify the route of the product based on the warehouse
            set 'is_available' at True if the product availability in stock does
            not need to be verified, which is the case in MTO, Cross-Dock or Drop-Shipping
        """
        self.is_mto = False
        for line in self:
            if not line.display_qty_widget:
                continue
            product = line.product_id
            product_routes = (product.route_ids + product.categ_id.total_route_ids)

            # Check MTO
            mto_route = line.warehouse_id.mto_pull_id.route_id
            if not mto_route:
                try:
                    mto_route = self.env['stock.warehouse']._find_global_route('stock.route_warehouse0_mto', _('Replenish on Order (MTO)'))
                except UserError:
                    # if route MTO not found in ir_model_data, we treat the product as in MTS
                    pass

            if mto_route and mto_route in product_routes:
                line.is_mto = True
            else:
                line.is_mto = False

# ----------------------------------------------------------------------------------------------------------------------------------------------
@api.onchange('product_id')
def _onchange_check_product_bom(self):
    """Automatically replace kit products with their components instead of raising an error"""
    for line in self:
        bom = self.env['mrp.bom'].sudo().search([
            ('product_id', '=', line.product_id.product_id.id),
            ('type', '=', 'phantom')
        ], limit=1)

        if bom:
            self.transfer_lines = [(5, 0, 0)]

            component_lines = []
            for component in bom.bom_line_ids:
                component_lines.append((0, 0, {
                    'product_id': component.product_id.id,
                    'product_uom_qty': component.product_qty,
                    'product_uom': component.product_uom_id.id,
                    'name': component.product_id.display_name,
                }))

            self.transfer_lines = component_lines

            return {
                'warning': {
                    'title': _("Kit Product Auto-Converted"),
                    'message': _("The selected product is a Kit and has been replaced with its components."),
                }
            }
