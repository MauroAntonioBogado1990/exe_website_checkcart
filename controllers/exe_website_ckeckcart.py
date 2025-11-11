# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.tools.translate import _
from odoo.addons.website_sale.controllers.main import WebsiteSale

class WebsiteSaleWarning(WebsiteSale):

    @http.route('/shop/cart/update_json', type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def cart_update_json(self, product_id, add_qty=1, set_qty=0, force_add=False, **kwargs):
        
        product_id = int(product_id) if isinstance(product_id, (str, int)) else product_id
        product = request.env['product.product'].browse(product_id)
        
        # 1. Chequear si la línea existe ANTES de la operación
        line_exists = False
        try:
            order = request.website.sale_get_order(force_create=False)
            if order:
                line = order.order_line.filtered(lambda l: l.product_id.id == product_id)
                if line:
                    line_exists = True
        except Exception:
            pass
        
        # Almacenar el mensaje de aviso
        warning_message = False

        # 2. Lógica para el Aviso
        if line_exists and add_qty > 0:
            warning_message = _("¡El producto '%s' ya estaba en el carrito!") % product.name
            
        # 3. Solución Explícita de Eliminación (set_qty=0): Corrección del return
        if set_qty == 0:
            try:
                order = request.website.sale_get_order(force_create=False)
                if order:
                    line = order.order_line.filtered(lambda l: l.product_id.id == product_id)
                    if line:
                        line.unlink() # Elimina la línea
                        
                        # **CORRECCIÓN FINAL Y CRÍTICA:**
                        # Devolvemos el diccionario de actualización del carrito llamando al 
                        # método de la orden de venta (_cart_update_result), que es el estándar.
                        order.invalidate_cache() # Limpiar caché para asegurar datos frescos
                        return order._cart_update_result() # <- Usamos el método de la ORDEN
                        
            except Exception as e:
                # Si hay error en la eliminación manual, continuamos con la lógica base.
                pass 
                
        # 4. Lógica de adición/actualización:
        # Si set_qty está siendo usado para actualizar (o eliminar, si el paso 3 falló), anulamos add_qty.
        if set_qty is not False:
            add_qty = 0
            
        # 5. Ejecutar la lógica base de Odoo (si no se eliminó manualmente o si no se hizo set_qty=0)
        result = super(WebsiteSaleWarning, self).cart_update_json(
            product_id,
            add_qty=add_qty,
            set_qty=set_qty, 
            **kwargs
        )
        
        # 6. Añadir el aviso al resultado si es necesario
        if warning_message:
            result['warning'] = warning_message

        return result