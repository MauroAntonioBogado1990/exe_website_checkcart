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
        
        # Almacenar un posible mensaje de aviso
        warning_message = False

        # 2. Lógica para el Aviso
        # Solo avisamos si el producto YA EXISTE y la intención es AGREGAR unidades (add_qty > 0)
        if line_exists and add_qty > 0:
            warning_message = _("¡El producto '%s' ya estaba en el carrito! Se ha actualizado la cantidad.") % product.name
            
        # 3. Corrección Crítica: Lógica para manejar correctamente la cantidad
        # Si 'set_qty' se proporciona (lo que ocurre al eliminar o ajustar la cantidad en el carrito),
        # 'add_qty' DEBE ser 0 para que no se sume una unidad extra.
        # Esto también permite que set_qty=0 elimine el producto.
        
        # Odoo por defecto pasa set_qty como 0 si se usa el botón de "Eliminar" del carrito.
        # Si set_qty es diferente de False/None, asumimos que se quiere ESTABLECER la cantidad.
        if set_qty is not False and set_qty >= 0:
            add_qty = 0

        # 4. Ejecutar la lógica base de Odoo
        # Esta llamada realiza la adición, actualización o eliminación real.
        result = super(WebsiteSaleWarning, self).cart_update_json(
            product_id,
            add_qty=add_qty,
            set_qty=set_qty,
            **kwargs
        )
        
        # 5. Si hay un mensaje de aviso preparado, se añade al resultado
        # Usamos 'warning' que es más estándar para mensajes temporales en el frontend de Odoo.
        if warning_message:
            result['warning'] = warning_message

        return result