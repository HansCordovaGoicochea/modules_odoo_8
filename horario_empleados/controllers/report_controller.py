# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2015 Therp BV (<http://therp.nl>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import base64
import pdb
from openerp.addons.web.http import Controller, route, request
from openerp.addons.report.controllers.main import ReportController
from openerp.osv import osv
from openerp import http
import simplejson
import time
import logging
from werkzeug import exceptions, url_decode

_logger = logging.getLogger(__name__)

id_slip = 0

class ReportController(ReportController):
    @http.route([
        '/report/<path:converter>/<reportname>',
        '/report/<path:converter>/<reportname>/<docids>',
    ])
    def report_routes(self, reportname, docids=None, converter=None, **data):
        global id_slip
        response = super(ReportController, self).report_routes(
            reportname, docids=docids, converter=converter, **data)
        if reportname == "horario_empleados.report_nominas_empleados_pdf":
            # print (response)
            report_obj = request.registry['report']
            cr, uid, context = request.cr, request.uid, request.context
            options_data = None
            if data.get('options'):
                options_data = simplejson.loads(data['options'])
            if data.get('context'):
                # Ignore 'lang' here, because the context in data is the one from the webclient *but* if
                # the user explicitely wants to change the lang, this mechanism overwrites it.
                data_context = simplejson.loads(data['context'])
                # print (data_context)
                id_slip = data_context['active_id']
                # print (id_slip)
                if data_context.get('lang'):
                    del data_context['lang']
                context.update(data_context)

            pdf = report_obj.get_pdf(cr, uid, docids, reportname, data=options_data, context=context)
            pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', len(pdf))]
            # print ("ggggggggggggg" )
            # print (pdfhttpheaders )

            return request.make_response(pdf, headers=pdfhttpheaders)

        return response

    # @http.route(['/report/download'])
    # def report_download(self, data, token):
    #     order_obj = http.request.env['hr.payslip.run']
    #     requestcontent = simplejson.loads(data)
    #     url, type = requestcontent[0], requestcontent[1]
    #     response = super(ReportController, self).report_download(data, token)
    #     print (response)
    #     if type == 'qweb-pdf':
    #         reportname = url.split('/report/pdf/')[1].split('?')[0]
    #         if reportname == "horario_empleados.report_nominas_empleados_pdf":
    #             object = order_obj.browse(id_slip)
    #             f_i = object.date_start
    #             f_f = object.date_end
    #             filename = 'Nomina_del_' + f_i + '_al_' + f_f
    #             response.headers.set('Content-Disposition', 'attachment; filename=%s.pdf;' % filename)
    #
    #         # from pyPdf import PdfFileWriter, PdfFileReader
    #         # inputpdf = PdfFileReader(open(filename+'.pdf', "rb"))
    #         # for i in xrange(inputpdf.numPages):
    #         #     output = PdfFileWriter()
    #         #     output.addPage(inputpdf.getPage(i))
    #         #     with open("C:\Nominas\document-page%s.pdf" % i, "wb") as outputStream:
    #         #         output.write(outputStream)
    #
    #
    #     return response
