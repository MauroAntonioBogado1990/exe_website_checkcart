odoo.define('exe_website_checkcart.confirm_cart_addition', function (require) {
    "use strict";

    const publicWidget = require('web.public.widget');
    const ajax = require('web.ajax');
    const core = require('web.core');
    const _t = core._t;

    publicWidget.registry.WebsiteSale.include({

        _callController: function (route, params) {
            const def = this._super.apply(this, arguments);

            if (route !== '/shop/cart/update_json') {
                return def;
            }

            const self = this;
            return def.then(function (data) {
                // Si se requiere confirmación, mostrar modal
                if (data && data.require_confirmation) {
                    self._showConfirmationModal(data);
                    return Promise.resolve(); // Detener flujo original
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
                if (data && data.message) {
                    self.displayNotification({
                        type: 'info',
                        title: _t('Información'),
                        message: data.message,
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
                        <p>${data.message}</p>
                      </div>
                      <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-dismiss="modal">${_t("Cancelar")}</button>
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

                // Reintentar la llamada con force_add: true
                ajax.jsonRpc('/shop/cart/update_json', 'call', {
                    product_id: data.product_id,
                    add_qty: data.add_qty,
                    set_qty: data.set_qty,
                    force_add: true
                }).then(function (result) {
                    if (result && result.message) {
                        publicWidget.registry.WebsiteSale.prototype.displayNotification({
                            type: 'info',
                            title: _t('Confirmado'),
                            message: result.message,
                            sticky: false,
                        });
                    }
                });
            });

            modal.on('hidden.bs.modal', function () {
                modal.remove();
            });
        }
    });
});