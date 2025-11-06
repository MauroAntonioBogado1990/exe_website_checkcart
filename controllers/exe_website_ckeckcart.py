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
            warning_message = _("¡El producto '%s' ya estaba en el carrito! Se ha actualizado la cantidad.") % product.name
            
        # 3. Solución Explícita de Eliminación (set_qty=0): Corrección del return
        if set_qty == 0:
            try:
                order = request.website.sale_get_order(force_create=False)
                if order:
                    line = order.order_line.filtered(lambda l: l.product_id.id == product_id)
                    if line:
                        line.unlink() # **¡Eliminación exitosa!**
                        
                        # **CORRECCIÓN CRÍTICA AQUÍ:**
                        # Para devolver el resultado esperado después de la eliminación manual,
                        # llamamos al método del controlador base.
                        # Obtenemos la orden actualizada después de eliminar.
                        order = request.website.sale_get_order() 
                        
                        return self._get_res_url_response(order) 
                        # 'self._get_res_url_response(order)' es la forma correcta 
                        # de obtener el JSON de respuesta del carrito actualizado en muchos Odoo
                        
            except Exception as e:
                # Opcional: imprimir error para debug
                # print(f"Error al eliminar línea manualmente: {e}")
                pass
                
        # 4. Lógica de adición/actualización:
        # Si set_qty está siendo usado para actualizar (N > 0) y NO se eliminó antes, 
        # anulamos add_qty para no interferir.
        if set_qty is not False:
            add_qty = 0
            
        # 5. Ejecutar la lógica base de Odoo (si no se eliminó manualmente)
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