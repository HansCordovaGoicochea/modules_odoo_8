# -*- coding: utf-8 -*-
from openerp import http

# class WebExample(http.Controller):
#     @http.route('/web_example/web_example/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/web_example/web_example/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('web_example.listing', {
#             'root': '/web_example/web_example',
#             'objects': http.request.env['web_example.web_example'].search([]),
#         })

#     @http.route('/web_example/web_example/objects/<model("web_example.web_example"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('web_example.object', {
#             'object': obj
#         })