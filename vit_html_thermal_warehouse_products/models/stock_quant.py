from odoo import models


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    def get_product_name_by_lang(self, product, lang_code):
        self.ensure_one()
        return product.with_context(lang=lang_code).name

    def get_warehouse_products(self, docs):
        products = {
            'products': [],
        }

        for doc in docs:
            product = doc.product_id
            if product not in products['products']:
                products['products'].append(product)
                print(self.get_product_name_by_lang(product, 'en_US'))
                print(self.get_product_name_by_lang(product, 'ar_001'))

            if product.id not in products:
                products[product.id] = []
                products[product.id].append([doc.location_id, doc.quantity])
            else:
                products[product.id].append([doc.location_id, doc.quantity])

        return products
