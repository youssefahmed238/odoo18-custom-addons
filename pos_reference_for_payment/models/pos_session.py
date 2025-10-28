# -*- coding: utf-8 -*-
################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Bhagyadev KP (odoo@cybrosys.com)
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
################################################################################
from odoo import models, fields, api


class PosSessionLoadFields(models.Model):
    """Inherited model pos session for loading field in pos payment into
       pos session.
        Methods:
            _compute_is_allow_payment_ref: Compute method to get the config param boolean.
            _load_pos_data_fields: Load additional fields into POS session data.
    """
    _inherit = 'pos.session'

    is_allow_payment_ref = fields.Boolean(string="Allow Payment Reference",
                                          compute='_compute_is_allow_payment_ref',
                                          store=False)

    @api.depends_context('uid')
    def _compute_is_allow_payment_ref(self):
        value = self.env['ir.config_parameter'].sudo().get_param('pos_reference_for_payment.is_allow_payment_ref',
                                                                 default=False)
        for rec in self:
            rec.is_allow_payment_ref = value == 'True'

    @api.model
    def _load_pos_data_fields(self, config_id):
        """Load additional fields into POS session data."""
        result = super(PosSessionLoadFields, self)._load_pos_data_fields(config_id)

        # Load payment reference configuration
        result.extend({'is_allow_payment_ref'})

        return result
