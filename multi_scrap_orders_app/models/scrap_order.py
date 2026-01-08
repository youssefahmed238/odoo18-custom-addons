# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare


class StockScrapOrders(models.Model):
    _name = 'stock.scrap.orders'
    _order = 'id desc'
    _description = "Multi Stock Scrap Orders"

    def _get_default_scrap_location_id(self):
        return self.env['stock.location'].search(
            [('scrap_location', '=', True), ('company_id', 'in', [self.env.user.company_id.id, False])], limit=1).id

    name = fields.Char(
        'Reference', default=lambda self: _('New'),
        copy=False, readonly=True, required=True,
        states={'done': [('readonly', True)]})
    origin = fields.Char(string='Source Document', states={'done': [('readonly', True)]})
    scrap_line_ids = fields.One2many('stock.scrap.orders.line', 'scrap_order_id', 'Operations',
                                     states={'done': [('readonly', True)]})
    scrap_location_id = fields.Many2one(
        'stock.location', 'Scrap Location', default=_get_default_scrap_location_id,
        domain="[('scrap_location', '=', True)]", required=True, states={'done': [('readonly', True)]})
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done')], string='Status', default="draft")
    date_expected = fields.Datetime('Expected Date', default=fields.Datetime.now, states={'done': [('readonly', True)]})
    picking_id = fields.Many2one('stock.picking', 'Picking', states={'done': [('readonly', True)]})
    company_id = fields.Many2one('res.company', string='Company', index=True,
                                 default=lambda self: self.env.user.company_id)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            if 'company_id' in vals:
                vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code(
                    'multi.stock.scrap') or _('New')
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code('multi.stock.scrap') or _('New')
        scrap = super(StockScrapOrders, self).create(vals)
        return scrap

    def unlink(self):
        if 'done' in self.mapped('state'):
            raise UserError(_('You cannot delete a scrap which is done.'))
        return super(StockScrapOrders, self).unlink()

    def action_get_stock_picking(self):
        action = self.env.ref('stock.action_picking_tree_all').read([])[0]
        action['domain'] = [('id', '=', self.picking_id.id)]
        return action

    def action_get_stock_move_lines(self):
        action = self.env.ref('stock.stock_move_line_action').read([])[0]
        scrap_line_ids = self.scrap_line_ids.mapped('move_id')
        action['domain'] = [('move_id', 'in', scrap_line_ids.ids)]
        return action

    def action_validate(self):
        for record in self:
            for line in record.scrap_line_ids:
                if line.product_id.type != 'product':
                    line.do_scrap()
                    continue

                precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
                available_qty = sum(self.env['stock.quant']._gather(line.product_id,
                                                                    line.location_id,
                                                                    line.lot_id or None,
                                                                    line.package_id or None,
                                                                    line.owner_id or None,
                                                                    strict=True).mapped('quantity'))
                scrap_qty = line.product_uom_id._compute_quantity(line.scrap_qty, line.product_id.uom_id)
                if float_compare(available_qty, scrap_qty, precision_digits=precision) >= 0:
                    line.do_scrap()
                else:
                    variant = line.product_id.product_template_attribute_value_ids._get_combination_name()
                    name = variant and "%s (%s)" % (line.product_id.name, variant) or line.product_id.name
                    raise UserError(
                        _('You plan to transfer %s %s of %s but you only have %s %s available stock in %s location.') % \
                        (scrap_qty, line.product_uom_id.name, name, available_qty, line.product_id.uom_id.name,
                         line.location_id.display_name))
            if all(line.state == 'done' for line in record.scrap_line_ids):
                record.write({'state': 'done'})


class StockScrapOrdersLine(models.Model):
    _name = 'stock.scrap.orders.line'
    _description = "Multi Stock Scrap Orders Line"

    def _get_default_location_id(self):
        company_user = self.env.user.company_id
        warehouse = self.env['stock.warehouse'].search([('company_id', '=', company_user.id)], limit=1)
        if warehouse:
            return warehouse.lot_stock_id.id
        return None

    scrap_order_id = fields.Many2one('stock.scrap.orders', 'Scrap Order')
    product_id = fields.Many2one('product.product', 'Product', required=True)
    product_uom_id = fields.Many2one('uom.uom', 'Unit of Measure', required=True)
    owner_id = fields.Many2one('res.partner', 'Owner')
    tracking = fields.Selection([
        ('serial', 'By Unique Serial Number'),
        ('lot', 'By Lots'),
        ('none', 'No Tracking')], string="Tracking",
        help="Ensure the traceability of a storable product in your warehouse.", default='none')
    lot_id = fields.Many2one('stock.lot', 'Lot', domain="[('product_id', '=', product_id)]")
    package_id = fields.Many2one('stock.quant.package', 'Package')
    location_id = fields.Many2one(
        'stock.location', 'Location', domain="[('usage', '=', 'internal')]",
        required=True, default=_get_default_location_id)
    scrap_qty = fields.Float('Quantity', default=1.0, required=True)
    move_id = fields.Many2one('stock.move', 'Scrap Move', readonly=True)
    state = fields.Selection(related='move_id.state', store=True)
    company_id = fields.Many2one('res.company', string='Company', index=True,
                                 default=lambda self: self.env.user.company_id)

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.product_uom_id = self.product_id.uom_id.id
            self.tracking = self.product_id.tracking

    def _prepare_move_values(self):
        return {
            'name': self.scrap_order_id.name,
            'origin': self.scrap_order_id.origin or self.scrap_order_id.name,
            'product_id': self.product_id.id,
            'product_uom': self.product_uom_id.id,
            'product_uom_qty': self.scrap_qty,
            'location_id': self.location_id.id,
            'scrapped': True,
            'state': 'done',
            'location_dest_id': self.scrap_order_id.scrap_location_id.id,
            'move_line_ids': [(0, 0, {'product_id': self.product_id.id,
                                      'product_uom_id': self.product_uom_id.id,
                                      'quantity': self.scrap_qty,
                                      'location_id': self.location_id.id,
                                      'location_dest_id': self.scrap_order_id.scrap_location_id.id,
                                      'package_id': self.package_id.id,
                                      'owner_id': self.owner_id.id,
                                      'state': 'done',
                                      'lot_id': self.lot_id.id, })],
        }

    def do_scrap(self):
        for scrap in self:
            move = self.env['stock.move'].create(scrap._prepare_move_values())
            # master: replace context by cancel_backorder
            move.with_context(is_scrap=True)._action_done()
            print(self.scrap_qty)
            stock_quant_ids = self.env['stock.quant'].search(
                [('product_id', '=', self.product_id.id), ('location_id', '=', self.location_id.id)])
            stock_quant_ids.reserved_quantity = stock_quant_ids.reserved_quantity - self.scrap_qty
            scrap.write({'move_id': move.id})
        return True
