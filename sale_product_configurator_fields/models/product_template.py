from odoo import models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def get_single_product_variant(self):
        """ Check if the product template has accessory products or alternative products
            and return the single product variant if it exists.
        """
        res = super(ProductTemplate, self).get_single_product_variant()

        if res.get('product_id', False):

            # Accessory Products
            has_accessory_products = False
            for accessory_product in self.product_variant_id.accessory_product_ids:
                product_template = accessory_product.product_tmpl_id
                if product_template.has_dynamic_attributes() or product_template._get_possible_variants(
                        self.product_variant_id.product_template_attribute_value_ids
                ):
                    has_accessory_products = True
                    break

            # Alternative Products
            has_alternative_products = False
            for alternative_product in self.product_variant_id.alternative_product_ids:
                if alternative_product.has_dynamic_attributes() or alternative_product._get_possible_variants(
                        self.product_variant_id.product_template_attribute_value_ids
                ):
                    has_alternative_products = True
                    break

            res.update({
                'has_accessory_products': has_accessory_products,
                'has_alternative_products': has_alternative_products,
                'is_combo': self.type == 'combo',
            })

        return res
