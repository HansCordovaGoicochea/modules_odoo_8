# -*- coding: utf-8 -*-
from openerp import http

class ModuloValorizaciones(http.Controller):
    @http.route('/modulo_valorizaciones/modulo_valorizaciones/', auth='public')
    def index(self, **kw):
        return "Hello, world"

    @http.route('/modulo_valorizaciones/modulo_valorizaciones/objects/', auth='public')
    def list(self, **kw):
        return http.request.render('modulo_valorizaciones.listing', {
            'root': '/modulo_valorizaciones/modulo_valorizaciones',
            'objects': http.request.env['modulo_valorizaciones.modulo_valorizaciones'].search([]),
        })

    @http.route('/modulo_valorizaciones/modulo_valorizaciones/objects/<model("modulo_valorizaciones.modulo_valorizaciones"):obj>/', auth='public')
    def object(self, obj, **kw):
        return http.request.render('modulo_valorizaciones.object', {
            'object': obj
        })



