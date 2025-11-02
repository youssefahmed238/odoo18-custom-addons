from odoo.tools import float_is_zero
from odoo import api, fields, models

class StockBackorderConfirmationInherit(models.TransientModel):
    _inherit = 'stock.backorder.confirmation'

    def process_cancel_backorder2(self):
        print('Checking for No Backorder condition...')
        res = super(StockBackorderConfirmationInherit, self).process_cancel_backorder()

        pickings_to_validate_ids = self.env.context.get('button_validate_picking_ids')
        if not pickings_to_validate_ids:
            return res

        pickings_to_validate = self.env['stock.picking'].sudo().browse(pickings_to_validate_ids)

        if pickings_to_validate.origin:
            sale_order = self.env['sale.order'].sudo().search([('name', '=', pickings_to_validate.origin)], limit=1)
            if sale_order and not sale_order.picking_policy == 'backorder':
                print('No backorder from Sales Order, calling super only.')
                return res

        if pickings_to_validate.transfer_id.location_id != pickings_to_validate.location_id:
            if any(line.product_uom_qty > line.quantity for line in pickings_to_validate.move_ids):
                print('pickings_to_validate: ', pickings_to_validate)
                Move = self.env['stock.move'].sudo()
                Picking = self.env['stock.picking'].sudo()
                picking_type = self.env['stock.picking.type'].sudo().search([
                    ('code', '=', 'internal'),
                    ('warehouse_id', '=', pickings_to_validate.transfer_id.location_id.warehouse_id.id)
                ], limit=1)

                picking_vals = {
                    'origin': pickings_to_validate.transfer_id.name,
                    'partner_id': pickings_to_validate.transfer_id.partner_id.id,
                    'date_done': fields.Datetime.now(),
                    'picking_type_id': picking_type.id if picking_type else pickings_to_validate.picking_type_id.id,
                    'company_id': pickings_to_validate.transfer_id.company_id.id,
                    'move_type': 'direct',
                    'note': pickings_to_validate.transfer_id.note or "",
                    'location_id': pickings_to_validate.location_id.id or "",
                    'location_dest_id': pickings_to_validate.transfer_id.location_id.id if pickings_to_validate.transfer_id.location_id else pickings_to_validate.location_dest_id.id,
                    'transfer_id': pickings_to_validate.transfer_id.id,
                    'picking_seq': pickings_to_validate.transfer_id.picking_count + 1,
                }
                picking_id = Picking.create(picking_vals.copy())

                for line in pickings_to_validate.move_ids.filtered(lambda l: l.product_id.type in ['product', 'consu'] and not float_is_zero(l.product_uom_qty, precision_rounding=l.product_id.uom_id.rounding)):
                    if line.product_uom_qty > line.quantity:
                        Move.create({
                            'name': line.name,
                            'product_uom': line.product_uom.id,
                            'picking_id': picking_id.id,
                            'picking_type_id': picking_type.id if picking_type else pickings_to_validate.picking_type_id.id,
                            'product_id': line.product_id.id,
                            'product_uom_qty': abs(line.product_uom_qty - line.quantity),
                            'state': 'confirmed',
                            'location_id': picking_id.location_id.id or "",
                            'location_dest_id': picking_id.location_dest_id.id or "",
                            'company_id': picking_id.company_id.id,
                            'package_level_id': pickings_to_validate.transfer_id.current_package_level_id.id or False,
                            'stock_valuation_layer_ids': False,
                        })

        if pickings_to_validate.origin:
            if pickings_to_validate.transfer_id:
                transfer = pickings_to_validate.transfer_id.sudo()
                if transfer.picking_count == 2 and pickings_to_validate.picking_seq == 2:
                    new_moves = self.env['stock.move'].sudo().search(['&', ('id', 'in', pickings_to_validate.move_ids_without_package.ids), ('quantity', '=', 0)])
                    transfer.second_dispatch_done = True

        return res
