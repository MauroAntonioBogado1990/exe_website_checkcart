odoo.define('exe_website_checkcart.prevent_duplicate_cart', function (require) {
    const publicWidget = require('web.public.widget');
    const rpc = require('web.rpc'); // ✅ necesario para llamar al controlador

    publicWidget.registry.PreventDuplicateCart = publicWidget.Widget.extend({
        selector: 'body',

        start: function () {
            console.log("PreventDuplicateCart montado");
            return this._super.apply(this, arguments);
        },

        events: {
            'click .js_check_product': '_onAddToCart',
        },

        _onAddToCart: function (ev) {
            ev.preventDefault();
            ev.stopImmediatePropagation();

            const productId = $(ev.currentTarget).data('product-id');
            console.log("Producto clickeado:", productId); // ✅ validación visual

            // Podés dejar esto como prueba mínima:
            alert("hola");

            // O avanzar con el llamado al controlador:
            /*
            rpc.query({
                route: '/shop/cart/update',
                params: {
                    product_id: productId,
                    add_qty: 1,
                },
            }).then(response => {
                if (response.error) {
                    alert(response.message);
                } else {
                    alert("Producto agregado al carrito");
                }
            });
            */
        },
    });
});