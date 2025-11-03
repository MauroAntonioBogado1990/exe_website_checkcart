# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.tools.translate import _
from odoo.addons.website_sale.controllers.main import WebsiteSale

class WebsiteSaleCheck(WebsiteSale):

    @http.route('/shop/cart/update_json', type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def cart_update_json(self, product_id, add_qty=1, set_qty=0, **kwargs):
        try:
            product_id = int(product_id)
        except Exception:
            pass

        product = request.env['product.product'].browse(product_id)

        # Obtener parámetros
        params = getattr(request, 'jsonrequest', None) or request.params or {}

        # Detectar si se envió set_qty explícitamente (incluso si es 0)
        set_qty_raw = params.get('set_qty', kwargs.get('set_qty'))
        set_qty_provided = set_qty_raw is not None and str(set_qty_raw).strip() != ''

        # Normalizar valores
        try:
            set_qty_param = float(set_qty_raw or 0)
        except Exception:
            set_qty_param = float(set_qty or 0)

        try:
            # Aquí add_qty_param puede ser positivo (agregar) o negativo (reducir)
            add_qty_param = float(params.get('add_qty', add_qty) or 0)
        except Exception:
            add_qty_param = float(add_qty or 0)

        # Verificar si el producto ya estaba en el carrito antes de la operación
        existed_before = False
        try:
            order = request.website.sale_get_order(force_create=False)
            if order:
                line = order.order_line.filtered(lambda l: l.product_id.id == product_id)
                if line:
                    existed_before = True
        except Exception:
            pass

        # Ejecutar la lógica original con parámetros corregidos.
        # Esto es crucial: Si set_qty_provided es True, se usa set_qty_param.
        # Si set_qty_provided es False, se usa add_qty_param (que puede ser negativo para reducir).
        result = super(WebsiteSaleCheck, self).cart_update_json(
            product_id,
            add_qty=0 if set_qty_provided else add_qty_param,
            set_qty=set_qty_param if set_qty_provided else 0,
            **kwargs
        )

        # --- INICIO DE LA CORRECCIÓN ---
        # Mostrar advertencia solo si la intención fue agregar (add_qty > 0)
        # y no se intentó establecer una cantidad explícita (set_qty_provided = False)
        try:
            if add_qty_param > 0 and not set_qty_provided and existed_before:
                result['warning'] = _("El producto '%s' ya existe en el carrito.") % product.name
        except Exception:
            pass

        # --- FIN DE LA CORRECCIÓN ---

        return result