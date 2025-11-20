odoo.define('exe_website_checkcart.cart_check', function (require) {
    const publicWidget = require('web.public.widget');

    publicWidget.registry.CartCheck = publicWidget.Widget.extend({
        selector: '#add_to_cart',
        start: function () {
            if ($('.alert.alert-warning').length) {
                this.$el.addClass('btn-secondary').removeClass('btn-primary');
                this.$el.text('Ya está en el carrito');
            }
        },
    });
});
