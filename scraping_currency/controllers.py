# -*- coding: utf-8 -*-
from openerp import http

# class ScrapingCurrency(http.Controller):
#     @http.route('/scraping_currency/scraping_currency/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/scraping_currency/scraping_currency/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('scraping_currency.listing', {
#             'root': '/scraping_currency/scraping_currency',
#             'objects': http.request.env['scraping_currency.scraping_currency'].search([]),
#         })

#     @http.route('/scraping_currency/scraping_currency/objects/<model("scraping_currency.scraping_currency"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('scraping_currency.object', {
#             'object': obj
#         })