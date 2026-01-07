from odoo import models, fields, api


class WarehouseProduct(models.Model):
    _name = 'warehouse.product'
    _description = 'Warehouse Product Dashboard'
    _inherit = 'stock.quant'
    _auto = False

    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse', readonly=True)
    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    quantity = fields.Float(string='Quantity', readonly=True)
    location_id = fields.Many2one('stock.location', string='Location', readonly=True)

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        """Override to filter by user's default warehouse and internal locations"""
        user = self.env.user
        default_warehouse = user.property_warehouse_id

        new_args = args + [
            ('quantity', '>', 0),
            ('location_id.usage', '=', 'internal')
        ]

        if default_warehouse:
            new_args.append(('warehouse_id', '=', default_warehouse.id))

        # Use stock.quant's search - handle count parameter properly
        if count:
            return self.env['stock.quant'].search_count(new_args)
        else:
            return self.env['stock.quant'].search(new_args, offset=offset, limit=limit, order=order)

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        """Override to use stock.quant data"""
        if domain is None:
            domain = []

        # Get user's default warehouse
        user = self.env.user
        default_warehouse = user.property_warehouse_id

        # Add filters
        domain = domain + [
            ('quantity', '>', 0),
            ('location_id.usage', '=', 'internal')
        ]

        if default_warehouse:
            domain.append(('warehouse_id', '=', default_warehouse.id))

        # Use stock.quant's search_read
        return self.env['stock.quant'].search_read(domain, fields, offset, limit, order)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        """Override for pivot view to use stock.quant data"""
        if domain is None:
            domain = []

        # Get user's default warehouse
        user = self.env.user
        default_warehouse = user.property_warehouse_id

        # Add filters
        domain = domain + [
            ('quantity', '>', 0),
            ('location_id.usage', '=', 'internal')
        ]

        if default_warehouse:
            domain.append(('warehouse_id', '=', default_warehouse.id))

        # Use stock.quant's read_group
        return self.env['stock.quant'].read_group(domain, fields, groupby, offset, limit, orderby, lazy)
