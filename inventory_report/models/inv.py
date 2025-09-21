# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details

from odoo import _, api, fields, models
from odoo.tools.float_utils import float_is_zero
from odoo.osv import expression
from odoo.tools.misc import format_datetime


class StockReport(models.Model):
    _inherit = 'stock.quant'
    vendor = fields.Many2one('res.partner', string="Vendor", compute="_compute_get_vendor", store=True)
    pro_cost = fields.Float(string="Cost", compute="_compute_pro_cost", store=True)
    pro_price = fields.Float(string="Price", related="product_id.lst_price", store=True)
    value = fields.Monetary('Value', store=True, readonly=True, compute='_compute_value_2',
                            groups='inventory_report.group_stock_manager')
    currency_id = fields.Many2one('res.currency', compute='_compute_value_2',
                                  groups='inventory_report.group_stock_manager')
    accounting_date = fields.Date(
        'Accounting Date',
        help="Date at which the accounting entries will be created"
             " in case of automated inventory valuation."
             " If empty, the inventory date will be used.")

    @api.model
    def action_set_inventory_quantity_to_zero(self):
        for quant in self:
            quant.inventory_quantity = 0
            quant.inventory_quantity_set = False
        return True

    def action_inventory_at_date(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Inventory at Date and location',
            'res_model': 'stock.quantity.history',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_inventory_datetime': fields.Datetime.now(),
            },
        }

    @api.depends('product_id')
    def _compute_pro_cost(self):
        for record in self:
            if record.product_id:
                record.pro_cost = record.product_id.standard_price
            else:
                record.pro_cost = 0.0

    # dddddddddddddddddddddddddddddddddddddddddddd
    class ProductCategory2(models.Model):
        _inherit = 'product.category'

        property_cost_method = fields.Selection([
            ('standard', 'Standard Price'),
            ('fifo', 'First In First Out (FIFO)'),
            ('average', 'Average Cost (AVCO)')], string="Costing Method",
            company_dependent=True, copy=True, required=True,
            help="""Standard Price: The products are valued at their standard cost defined on the product.
            Average Cost (AVCO): The products are valued at weighted average cost.
            First In First Out (FIFO): The products are valued supposing those that enter the company first will also leave it first.
            """)

    @api.depends('company_id', 'location_id', 'owner_id', 'product_id', 'quantity')
    def _compute_value_2(self):
        """ For standard and AVCO valuation, compute the current accounting
        valuation of the quants by multiplying the quantity by
        the standard price. Instead for FIFO, use the quantity times the
        average cost (valuation layers are not manage by location so the
        average cost is the same for all location and the valuation field is
        a estimation more than a real value).
        """
        for quant in self:
            quant.currency_id = quant.company_id.currency_id
            # If the user didn't enter a location yet while enconding a quant.
            if not quant.location_id:
                quant.value = 0
                return

            if not quant.location_id._should_be_valued_2() or \
                    (quant.owner_id and quant.owner_id != quant.company_id.partner_id):
                quant.value = 0
                continue
            if quant.product_id.categ_id.property_cost_method == 'fifo':
                quantity = quant.product_id.with_company(quant.company_id).quantity_svl
                if float_is_zero(quantity, precision_rounding=quant.product_id.uom_id.rounding):
                    quant.value = 0.0
                    continue
                average_cost = quant.product_id.with_company(quant.company_id).value_svl / quantity
                quant.value = quant.quantity * average_cost
            else:
                quant.value = quant.quantity * quant.product_id.with_company(quant.company_id).standard_price

    @api.depends('product_id')
    def _compute_get_vendor(self):
        for rec in self:
            vendor = False
            if rec.product_id and rec.product_id.seller_ids:
                for seller_line in rec.product_id.seller_ids:
                    if seller_line.partner_id:
                        vendor = seller_line.partner_id.id
                        break  # stop at the first available vendor
            rec.vendor = vendor

    @api.model
    def _get_quants_action_2(self, domain=None, extend=False):
        """ Returns an action to open (non-inventory adjustment) quant view.
        Depending of the context (user have right to be inventory mode or not),
        the list view will be editable or readonly.

        :param domain: List for the domain, empty by default.
        :param extend: If True, enables form, graph and pivot views. False by default.
        """
        if not self.env['ir.config_parameter'].sudo().get_param('stock.skip_quant_tasks'):
            self._quant_tasks()
        ctx = dict(self.env.context or {})
        ctx['inventory_report_mode'] = True
        ctx.pop('group_by', None)
        action = {
            'name': _('Stock On Hand'),
            'view_mode': 'list,form',
            'res_model': 'stock.quant',
            'type': 'ir.actions.act_window',
            'context': ctx,
            'domain': domain or [],
            'help': """
                   <p class="o_view_nocontent_empty_folder">{}</p>
                   <p>{}</p>
                   """.format(_('No Stock On Hand'),
                              _('This analysis gives you an overview of the current stock level of your products.')),
        }

        target_action = self.env.ref('inventory_report.dashboard_open_quants_2', False)
        if target_action:
            action['id'] = target_action.id

        form_view = self.env.ref('inventory_report.view_stock_quant_form_editable_2').id
        if self.env.context.get('inventory_mode') and self.env.user.has_group('stock.group_stock_manager'):
            action['view_id'] = self.env.ref('inventory_report.view_stock_quant_list_editable_2').id
        else:
            action['view_id'] = self.env.ref('inventory_report.view_stock_quant_list_2').id
        action.update({
            'views': [
                (action['view_id'], 'list'),
                (form_view, 'form'),
            ],
        })
        if extend:
            action.update({
                'view_mode': 'list,form,pivot,graph',
                'views': [
                    (action['view_id'], 'list'),
                    (form_view, 'form'),
                    (self.env.ref('inventory_report.view_stock_quant_pivot_2').id, 'pivot'),
                    (self.env.ref('inventory_report.stock_quant_view_graph_2').id, 'graph'),
                ],
            })
        return action

    @api.model
    def action_view_quants_2(self):
        print("f")
        self = self.with_context(search_default_internal_loc=1)
        self = self._set_view_context()
        return self._get_quants_action_2(extend=True)


