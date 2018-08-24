# -*- coding: utf-8 -*-
from openerp import http

# class ModReportes(http.Controller):
#     @http.route('/mod_reportes/mod_reportes/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mod_reportes/mod_reportes/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('mod_reportes.listing', {
#             'root': '/mod_reportes/mod_reportes',
#             'objects': http.request.env['mod_reportes.mod_reportes'].search([]),
#         })

#     @http.route('/mod_reportes/mod_reportes/objects/<model("mod_reportes.mod_reportes"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mod_reportes.object', {
#             'object': obj
#         })