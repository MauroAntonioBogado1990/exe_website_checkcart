{
    'name': 'Exe Web Site Ckechcart',
    'version': '15.0',
    'category': 'Tools',
    'author':'Mauro Bogado,Exemax',
    'summary': 'Modulo para poder realizar el control del carrito de compras de la web',
    'depends': ['base','sale','web', 'website'],
    'data': [
        'views/product_cart_warning.xml',

        #'security/ir.model.access.csv',
        #'views/assets.xml',
        #'views/add_to_cart_override.xml',

        
        
    ],
    'assets': {
    'web.assets_frontend': [
        'exe_website_checkcart/static/src/js/prevent_duplicate_cart.js',
        'exe_website_checkcart/static/src/js/cart_check.js',

        #'exe_website_checkcart/static/src/js/website_sale_warning.js',
    ],
    },

    'installable': True,
    'application': False,
}