from odoo import http
from odoo.http import request


class WebsiteCartInfo(http.Controller):

    @http.route('/shop/cart/info', type='json', auth='public', website=True)
    def cart_info(self):
        order = request.website.sale_get_order()
        if not order:
            return {}

        items = []
        for line in order.order_line:
            for item in items:
                if item['product_id'] == line.product_id.id:
                    item['quantity'] += line.product_uom_qty
                    break
            else:
                items.append({
                    'product_id': line.product_id.id,
                    'quantity': line.product_uom_qty,
                })

        return {'cart_items': items}
