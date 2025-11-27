odoo.define('exe_website_checkcart.confirm_cart_addition', function (require) {
    "use strict";

    const publicWidget = require('web.public.widget');
    const ajax = require('web.ajax');
    const core = require('web.core');
    const _t = core._t;

    publicWidget.registry.WebsiteSale.include({

        _callController: function (route, params) {
            const def = this._super.apply(this, arguments);

            // Sólo nos interesa el endpoint del carrito
            if (route !== '/shop/cart/update_json') {
                return def;
            }

            const self = this;

            return def.then(function (data) {
                // Si no hay data, devolvemos la respuesta tal cual
                if (!data) {
                    return data;
                }

                // Si el backend pide confirmación para esta operación mostramos modal,
                // pero NO alteramos la ejecución original ni revertimos la acción.
                // El modal, si se confirma, realizará una llamada adicional con force_add:true
                // (esto respeta la lógica del servidor y no provoca dobles efectos al eliminar).
                if (data && data.require_confirmation) {
                    // Determinar si la intención original era eliminar (set_qty === 0)
                    // Si era eliminación, NO mostrar modal de confirmación.
                    var isDeletion = (params && (typeof params.set_qty !== 'undefined') && Number(params.set_qty) === 0);
                    if (!isDeletion) {
                        self._showConfirmationModal(data);
                    }
                    // Devolver data para que la UI procese la respuesta original sin bloqueos
                    return data;
                }

                // Mostrar advertencia si existe
                if (data && data.warning) {
                    self.displayNotification({
                        type: 'warning',
                        title: _t('Advertencia'),
                        message: data.warning,
                        sticky: false,
                    });
                }

                // Mostrar mensaje informativo si existe
                if (data && (data.message || data.info)) {
                    self.displayNotification({
                        type: 'info',
                        title: _t('Información'),
                        message: data.message || data.info,
                        sticky: false,
                    });
                }

                return data;
            });
        },

        _showConfirmationModal: function (data) {
            const modal = $(`
                <div class="modal fade" id="confirmAddModal" tabindex="-1" role="dialog">
                  <div class="modal-dialog modal-dialog-centered" role="document">
                    <div class="modal-content">
                      <div class="modal-header bg-warning text-dark">
                        <h5 class="modal-title">${_t("Producto ya en el carrito")}</h5>
                        <button type="button" class="close" data-dismiss="modal">&times;</button>
                      </div>
                      <div class="modal-body">
                        <p>${data.message || _t("El producto ya existe en el carrito. ¿Desea continuar?")}</p>
                      </div>
                      <div class="modal-footer">
                        <button type="button" class="btn btn-secondary cancel-add" data-dismiss="modal">${_t("Cancelar")}</button>
                        <button type="button" class="btn btn-primary confirm-add">${_t("Desea continuar")}</button>
                      </div>
                    </div>
                  </div>
                </div>
            `);

            $('body').append(modal);
            modal.modal('show');

            modal.find('.confirm-add').on('click', function () {
                modal.modal('hide');
                modal.remove();

                // Reintentar la llamada con force_add: true (no alteramos la llamada original)
                ajax.jsonRpc('/shop/cart/update_json', 'call', {
                    product_id: data.product_id,
                    add_qty: data.add_qty,
                    set_qty: data.set_qty,
                    force_add: true
                }).then(function (result) {
                    if (result && (result.message || result.info)) {
                        publicWidget.registry.WebsiteSale.prototype.displayNotification({
                            type: 'info',
                            title: _t('Confirmado'),
                            message: result.message || result.info,
                            sticky: false,
                        });
                    }
                }).catch(function (err) {
                    // Silenciar errores de la llamada adicional (no romper UX)
                    console.error('confirm_add error', err);
                });
            });

            modal.on('hidden.bs.modal', function () {
                modal.remove();
            });
        }
    });
});

odoo.define('exe_website_checkcart.prevent_duplicate_cart', function (require) {
    "use strict";
    require('website_sale.website_sale');
    
    var core = require('web.core');
    var _t = core._t;

    // Duración de la alerta en milisegundos: 10 SEGUNDOS
    var TOAST_DURATION = 10000; 

    // Función para mostrar la alerta temporal (Toast) - MODIFICADA
    function showToast(msg, level) {
        level = level || 'info';
        var bg = (level === 'warning' ? '#f2dede' : '#dff0d8');
        var color = (level === 'warning' ? '#a94442' : '#3c763d');
        
        var $toast = $('<div/>', {class: 'exe-cart-toast'}).text(msg).css({
            position: 'fixed',
            // POSICIÓN ACTUALIZADA: 100px desde arriba
            top: '100px', 
            'z-index': 20000,
            padding: '10px 14px',
            'background-color': bg,
            color: color,
            'border-radius': '4px',
            'border': '1px solid rgba(0,0,0,0.05)',
            'box-shadow': '0 2px 6px rgba(0,0,0,0.12)',
            
            // CENTRADO HORIZONTAL
            left: '50%',
            transform: 'translateX(-50%)',
            'text-align': 'center',
        });
        
        $('body').append($toast);
        
        // El Toast se oculta después de 10 segundos
        setTimeout(function () { $toast.fadeOut(250, function () { $toast.remove(); }); }, TOAST_DURATION); 
    }

    // Escuchador de respuestas AJAX del carrito (sin cambios en esta sección)
    $(document).ajaxComplete(function (event, xhr, settings) {
        try {
            if (!settings || !settings.url || settings.url.indexOf('/shop/cart/update_json') === -1) { return; }
            if (xhr.status !== 200) { return; }

            var data;
            try { data = JSON.parse(xhr.responseText); } catch (e) { return; }
            if (!data) { return; }

            if (data.warning) { showToast(data.warning, 'warning'); }
            else if (data.info || data.message) { showToast(data.info || data.message, 'info'); }
            
        } catch (err) {
            console.error('prevent_duplicate_cart error:', err);
        }
    });

    // Widget para el botón "Ya está en el carrito" (sin cambios en esta sección)
    const publicWidget = require('web.public.widget');

    publicWidget.registry.CartButtonWarning = publicWidget.Widget.extend({
        selector: '.js_redirect_with_warning', 
        events: {
            'click': '_onClick',
        },

        _onClick: function (ev) {
            ev.preventDefault(); 
            
            showToast(_t("¡El producto ya existe en tu carrito! Redirigiendo a su carrito..."), 'warning');
            
            // Redirige al carrito después de 1 segundo
            setTimeout(function() {
                window.location.href = "/shop/cart";
            }, 1000); 
        },
    });
});
