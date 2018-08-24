# -*- coding: utf-8 -*-
from openerp import http

# class ModuloOcultarPos(http.Controller):
#     @http.route('/modulo_ocultar_pos/modulo_ocultar_pos/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/modulo_ocultar_pos/modulo_ocultar_pos/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('modulo_ocultar_pos.listing', {
#             'root': '/modulo_ocultar_pos/modulo_ocultar_pos',
#             'objects': http.request.env['modulo_ocultar_pos.modulo_ocultar_pos'].search([]),
#         })

#     @http.route('/modulo_ocultar_pos/modulo_ocultar_pos/objects/<model("modulo_ocultar_pos.modulo_ocultar_pos"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('modulo_ocultar_pos.object', {
#             'object': obj
#         })