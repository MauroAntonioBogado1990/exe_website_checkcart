# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.tools.translate import _
from odoo.addons.website_sale.controllers.main import WebsiteSale
import json # Necesario para devolver respuestas JSON con warnings

class WebsiteSaleWarning(WebsiteSale):

    # Método auxiliar para la vista (ya lo tenías)
    def _is_product_in_cart(self, product_id):
        order = request.website.sale_get_order()
        if not order:
            return False
        return any(line.product_id.id == product_id for line in order.order_line)

    # Sobrescribir la página de producto para inyectar 'product_in_cart' (ya lo tenías)
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
            # Inyectamos la variable product_in_cart
            'product_in_cart': self._is_product_in_cart(product_variant.id),
        })

    # Sobrescribir el método JSON para bloquear duplicados y ajustar la cantidad
    @http.route('/shop/cart/update_json', type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def cart_update_json(self, product_id, add_qty=1, set_qty=0, force_add=False, **kwargs):
        params = request.params
        product_id = int(product_id)
        product = request.env['product.product'].browse(product_id)
        order = request.website.sale_get_order(force_create=False)

        def _to_float(val, default=0.0):
            try:
                return float(val)
            except Exception:
                return float(default)

        input_set_qty = _to_float(params.get('set_qty', set_qty), set_qty)
        input_add_qty = _to_float(params.get('add_qty', add_qty), add_qty)
        
        # 1. Chequeo de línea existente (para bloqueo/ajuste)
        existing_line = order.order_line.filtered(lambda line: line.product_id.id == product_id)
        
        # 2. LÓGICA DE NO DUPLICACIÓN Y AJUSTE DE CANTIDAD
        # Si la línea ya existe Y la intención es añadir (add_qty > 0 y no es un ajuste de cantidad)
        if existing_line and input_add_qty > 0 and 'set_qty' not in params:
            
            # Bloqueamos la lógica base y ajustamos la cantidad manualmente
            new_qty = existing_line.product_uom_qty + input_add_qty
            
            # Llamamos a super() con set_qty para forzar la actualización de la línea existente
            super(WebsiteSaleWarning, self).cart_update_json(
                product_id=product_id,
                set_qty=new_qty, 
                add_qty=0,
                line_id=existing_line.id
            )
            
            warning_message = _("¡El producto '%s' ya estaba en el carrito! Se ha ajustado la cantidad.") % product.name
            
            # Devolvemos la respuesta JSON con el warning para que el JS lo muestre
            order_sudo = order.sudo()
            return {
                'order_id': order.id,
                'cart_quantity': sum(order_sudo.order_line.mapped('product_uom_qty')),
                'warning': warning_message, 
                'quantity': new_qty, 
            }

        # 3. LÓGICA DE ELIMINACIÓN Y ADVERTENCIA (Si no es adición duplicada)
        
        # Si la intención es eliminar (set_qty == 0), usamos tu lógica de eliminación proactiva
        if 'set_qty' in params and input_set_qty == 0:
            if order:
                line_to_remove = order.order_line.filtered(lambda l: l.product_id.id == product_id)
                if line_to_remove:
                    line_to_remove.unlink()
                    order_sudo = order.sudo()
                    cart_quantity = sum(order_sudo.order_line.mapped('product_uom_qty'))
                    return {
                        'order_id': order.id,
                        'cart_quantity': cart_quantity,
                        'message': _("Producto '%s' eliminado del carrito.") % product.name,
                    }
        
        # Si la línea existía y solo se ajustó la cantidad (set_qty), enviamos un warning
        warning_message = False
        if existing_line and 'set_qty' in params and input_set_qty > 0:
            warning_message = _("El producto '%s' ya estaba en el carrito.") % product.name

        # Llamada a la implementación original de Odoo
        call_add_qty = 0.0 if 'set_qty' in params else input_add_qty

        result = super(WebsiteSaleWarning, self).cart_update_json(
            product_id=product_id,
            add_qty=call_add_qty,
            set_qty=input_set_qty,
            force_add=_to_float(params.get('force_add', force_add), force_add),
            **kwargs
        )

        # 4. Añadir el aviso al resultado si corresponde
        if warning_message:
            try:
                result['warning'] = warning_message
            except Exception:
                pass

        return result