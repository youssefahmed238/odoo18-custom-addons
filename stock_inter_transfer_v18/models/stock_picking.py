# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero


class StockPicking(models.Model):
    _inherit = "stock.picking"

    transfer_id = fields.Many2one('stock.transfer', string="Internal transfer")
    picking_seq = fields.Integer(string="sequence")

    def button_validate(self):
        if self.transfer_id:
            transfer = self.transfer_id.sudo()
            if transfer.transfer_type == 'direct_transfer':
                return super(StockPicking, self).button_validate()

        if self.picking_type_id.code == 'internal':
            for product in self.move_ids_without_package:
                if product.quantity > product.product_uom_qty and not self.env.user.allow_done_exceeds_demand:
                    raise UserError(_('Quantity cannot be greater than Demand quantity.'))

        res = super(StockPicking, self).button_validate()
        if self.origin and self.state == 'done':
            if self.transfer_id:
                transfer = self.transfer_id.sudo()
                if self.location_dest_id != transfer.location_dest_id and self.location_dest_id != transfer.location_id:
                    picking_type = self.env['stock.picking.type'].sudo().search(
                        [('code', '=', 'internal'),
                         ('default_location_src_id', '=', transfer.location_dest_id.id)], limit=1)
                    transfer.create_picking(self.location_dest_id, transfer.location_dest_id, main_picking=self, picking_type_id=picking_type)
        return res

    def sh_cancel(self):
        if self.transfer_id:
            transfer = self.transfer_id.sudo()
            Move = self.env['stock.move']
            Picking = self.env['stock.picking']
            picking_vals = {
                'origin': transfer.name,
                'partner_id': transfer.partner_id.id,
                'date_done': fields.Datetime.now(),
                'picking_type_id': self.picking_type_id.id,
                'company_id': transfer.company_id.id,
                'move_type': 'direct',
                'note': transfer.note or "",
                'location_id': self.location_dest_id.id,
                'location_dest_id': self.location_id.id or "",
                'transfer_id': transfer.id,
                'picking_seq': transfer.picking_count + 1,
            }
            picking_id = Picking.create(picking_vals.copy())
            for line in self.move_ids.filtered(
                    lambda l: l.product_id.type in ['product', 'consu'] and not float_is_zero(l.product_uom_qty,
                                                                                              precision_rounding=l.product_id.uom_id.rounding)):
                line.quantity = 0.0
                Move.create({
                    'name': line.name,
                    'product_uom': line.product_uom.id,
                    'picking_id': picking_id.id,
                    'picking_type_id': picking_id.picking_type_id.id,
                    'product_id': line.product_id.id,
                    'product_uom_qty': abs(line.product_uom_qty),
                    'state': 'confirmed',
                    'location_id': picking_id.location_id.id,
                    'location_dest_id': picking_id.location_dest_id.id or "",
                    'company_id': picking_id.company_id.id,
                    'package_level_id': transfer.current_package_level_id.id or False,
                    'stock_valuation_layer_ids': False,
                })

        return super(StockPicking, self).sh_cancel()

class StockLocation(models.Model):
    _inherit = "stock.location"

    @api.model
    def _name_search(self, name, domain=None, operator='ilike', limit=100, order=None):
        domain = domain or []
        context = dict(self.env.context or {})
        if context.get('check_source_location'):
            picking_type_id = self.env['stock.picking.type'].browse(context['check_source_location'])
            domain.append(('id', 'in', self.search([]).filtered(
                lambda l: l.warehouse_id and l.warehouse_id.id == picking_type_id.warehouse_id.id).ids))
        return super(StockLocation, self)._name_search(name=name, domain=domain, operator=operator, limit=limit, order=order)
