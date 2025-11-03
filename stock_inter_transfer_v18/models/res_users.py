# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ResConfigSettings(models.Model):
    _inherit = "res.users"

    allow_done_exceeds_demand = fields.Boolean("Inter transfer: Allow Done quantity to be more than Demand?")

    use_locations = fields.Boolean(string="Use Locations")
    location_ids = fields.Many2many('stock.location', "Locations")

    @api.onchange('use_locations')
    def _onchange_use_locations(self):
        if not self.use_locations:
            self.location_ids = [(5, 0, 0)]

    @api.constrains('use_locations', 'location_ids')
    def _check_location_ids_required(self):
        for user in self:
            if user.use_locations and not user.location_ids:
                raise ValidationError(_("You must select at least one Location when 'Use Locations' is enabled."))


class StockLocation(models.Model):
    _inherit = "stock.location"

    user_ids = fields.Many2many(
        'res.users',
        string="Users",
        relation='stock_location_user_rel',
        column1='location_id',
        column2='user_id'
    )
