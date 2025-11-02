from odoo import models, fields, api
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class StockTransferKitWizard(models.TransientModel):
    _name = 'stock.transfer.kit.wizard'
    _description = "Stock Transfer Kit Wizard"

    transfer_id = fields.Many2one('stock.transfer', string="Stock Transfer", required=True)
    kit_product_id = fields.Many2one(
        'product.product', string="Kit Product", required=True,
    )
    kit_product_tmpl_id = fields.Many2one(
        'product.template', string="Kit Product Template", compute="_compute_kit_product_tmpl_id", store=True
    )
    bom_id = fields.Many2one(
        'mrp.bom', string="Bill of Materials", required=True
    )
    bom_domain_ids = fields.Many2many('mrp.bom', compute="_compute_bom_domain", store=False)
    kit_quantity = fields.Float(string="Kit Quantity", required=True, default=1)

    @api.depends('kit_product_id')
    def _compute_kit_product_tmpl_id(self):
        """ Compute the related product template. """
        for wizard in self:
            wizard.kit_product_tmpl_id = wizard.kit_product_id.product_tmpl_id if wizard.kit_product_id else False

    @api.depends('kit_product_id')
    def _compute_bom_domain(self):
        for wizard in self:
            # Ensure the kit_product_id is valid
            if not wizard.kit_product_id:
                raise UserError("Kit product ID is not set.")

            _logger.info(f"Available models: {self.env.registry.models}")

            wizard.bom_id = False
            domain_boms = self.env['mrp.bom']

            if wizard.kit_product_id:
                domain_boms = self.env['mrp.bom'].sudo().search([
                    ('product_id', '=', wizard.kit_product_id.id)
                ])

                if not domain_boms:
                    domain_boms = self.env['mrp.bom'].sudo().search([
                        ('product_tmpl_id', '=', wizard.kit_product_id.product_tmpl_id.id)
                    ])

                if domain_boms:
                    wizard.bom_id = domain_boms[0].id
            wizard.bom_domain_ids = domain_boms

    @api.onchange('kit_product_id')
    def _onchange_kit_product_id(self):
        self._compute_bom_domain()

    def action_add_kit_to_transfer(self):
        """Add BOM components to the transfer lines and validate stock availability without duplication."""
        self.ensure_one()

        if not self.bom_id:
            raise UserError("Please select a Bill of Materials.")

        if self.kit_quantity <= 0:
            raise UserError("Quantity must be greater than zero.")

        transfer = self.transfer_id
        source_location = transfer.location_id

        if not source_location:
            raise UserError("No source location is set for this transfer.")

        existing_lines = {line.product_id.id: line for line in transfer.transfer_lines}
        updated_lines = []

        for component in self.bom_id.bom_line_ids:
            if component.product_id.id in existing_lines:
                existing_lines[component.product_id.id].product_uom_qty += component.product_qty * self.kit_quantity
                updated_lines.append((1, existing_lines[component.product_id.id].id, {
                    'product_uom_qty': existing_lines[component.product_id.id].product_uom_qty
                }))
            else:
                updated_lines.append((0, 0, {
                    'transfer_id': transfer.id,
                    'product_id': component.product_id.id,
                    'product_uom_qty': component.product_qty * self.kit_quantity,
                    'product_uom': component.product_uom_id.id,
                    'name': component.product_id.display_name
                }))

        transfer.sudo().write({'transfer_lines': updated_lines})
        return {'type': 'ir.actions.act_window_close'}
