from odoo import http
from odoo.http import request

class WebsiteSaleCustom(http.Controller):

    @http.route(['/shop/cart/update'], type='json', auth='user', website=True)
    def custom_add_to_cart(self, product_id, add_qty=1):
        order = request.website.sale_get_order()
        existing_line = order.order_line.filtered(lambda l: l.product_id.id == product_id)

        if existing_line:
            return {
                'error': True,
                'message': f"Ya agregaste este producto al carrito. Podés modificar la cantidad desde el carrito."
            }

        # Si no existe, agregar normalmente
        request.website.sale_get_order(force_create=True)._cart_update(
            product_id=product_id,
            add_qty=add_qty,
        )
        return {'success': True}