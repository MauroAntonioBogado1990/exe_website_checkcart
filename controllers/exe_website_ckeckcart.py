# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.tools.translate import _
from odoo.addons.website_sale.controllers.main import WebsiteSale

class WebsiteSaleWarning(WebsiteSale):

    # @http.route('/shop/cart/update_json', type='json', auth="public", methods=['POST'], website=True, csrf=False)
    # def cart_update_json(self, product_id, add_qty=1, set_qty=0, force_add=False, **kwargs):
        
    #     product_id = int(product_id) if isinstance(product_id, (str, int)) else product_id
    #     product = request.env['product.product'].browse(product_id)
        
    #     # 1. Chequear si la línea existe ANTES de la operación
    #     line_exists = False
    #     try:
    #         order = request.website.sale_get_order(force_create=False)
    #         if order:
    #             line = order.order_line.filtered(lambda l: l.product_id.id == product_id)
    #             if line:
    #                 line_exists = True
    #     except Exception:
    #         pass
        
    #     # Almacenar el mensaje de aviso
    #     warning_message = False

    #     # 2. Lógica para el Aviso
    #     if line_exists and add_qty > 0:
    #         warning_message = _("¡El producto '%s' ya estaba en el carrito!") % product.name
            
    #     # 3. Solución Explícita de Eliminación (set_qty=0): Corrección del return
    #     if set_qty == 0:
    #         try:
    #             order = request.website.sale_get_order(force_create=False)
    #             if order:
    #                 line = order.order_line.filtered(lambda l: l.product_id.id == product_id)
    #                 if line:
    #                     line.unlink() # Elimina la línea
                        
    #                     # **CORRECCIÓN FINAL Y CRÍTICA:**
    #                     # Devolvemos el diccionario de actualización del carrito llamando al 
    #                     # método de la orden de venta (_cart_update_result), que es el estándar.
    #                     order.invalidate_cache() # Limpiar caché para asegurar datos frescos
    #                     return order._cart_update_result() # <- Usamos el método de la ORDEN
                        
    #         except Exception as e:
    #             # Si hay error en la eliminación manual, continuamos con la lógica base.
    #             pass 
                
    #     # 4. Lógica de adición/actualización:
    #     # Si set_qty está siendo usado para actualizar (o eliminar, si el paso 3 falló), anulamos add_qty.
    #     if set_qty is not False:
    #         add_qty = 0
            
    #     # 5. Ejecutar la lógica base de Odoo (si no se eliminó manualmente o si no se hizo set_qty=0)
    #     result = super(WebsiteSaleWarning, self).cart_update_json(
    #         product_id,
    #         add_qty=add_qty,
    #         set_qty=set_qty, 
    #         **kwargs
    #     )
        
    #     # 6. Añadir el aviso al resultado si es necesario
    #     if warning_message:
    #         result['warning'] = warning_message

    #     return result
    #se agrega esto
    def _is_product_in_cart(self, product_id):
        order = request.website.sale_get_order()
        return any(line.product_id.id == product_id for line in order.order_line)

    @http.route(['/shop/product/<model("product.template"):product>'], type='http', auth="public", website=True)
    def product_page(self, product, **kwargs):
        combination = product._get_first_possible_combination()
        combination_info = product._get_combination_info(combination, add_qty=1, pricelist=request.website.get_current_pricelist())
        product_variant = request.env['product.product'].browse(combination_info['product_id'])

        return request.render('website_sale.product', {
            'product': product,
            'product_variant': product_variant,
            'combination': combination,
            'combination_info': combination_info,
            'product_in_cart': self._is_product_in_cart(product_variant.id),
        })


    # CÓDIGO FINAL VERIFICADO
    @http.route('/shop/cart/update_json', type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def cart_update_json(self, product_id, add_qty=1, set_qty=0, force_add=False, **kwargs):
        """
        Maneja la eliminación (set_qty == 0) de forma proactiva para un solo producto.
        """
        params = request.params
        product_id = int(product_id) if isinstance(product_id, (str, int)) else product_id
        product = request.env['product.product'].browse(product_id)

        # Leer valores numéricos de los parámetros de forma segura
        def _to_float(val, default=0.0):
            try:
                return float(val)
            except Exception:
                return float(default)

        input_set_qty = _to_float(params.get('set_qty', set_qty), set_qty)

        # 1. LÓGICA CLAVE PARA LA ELIMINACIÓN DE UN SOLO PRODUCTO:
        # Si la intención es establecer la cantidad a 0 (eliminar)
        if 'set_qty' in params and input_set_qty == 0:
            order = request.website.sale_get_order(force_create=False)
            if order:
                # Filtrar SOLAMENTE la línea de pedido que coincide con el product_id
                line_to_remove = order.order_line.filtered(lambda l: l.product_id.id == product_id)
                if line_to_remove:
                    # Usar unlink() en la línea específica
                    line_to_remove.unlink()
                    
                    # Recalcular la cantidad total del carrito después de la eliminación
                    order_sudo = order.sudo()
                    cart_quantity = sum(order_sudo.order_line.mapped('product_uom_qty'))

                    # Devolver la respuesta JSON que el frontend espera
                    return {
                        'order_id': order.id,
                        'cart_quantity': cart_quantity,
                        'message': _("Producto '%s' eliminado del carrito.") % product.name,
                    }
            
            # Si no hay orden o línea que eliminar, dejamos que el super() intente manejarlo 
            # (aunque no debería hacer nada si ya se eliminó o no existía)

        # 2. Lógica para añadir/actualizar (cuando NO es eliminación)

        # ... [El resto de tu lógica de warning anterior puede ir aquí] ...
        # Chequear si la línea existía ANTES de la operación actual (solo para el mensaje de advertencia)
        line_exists = False
        try:
            order_check = request.website.sale_get_order(force_create=False)
            if order_check:
                if order_check.order_line.filtered(lambda l: l.product_id.id == product_id):
                    line_exists = True
        except Exception:
            pass
            
        warning_message = False
        # Si se está sumando cantidad y la línea ya existía
        if line_exists and _to_float(params.get('add_qty', add_qty) or 0) > 0:
            warning_message = _("¡El producto '%s' ya estaba en el carrito!") % product.name
        # ... [Fin lógica de warning] ...

        # Llamada a la implementación original con valores normalizados
        # Para la llamada super, si es una acción de set_qty, forzamos add_qty a 0
        call_add_qty = 0.0 if 'set_qty' in params else _to_float(params.get('add_qty', add_qty), add_qty)

        result = super(WebsiteSaleWarning, self).cart_update_json(
            product_id=product_id,
            add_qty=call_add_qty,
            set_qty=input_set_qty,
            force_add=_to_float(params.get('force_add', force_add), force_add),
            **kwargs
        )

        # 3) Añadir el aviso al resultado si corresponde
        if warning_message:
            try:
                result['warning'] = warning_message
            except Exception:
                pass

        return result
