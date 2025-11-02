from odoo import api, fields, models
from odoo.tools import float_is_zero, OrderedSet


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_in_move_lines(self):
        """ Returns the `stock.move.line` records of `self` considered as incoming. It is done thanks
        to the `_should_be_valued` method of their source and destionation location as well as their
        owner.

        :returns: a subset of `self` containing the incoming records
        :rtype: recordset
        """
        self.ensure_one()
        res = OrderedSet()
        for move_line in self.move_line_ids:
            if move_line.owner_id and move_line.owner_id != move_line.company_id.partner_id:
                continue
            if (not move_line.location_id._should_be_valued() and move_line.location_dest_id._should_be_valued()) or (
                    move_line.location_id._should_be_valued() and move_line.location_dest_id._should_be_valued()):
                res.add(move_line.id)
        return self.env['stock.move.line'].browse(res)
        

    #
    # @api.model
    # def _get_valued_types(self):
    #     """Returns a list of `valued_type` as strings. During `action_done`, we'll call
    #     `_is_[valued_type]'. If the result of this method is truthy, we'll consider the move to be
    #     valued.
    #     Adding Internal Transfer
    #
    #     :returns: a list of `valued_type`
    #     :rtype: list
    #     """
    #
    #     valued_types = super(StockMove, self)._get_valued_types()
    #     valued_types.append('internal')
    #     return valued_types
    #
    # def _get_internal_move_lines(self):
    #     """ Returns the `stock.move.line` records of `self` considered as internal_transfer. It is done thanks
    #     to the `_should_be_valued` method of their source and destionation location as well as their
    #     owner.
    #
    #     :returns: a subset of `self` containing the incoming records
    #     :rtype: recordset
    #     """
    #     self.ensure_one()
    #     res = OrderedSet()
    #     for move_line in self.move_line_ids:
    #         if move_line.owner_id and move_line.owner_id != move_line.company_id.partner_id:
    #             continue
    #         if move_line.location_id._should_be_valued() and move_line.location_dest_id._should_be_valued():
    #             res.add(move_line.id)
    #     return self.env['stock.move.line'].browse(res)
    #
    # def _is_internal(self):
    #     """Check if the move should be considered as entering the company so that the cost method
    #     will be able to apply the correct logic.
    #
    #     :returns: True if the move is entering the company else False
    #     :rtype: bool
    #     """
    #     self.ensure_one()
    #     if self._get_internal_move_lines():
    #         return True
    #     return False
    #
    # def _create_internal_svl(self, forced_quantity=None):
    #     """Create a `stock.valuation.layer` from `self`.
    #
    #     :param forced_quantity: under some circunstances, the quantity to value is different than
    #         the initial demand of the move (Default value = None)
    #     """
    #     svl_vals_list = self._get_internal_svl_vals(forced_quantity)
    #     return self.env['stock.valuation.layer'].sudo().create(svl_vals_list)
    #
    # def _get_internal_svl_vals(self, forced_quantity):
    #     svl_vals_list = []
    #     for move in self:
    #         move = move.with_company(move.company_id)
    #         valued_move_lines = move._get_internal_move_lines()
    #         valued_quantity = 0
    #         for valued_move_line in valued_move_lines:
    #             valued_quantity += valued_move_line.product_uom_id._compute_quantity(valued_move_line.qty_done,
    #                                                                                  move.product_id.uom_id)
    #         unit_cost = move.product_id.standard_price
    #         if move.product_id.cost_method != 'standard':
    #             unit_cost = abs(move._get_price_unit())  # May be negative (i.e. decrease an out move).
    #         if "OUT" in move.picking_id.name:
    #             svl_vals = move.product_id._prepare_out_svl_vals(forced_quantity or valued_quantity, move.company_id)
    #         else:
    #
    #             svl_vals = move.product_id._prepare_in_svl_vals(forced_quantity or valued_quantity, unit_cost)
    #         svl_vals.update(move._prepare_common_svl_vals())
    #         if forced_quantity:
    #             svl_vals[
    #                 'description'] = 'Correction of %s (modification of past move)' % move.picking_id.name or move.name
    #         svl_vals_list.append(svl_vals)
    #     return svl_vals_list
