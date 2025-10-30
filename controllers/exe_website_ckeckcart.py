# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.tools.translate import _ # Para traducciones
from odoo.addons.website_sale.controllers.main import WebsiteSale

class WebsiteSaleCheck(WebsiteSale):

    @http.route('/shop/cart/update_json', type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def cart_update_json(self, product_id, add_qty=1, set_qty=0, **kwargs):
        """
        Sobrescribimos el método JSON para añadir al carrito.
        
        Verificamos si el product_id ya existe en las líneas del pedido (carrito).
        """
        
        # 1. Obtener el carrito actual
        order = request.website.sale_get_order()

        # 2. Verificar si el producto ya está en el carrito
        existing_line = order.order_line.filtered(
            lambda line: line.product_id.id == product_id
        )

        # 3. Lógica de advertencia
        if existing_line:
            # ¡El producto ya existe!
            
            # --- INICIO DE LA CORRECCIÓN ---

            # 1. Obtenemos la respuesta JSON estándar del carrito actual.
            # Esto nos da 'lines', 'cart_quantity', 'website_sale.total', etc.
            result = order._get_website_sale_cart_json()

            # 2. Obtenemos el nombre del producto
            product = request.env['product.product'].browse(product_id)
            
            # 3. Preparamos el mensaje de advertencia
            message = _("El producto '%s' ya está presente en el carrito de compras.") % (product.name,)

            # 4. Añadimos nuestra clave 'warning' al diccionario de respuesta estándar
            result['warning'] = message
            
            # 5. Devolvemos el diccionario completo
            # El JS recibirá 'lines' (y no fallará) y también 'warning' (y mostrará el popup)
            return result
            
            # --- FIN DE LA CORRECCIÓN ---

        # 4. Si no existe, llamar al método original (super)
        # Esto no ha cambiado y sigue funcionando igual.
        return super(WebsiteSaleCheck, self).cart_update_json(
            product_id, add_qty=add_qty, set_qty=set_qty, **kwargs
        )