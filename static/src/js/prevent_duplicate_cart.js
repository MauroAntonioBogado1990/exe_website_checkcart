odoo.define('exe_website_checkcart.notify_cart_addition', function (require) {
    "use strict";

    const publicWidget = require('web.public.widget');
    const core = require('web.core');
    const _t = core._t;

    publicWidget.registry.WebsiteSale.include({

        _callController: function (route, params) {
            var def = this._super.apply(this, arguments);

            if (route !== '/shop/cart/update_json') {
                return def;
            }

            var self = this;
            return def.then(function (data) {
                if (data && data.warning) {
                    self.displayNotification({
                        type: 'warning',
                        title: _t('Advertencia'),
                        message: data.warning,
                        sticky: false,
                    });
                }
                return data;
            });
        }
    });
});


odoo.define('exe_website_checkcart.prevent_duplicate_cart', function (require) {
    "use strict";

    function showToast(msg) {
        var $toast = $('<div/>', {class: 'exe-cart-toast'}).text('⚠️ ' + msg).css({
            position: 'fixed',
            right: '20px',
            top: '20px',
            'z-index': 2000,
            padding: '12px 16px',
            'background-color': '#fbeed5',
            color: '#8a6d3b',
            'border-radius': '4px',
            'border': '1px solid rgba(0,0,0,0.05)',
            'box-shadow': '0 2px 6px rgba(0,0,0,0.12)'
        });
        $('body').append($toast);
        setTimeout(function () { $toast.fadeOut(250, function () { $toast.remove(); }); }, 3000);
    }

    $(document).ajaxComplete(function (event, xhr, settings) {
        try {
            if (!settings || !settings.url || xhr.status !== 200) return;
            if (settings.url.indexOf('/shop/cart/update_json') === -1) return;

            var data = JSON.parse(xhr.responseText || '{}');
            if (data.warning) {
                showToast(data.warning);
            }
        } catch (err) {
            console.error('prevent_duplicate_cart error:', err);
        }
    });
});