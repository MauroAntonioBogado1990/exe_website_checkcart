odoo.define('your_module.prevent_duplicate_cart', function (require) {
    const ajax = require('web.ajax');
    const publicWidget = require('web.public.widget');

    publicWidget.registry.PreventDuplicateCart = publicWidget.Widget.extend({
        selector: '.oe_website_sale',
        events: {
            'click .add_to_cart_button': '_onAddToCart',
        },

        _onAddToCart: function (ev) {
            ev.preventDefault();
            const productId = $(ev.currentTarget).data('product-id');

            ajax.jsonRpc('/shop/cart/update', 'call', {
                product_id: productId,
                add_qty: 1,
            }).then(function (response) {
                if (response.error) {
                    alert(response.message); // Podés usar SweetAlert o Owl para algo más visual
                } else {
                    location.reload(); // O actualizar el carrito dinámicamente
                }
            });
        },
    });
});