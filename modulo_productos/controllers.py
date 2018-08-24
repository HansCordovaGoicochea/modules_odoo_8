# -*- coding: utf-8 -*-
from openerp import http

# class ModuloProductos(http.Controller):
#     @http.route('/modulo_productos/modulo_productos/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/modulo_productos/modulo_productos/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('modulo_productos.listing', {
#             'root': '/modulo_productos/modulo_productos',
#             'objects': http.request.env['modulo_productos.modulo_productos'].search([]),
#         })

#     @http.route('/modulo_productos/modulo_productos/objects/<model("modulo_productos.modulo_productos"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('modulo_productos.object', {
#             'object': obj
#         })