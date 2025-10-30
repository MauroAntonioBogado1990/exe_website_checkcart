{
    'name': 'Exe Web Site Ckechcart',
    'version': '15.0',
    'category': 'Tools',
    'author':'Mauro Bogado,Exemax',
    'summary': 'Modulo para poder realizar el control del carrito de compras de la web',
    'depends': ['base','sale','web', 'website'],
    'data': [
        #'security/ir.model.access.csv',
        'views/website_date.xml',
        
        
    ],
    'assets': {
    'web.assets_frontend': [
        'exe_website_checkcart/static/src/js/prevent_duplicate_cart.js',
    ],
    },

    'installable': True,
    'application': False,
}   