class ProductCategory2(models.Model):
    _inherit = 'product.category'

    property_cost_method = fields.Selection([
        ('standard', 'Standard Price'),
        ('fifo', 'First In First Out (FIFO)'),
        ('average', 'Average Cost (AVCO)')], string="Costing Method",
        company_dependent=True, copy=True, required=True,
        default='standard',
        help="""Standard Price: The products are valued at their standard cost defined on the product.
        Average Cost (AVCO): The products are valued at weighted average cost.
        First In First Out (FIFO): The products are valued supposing those that enter the company first will also leave it first.
        """)


class StockMoveReport(models.Model):
    _inherit = 'stock.move.line'
    vendor = fields.Many2one('res.partner', string="Vendor", compute="_compute_get_vendor", store=True)

    @api.depends('product_id')
    def _compute_get_vendor(self):
        for rec in self:
            # Directly use rec.product_id, no need to search again
            if rec.product_id.seller_ids:
                for seller_line in rec.product_id.seller_ids:
                    if seller_line.partner_id:
                        print("Vendor = ", seller_line.partner_id.name)
                        rec.vendor = seller_line.partner_id.id
                        break  # Stop at the first valid vendor
            else:
                rec.vendor = False


class StockLocationAdd(models.Model):
    _inherit = "stock.location"

    def _should_be_valued_2(self):
        """ This method returns a boolean reflecting whether the products stored in `self` should
        be considered when valuating the stock of a company.
        """
        self.ensure_one()
        if self.usage == 'internal' or (self.usage == 'transit' and self.company_id):
            return True
        return False


class StockQuantityHistory(models.TransientModel):
    _name = 'stock.quantity.history'
    _description = 'Stock Quantity History'

    inventory_datetime = fields.Datetime('Inventory at Date', default=fields.Datetime.now)

    def open_at_date(self):
        tree_view_id = self.env.ref('stock.view_stock_product_tree').id
        form_view_id = self.env.ref('stock.product_form_view_procurement_button').id

        inventory_date = self.inventory_datetime

        products = self.env['product.product'].search([('type', '=', 'consu')])
        context_at_date = dict(self.env.context, to_date=inventory_date)

        products_with_qty = products.with_context(context_at_date).filtered(lambda p: p.qty_available != 0)

        product_ids = products_with_qty.ids

        return {
            'type': 'ir.actions.act_window',
            'views': [(tree_view_id, 'list'), (form_view_id, 'form')],
            'view_mode': 'list,form',
            'name': _('Products'),
            'res_model': 'product.product',
            'domain': [('id', 'in', product_ids)],
            'context': context_at_date,
            'display_name': format_datetime(self.env, inventory_date)
        }

# class ProductProductAdd(models.Model):
#     _inherit = 'product.product'
#
#     total_value = fields.Float(
#         string='Total Value',
#         compute='_compute_total_value',
#         store=False
#     )
#
#     def _compute_total_value(self):
#         for product in self:
#                 product.total_value = product.standard_price * product.qty_available
#


class ProductProductAdd(models.Model):
    _inherit = 'product.product'

    total_value = fields.Float(
        string='Total Value',
        compute='_compute_total_value',
        store=False,
        readonly=True
    )

    @api.depends('qty_available', 'standard_price')
    def _compute_total_value(self):
        for product in self:
            if product.type == 'product':
                qty = product.qty_available or 0.0
                price = product.standard_price or 0.0
                product.total_value = qty * price
            else:
                product.total_value = 0.0

    # def _compute_total_value(self):
    #     for product in self.with_context({'location': False}):
    #         if product.type == 'product':
    #             qty = product.qty_available or 0.0
    #             price = product.standard_price or 0.0
    #             product.total_value = qty * price
    #         else:
    #             product.total_value = 0.0
