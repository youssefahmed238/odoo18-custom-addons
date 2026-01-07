from odoo import models, fields


class WarehouseProduct(models.Model):
    _inherit = 'warehouse.product'

    def print_warehouse_product_thermal_report(self):
        wp = self.search([])
        return self.env.ref(
            'vit_html_thermal_warehouse_products.action_report_warehouse_product_thermal'
        ).report_action(wp)
