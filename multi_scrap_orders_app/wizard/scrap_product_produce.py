# -*- coding: utf-8 -*-

from collections import Counter
from datetime import datetime

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_round

class MultiScrapProductProduce(models.TransientModel):
    _name = "multi.scrap.product.produce"
    _description = "Multi Scrap Product"

    def _get_default_location_id(self):
        company_user = self.env.user.company_id
        warehouse = self.env['stock.warehouse'].search([('company_id', '=', company_user.id)], limit=1)
        if warehouse:
            return warehouse.lot_stock_id.id
        return None

    @api.model
    def default_get(self, fields):
        res = super(MultiScrapProductProduce, self).default_get(fields)
        if self._context and self._context.get('active_id'):
            picking = self.env['stock.picking'].browse(self._context['active_id'])
            if 'produce_line_ids' in fields:
                lines = []
                for line in picking.move_ids:
                    location_id = self._get_default_location_id()
                    lines.append({
                        'product_id': line.product_id.id,
                        'product_uom_id': line.product_uom.id,
                        'scrap_qty': 0.0,
                        'location_id': location_id,
                        'qty_to_consume': line.quantity,
                        'tracking': line.product_id.tracking
                    })
                res['produce_line_ids'] = [(0, 0, x) for x in lines]
        return res

    def _get_default_scrap_location_id(self):
        return self.env['stock.location'].search([('scrap_location', '=', True), ('company_id', 'in', [self.env.user.company_id.id, False])], limit=1).id

    scrap_location_id = fields.Many2one(
        'stock.location', 'Scrap Location', default=_get_default_scrap_location_id,
        domain="[('scrap_location', '=', True)]", required=True)
    date_expected = fields.Datetime('Expected Date', default=fields.Datetime.now)
    produce_line_ids = fields.One2many('multi.scrap.product.produce.line', 'product_produce_id', string='Product to Track')


    def do_produce(self):
        scrap_order = self.env['stock.scrap.orders']
        picking = self.env['stock.picking'].browse(self._context['active_id'])
        for record in self:
            lines = []
            for line in record.produce_line_ids:
                lines.append({
                    'product_id': line.product_id.id or False,
                    'product_uom_id': line.product_uom_id.id or False,
                    'scrap_qty': line.scrap_qty,
                    'location_id': line.location_id.id or False,
                    'owner_id': line.owner_id.id or False,
                    'lot_id': line.lot_id.id or False,
                    'package_id': line.package_id.id or False,
                })
            scrap_order_id = \
                scrap_order.create({
                    'scrap_line_ids': [(0, 0, x) for x in lines],
                    'scrap_location_id':  record.scrap_location_id.id,
                    'date_expected'    :  record.date_expected,
                    'origin': picking.name,
                    'picking_id': picking.id,
                    'name': 'New',
                    'state': 'draft'
                })
            scrap_order_id.action_validate()
        return {'type': 'ir.actions.act_window_close'}



class MrpProductProduceLine(models.TransientModel):
    _name = "multi.scrap.product.produce.line"
    _description = "Record Multi Scrap Line"

    def _get_default_location_id(self):
        company_user = self.env.user.company_id
        warehouse = self.env['stock.warehouse'].search([('company_id', '=', company_user.id)], limit=1)
        if warehouse:
            return warehouse.lot_stock_id.id
        return None

    product_produce_id = fields.Many2one('multi.scrap.product.produce')
    product_id = fields.Many2one('product.product', 'Product',required=True)
    product_uom_id = fields.Many2one('uom.uom', 'Unit of Measure',required=True)
    owner_id = fields.Many2one('res.partner', 'Owner')
    tracking = fields.Selection([
        ('serial', 'By Unique Serial Number'),
        ('lot', 'By Lots'),
        ('none', 'No Tracking')], string="Tracking", help="Ensure the traceability of a storable product in your warehouse.", default='none')
    lot_id = fields.Many2one('stock.lot', 'Lot',domain="[('product_id', '=', product_id)]")
    package_id = fields.Many2one('stock.quant.package', 'Package')
    location_id = fields.Many2one(
        'stock.location', 'Location', domain="[('usage', '=', 'internal')]",
        required=True, default=_get_default_location_id)
    scrap_qty = fields.Float('Quantity', default=1.0, required=True)
    qty_to_consume = fields.Float('To Consume', digits=dp.get_precision('Product Unit of Measure'))
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.user.company_id)

    @api.onchange('lot_id')
    def _onchange_lot_id(self):
        """ When the user is encoding a produce line for a tracked product, we apply some logic to
        help him. This onchange will automatically switch `qty_done` to 1.0.
        """
        res = {}
        if self.product_id.tracking == 'serial':
            self.qty_to_consume = 1
        return res

    @api.onchange('product_id')
    def _onchange_product_id(self):
        print('self.product_id.uom_id======',self.product_id.uom_id)
        self.product_uom_id = self.product_id.uom_id.id
        self.tracking = self.product_id.tracking
