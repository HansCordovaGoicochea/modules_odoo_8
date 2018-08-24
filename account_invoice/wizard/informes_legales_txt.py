# -*- coding: utf-8 -*-
"""Framework for importing bank statement files."""
import logging
import base64

from openerp import api, models, fields
from openerp.tools.translate import _
import datetime
from datetime import date
from openerp.exceptions import except_orm, Warning, RedirectWarning

_logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


class account_registro_compras(models.TransientModel):
    @api.multi
    def generate_file_data1(self):
        self.ensure_one()
        content = ''
        hoy = datetime.datetime.now()
        anio = hoy.year
        mes = hoy.month
        dia = hoy.day
        # datetime.today().strftime('%m-%d-%Y')
        # obj_facturas = self.env['account.invoice'].search([['type','=','in_invoice'],['create_date','<']])
        self.env.cr.execute("SELECT * FROM account_invoice "
                            "WHERE create_date BETWEEN %s  AND %s "
                            "AND type = 'in_invoice' AND date_invoice <= (SELECT date_trunc('month',current_date) +'1month' - '1sec' ::INTERVAL) "
                            "AND state in ('open','paid')"
                            "ORDER BY date_invoice", (self.fecha_desde + ' 00:00:00', self.fecha_hasta +' 23:59:59'))
        data = self.env.cr.dictfetchall()

        spli_date_to = self.fecha_hasta.split('-')

        correlativo_m1 = 0
        for f in data:
            serie_factura_proveedor = str(f['serie_factura_proveedor'])
            correlativo_factura_proveedor = str(f['correlativo_factura_proveedor'])
            fecha_emision = datetime.datetime.strptime(str(f['date_invoice']), '%Y-%m-%d')
            fecha_emision_format = datetime.date.strftime(fecha_emision, "%d/%m/%Y")

            self.env.cr.execute("SELECT code "
                                "FROM account_journal WHERE id = %s ", [f['journal_id']])
            code_diario = int(self.env.cr.fetchone()[0])

            self.env.cr.execute("SELECT code "
                                "FROM einvoice_catalog_01 WHERE id = %s ", [f['tipo_factura']])
            code_diario2 = self.env.cr.fetchone()
            if code_diario2:
                code_diario2 = code_diario2[0]
            else:
                code_diario2 = ''

            self.env.cr.execute("SELECT doc_type, doc_number, display_name "
                                "FROM res_partner WHERE id = %s ", [f['partner_id']])
            proveedor = self.env.cr.fetchone()
            if proveedor[0] and proveedor[1]:
                if str(proveedor[0]) == 'ruc':
                    code_doc = '6'
                elif str(proveedor[0] == 'dni'):
                    code_doc = '1'
                else:
                    code_doc = '0'
            else:
                code_doc = '0'

            self.env.cr.execute("SELECT name, tc_compra, tc_venta "
                                "FROM res_currency WHERE id = %s ", [f['currency_id']])
            moneda = self.env.cr.fetchone()

            date_invoice = str(f['date_invoice']).split('-')
            if int(mes) > int(date_invoice[1]):
                code_ajuste = 6
            else:
                code_ajuste = 1

            correlativo_m1 += 1

            rate = self.env['res.currency'].search([['id', '=', f['currency_id']]])
            rate_line = self.env['res.currency.rate'].search([['currency_id', '=', f['currency_id']]])

            invoice_line = self.env['account.invoice.line'].search([['invoice_id', '=', f['id']]], limit=1)
            monto_base_tax = sum(line.base for line in invoice_line.invoice_id.tax_line) or 0.0
            monto_tax = sum(line.amount for line in invoice_line.invoice_id.tax_line) or 0.0

            for fecha_cambio in rate_line:
                if fecha_cambio.name == f['date_invoice']:
                    if invoice_line.invoice_id.tax_line:
                        inafecta = (invoice_line.invoice_id.amount_untaxed - monto_base_tax) * moneda[1] or 0.0
                        monto_sin_igv = monto_base_tax * fecha_cambio.tc_compra_rate
                        amount_tax = monto_tax * fecha_cambio.tc_compra_rate
                        amount_total = f['amount_total'] * fecha_cambio.tc_compra_rate
                    else:
                        inafecta = f['amount_total'] * fecha_cambio.tc_compra_rate
                        monto_sin_igv = 0.00
                        amount_tax = 0.00
                        amount_total = f['amount_total'] * fecha_cambio.tc_compra_rate

                    content += str(str(spli_date_to[0]+''+str(spli_date_to[1]).zfill(2)+'00')) + '|' + str(f['internal_number'] or '') + '|' + str(
                'M01' + str(correlativo_m1).zfill(5) or '') + '|' + str(fecha_emision_format or '') + '|' + str(
                ' ') + '|' + str(str(code_diario2).zfill(2) or '') + '|' + str(serie_factura_proveedor or '') + '|' + str('0') + '|' + str(
                correlativo_factura_proveedor or '') + '|' + str('') + '|' + str(code_doc or '') + '|' + str(proveedor[1] or '') + '|' + str(
                proveedor[2] or '') + '|' + str('%.2f' % monto_sin_igv or '') + '|' + str(
                '%.2f' % amount_tax or '') + '|' + str('0.00' or '') + '|' + str('0.00' or '') + '|' + str(
                inafecta or '') + '|' + str('0.00' or '') + '|' + str('0.00' or '') + '|' + str('0.00' or '') + '|' + str(
                '0.00' or '') + '|' + str('%.2f' % amount_total or '') + '|' + str(rate.name or '') + '|' + str(
                '%.3f' % fecha_cambio.tc_compra_rate or '') + '|' + str('01/01/0001') + '|' + str('00') + '|' + str('-') + '|' + str(
                ' ') + '|' + str('-') + '|' + str('01/01/0001') + '|' + str('0') + '|' + str('') + '|' + str(
                ' ') + '|' + str('') + '|' + str('') + '|' + str('') + '|' + str('') + '|' + str(
                '') + '|' + str('') + '|' + str(code_ajuste or '') + '|' + str('') + '\r\n'

        id_c = self.env['res.company']._company_default_get('account.registro.compras')
        company = self.env['res.company'].browse(id_c)
        # print (company.x_ruc)
        date_hasta = str(self.fecha_hasta).split('-')
        # print (date_hasta)
        mes_actual = date.today().strftime('%m')
        anio_actual = date.today().strftime('%Y')
        if int(date_hasta[0]) >= int(anio_actual):
            if int(date_hasta[1]) > int(mes_actual):
                raise Warning('El mes que ha elegido no debe ser mayo que actual!')
        nombre_archivo = 'LE'+str(company.x_ruc)+str(date_hasta[0])+str(date_hasta[1])+'00080100001111.txt'
        self.write({
            'txt_filename': nombre_archivo,
            'txt_binary': base64.encodestring(content)
        })
        print ('hola')
        return {
            'context': self.env.context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.registro.compras',
            'res_id': self.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    _name = 'account.registro.compras'
    # _description = ''

    txt_filename = fields.Char()
    txt_binary = fields.Binary()
    fecha_desde = fields.Date(string='Fecha Desde', default=date.today().strftime('%Y-%m-01'), required=True)
    fecha_hasta = fields.Date(string='Fecha Hasta', default=date.today().strftime('%Y-%m-%d'), required=True)



class account_registro_compras_nodomiciliadas(models.TransientModel):
    def generate_file1111(self):
        hoy = datetime.datetime.now()
        anio = hoy.year
        mes = hoy.month
        dia = hoy.day
        id_c = self.env['res.company']._company_default_get('account.registro.compras')
        company = self.env['res.company'].browse(id_c)
        nombre_archivo = 'LE' + str(company.x_ruc) + str(anio) + str(mes).zfill(2) + '00080200001011.txt'
        return nombre_archivo

    def generate_file22(self):
        content = '\r\n'
        return base64.encodestring(content)

    _name = 'account.registro.compras.nodomiciliadas'
    # _description = ''

    txt_filename = fields.Char(default=generate_file1111)
    txt_binary = fields.Binary(default=generate_file22)


class account_registro_ventas(models.TransientModel):

    @api.multi
    def generate_file_data2(self):
        self.ensure_one()
        content = ''

        id_c = self.env['res.company']._company_default_get('account.registro.ventas')
        company = self.env['res.company'].browse(id_c)
        # print (company.x_ruc)
        date_hasta = str(self.fecha_hasta).split('-')
        # print (date_hasta)
        mes_actual = date.today().strftime('%m')
        anio_actual = date.today().strftime('%Y')
        if int(date_hasta[0]) >= int(anio_actual):
            if int(date_hasta[1]) > int(mes_actual):
                raise Warning('El mes que ha elegido no debe ser mayo que actual!')
        nombre_archivo = 'LE' + str(company.x_ruc) + str(date_hasta[0]) + str(date_hasta[1]) + '00140100001111.txt'

        self.env.cr.execute("SELECT * FROM account_invoice "
                            "WHERE create_date BETWEEN %s AND %s "
                            "AND type = 'out_invoice' AND date_invoice <= (SELECT date_trunc('month',current_date) +'1month' - '1sec' ::INTERVAL) "
                            "AND state in ('open', 'cancel','anulado')"
                            "ORDER BY internal_number", (self.fecha_desde + ' 00:00:00', self.fecha_hasta + ' 23:59:59'))
        data = self.env.cr.dictfetchall()

        correlativo_m2 = 0
        spli_date_to = self.fecha_hasta.split('-')
        for f in data:
            correlativo = str(f['internal_number']).split('-')
            fecha_emision = datetime.datetime.strptime(str(f['date_invoice']), '%Y-%m-%d')
            fecha_emision_format = datetime.date.strftime(fecha_emision, "%d/%m/%Y")
            self.env.cr.execute("SELECT code "
                                "FROM account_journal WHERE id = %s ", [f['journal_id']])
            code_diario = int(self.env.cr.fetchone()[0])
            # print (code_diario)
            self.env.cr.execute("SELECT doc_type, doc_number, display_name "
                                "FROM res_partner WHERE id = %s ", [f['partner_id']])
            proveedor = self.env.cr.fetchone()

            if proveedor[0] and proveedor[1]:
                if str(f['state']) != 'cancel':
                    if str(proveedor[0]) == 'ruc':
                        code_doc = '6'
                        prov_anulado_name = proveedor[2]
                        prov_anulado_number_doc = proveedor[1]
                    elif str(proveedor[0] == 'dni'):
                        code_doc = '1'
                        prov_anulado_name = proveedor[2]
                        prov_anulado_number_doc = proveedor[1]
                    else:
                        code_doc = '0'
                        prov_anulado_name = proveedor[2]
                        prov_anulado_number_doc = proveedor[1]
                else:
                    if str(proveedor[0]) == 'ruc':
                        code_doc = '0'
                        prov_anulado_name = 'COMPROBANTE ANULADO'
                        prov_anulado_number_doc = '00000000000'
                    elif str(proveedor[0] == 'dni'):
                        code_doc = '0'
                        prov_anulado_name = 'COMPROBANTE ANULADO'
                        prov_anulado_number_doc = '00000000'
                    else:
                        code_doc = '0'
                        prov_anulado_name = 'COMPROBANTE ANULADO'
                        prov_anulado_number_doc = '00000000000'

            else:
                code_doc = '0'

            self.env.cr.execute("SELECT name, tc_compra, tc_venta "
                                "FROM res_currency WHERE id = %s ", [f['currency_id']])
            moneda = self.env.cr.fetchone()

            correlativo_m2 += 1

            invoice_line = self.env['account.invoice.line'].search([['invoice_id', '=', f['id']]], limit=1)
            monto_base_tax = sum(line.base for line in invoice_line.invoice_id.tax_line) or 0.0
            monto_tax = sum(line.amount for line in invoice_line.invoice_id.tax_line) or 0.0

            rate = self.env['res.currency'].search([['id','=',f['currency_id']]])
            rate_line = self.env['res.currency.rate'].search([['currency_id', '=', f['currency_id']]])

            for fecha_cambio in rate_line:
                if fecha_cambio.name == f['date_invoice']:
                    if str(f['state']) == 'cancel':
                        monto_sin_igv = 0.00
                        amount_tax = 0.00
                        amount_total = 0.00
                        code_ajuste = 2
                        inafecta = 0.00

                    else:
                        code_ajuste = 1
                        if invoice_line.invoice_id.tax_line:
                            inafecta = (invoice_line.invoice_id.amount_untaxed - monto_base_tax) * fecha_cambio.tc_venta_rate or 0.0
                            monto_sin_igv = monto_base_tax * fecha_cambio.tc_venta_rate
                            amount_tax = monto_tax * fecha_cambio.tc_venta_rate
                            amount_total = f['amount_total'] * fecha_cambio.tc_venta_rate
                        else:
                            inafecta = f['amount_total'] * fecha_cambio.tc_venta_rate
                            monto_sin_igv = 0.00
                            amount_tax = 0.00
                            amount_total = f['amount_total'] * fecha_cambio.tc_venta_rate
                    content += str(str(spli_date_to[0]+''+str(spli_date_to[1]).zfill(2)+'00')) + '|' + str('DEMO ' + str(spli_date_to[1]).zfill(2) + str(spli_date_to[0]) + str(f['id']).zfill(4) or '') + '|' + str('M02' + str(correlativo_m2).zfill(5) or '') + '|' + str(fecha_emision_format or '') + '|' + str(' ') + '|' + str(str(code_diario).zfill(2) or '') + '|' + str(correlativo[0] or '') + '|' + str(correlativo[1] or '') + '|' + str('') + '|' + str(code_doc or '') + '|' + str(prov_anulado_number_doc) + '|' + str(prov_anulado_name) + '|' + str('0.00') + '|' + str('%.2f' % monto_sin_igv) + '|' + str('0.00') + '|' + str('%.2f' % amount_tax) + '|' + str('0.00') + '|' + str('0.00') + '|' + str(inafecta or '0.00') + '|' + str('0.00') + '|' + str('0.00') + '|' + str('0.00') + '|' + str('0.00') + '|' + str('%.2f' % amount_total) + '|' + str(rate.name or '') + '|' + str('%.3f' % fecha_cambio.tc_venta_rate or '') + '|' + str('01/01/0001') + '|' + str('00') + '|' + str('-') + '|' + str('-') + '|' + str('') + '|' + str('') + '|' + str('') + '|' + str(code_ajuste or '') + '|' + str('') + '\r\n'

        notas_credito = self.env['einvoice.nota.credito'].search([['fecha_emision','>=', self.fecha_desde],['fecha_emision','<=', self.fecha_hasta]])

        for d2 in notas_credito:
            correlativo_nota = str(d2.numeracion).split('-')
            correlativo = str(d2.referencia.internal_number).split('-')
            fecha_emision_nota = datetime.datetime.strptime(str(d2.fecha_emision), '%Y-%m-%d')
            fecha_emision_format_nota = datetime.date.strftime(fecha_emision_nota, "%d/%m/%Y")
            fecha_emision1 = datetime.datetime.strptime(str(d2.referencia.date_invoice), '%Y-%m-%d')
            fecha_emision_format = datetime.date.strftime(fecha_emision1, "%d/%m/%Y")
            self.env.cr.execute("SELECT code "
                                "FROM account_journal WHERE id = %s ", [d2.referencia.journal_id.id])
            code_diario = int(self.env.cr.fetchone()[0])
            # print (code_diario)
            self.env.cr.execute("SELECT doc_type, doc_number, display_name "
                                "FROM res_partner WHERE id = %s ", [d2.referencia.partner_id.id])
            proveedor = self.env.cr.fetchone()

            if proveedor[0] and proveedor[1]:
                if str(proveedor[0]) == 'ruc':
                    code_doc = '6'
                    prov_anulado_name = proveedor[2]
                    prov_anulado_number_doc = proveedor[1]
                elif str(proveedor[0] == 'dni'):
                    code_doc = '1'
                    prov_anulado_name = proveedor[2]
                    prov_anulado_number_doc = proveedor[1]
                else:
                    code_doc = '0'
                    prov_anulado_name = proveedor[2]
                    prov_anulado_number_doc = proveedor[1]

            else:
                code_doc = '0'

            self.env.cr.execute("SELECT name, tc_compra, tc_venta "
                                "FROM res_currency WHERE id = %s ", [d2.referencia.currency_id.id])
            moneda = self.env.cr.fetchone()

            correlativo_m2 += 1

            invoice_line = self.env['account.invoice.line'].search([['invoice_id', '=', d2.referencia.id]], limit=1)
            monto_base_tax = sum(line.base for line in invoice_line.invoice_id.tax_line) or 0.0
            monto_tax = sum(line.amount for line in invoice_line.invoice_id.tax_line) or 0.0

            rate = self.env['res.currency'].search([['id', '=', d2.referencia.currency_id.id]])
            rate_line = self.env['res.currency.rate'].search([['currency_id', '=', d2.referencia.currency_id.id]])

            for fecha_cambio in rate_line:
                if fecha_cambio.name == d2.fecha_emision:
                    code_ajuste = 1
                    if invoice_line.invoice_id.tax_line:
                        inafecta = -((invoice_line.invoice_id.amount_untaxed - monto_base_tax) * fecha_cambio.tc_venta_rate) or 0.0
                        monto_sin_igv = -(monto_base_tax * fecha_cambio.tc_venta_rate)
                        amount_tax = -(monto_tax * fecha_cambio.tc_venta_rate)
                        amount_total = -(d2.referencia.amount_total * fecha_cambio.tc_venta_rate)
                    else:
                        inafecta = -(d2.referencia.amount_total * fecha_cambio.tc_venta_rate)
                        monto_sin_igv = 0.00
                        amount_tax = 0.00
                        amount_total = -(d2.referencia.amount_total * fecha_cambio.tc_venta_rate)

                    content += str(str(spli_date_to[0] + '' + str(spli_date_to[1]).zfill(2) + '00')) + '|' + str(
                        'DEMO ' + str(spli_date_to[1]).zfill(2) + str(spli_date_to[0]) + str(d2.referencia.id).zfill(
                            4) or '') + '|' + str('M02' + str(correlativo_m2).zfill(5) or '') + '|' + str(
                        fecha_emision_format_nota or '') + '|' + str(' ') + '|' + str(
                        str('7').zfill(2) or '') + '|' + str(correlativo_nota[0] or '') + '|' + str(
                        correlativo_nota[1] or '') + '|' + str('') + '|' + str(code_doc or '') + '|' + str(
                        prov_anulado_number_doc) + '|' + str(prov_anulado_name) + '|' + str('0.00') + '|' + str(
                        '%.2f' % monto_sin_igv) + '|' + str('0.00') + '|' + str('%.2f' % amount_tax) + '|' + str(
                        '0.00') + '|' + str('0.00') + '|' + str(inafecta or '0.00') + '|' + str('0.00') + '|' + str(
                        '0.00') + '|' + str('0.00') + '|' + str('0.00') + '|' + str('%.2f' % amount_total) + '|' + str(
                        rate.name or '') + '|' + str('%.3f' % fecha_cambio.tc_venta_rate or '') + '|' + str(
                        fecha_emision_format or '') + '|' + str(str(code_diario).zfill(2) or '') + '|' + str(correlativo[0] or '') + '|' + str(
                        correlativo[1] or '') + '|' + str('') + '|' + str(
                        '') + '|' + str('') + '|' + str(code_ajuste or '') + '|' + str('') + '\r\n'


        self.write({
            'txt_filename': nombre_archivo,
            'txt_binary': base64.encodestring(content)
        })


        return {
            'context': self.env.context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.registro.ventas',
            'res_id': self.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    _name = 'account.registro.ventas'
    # _description = ''

    txt_filename = fields.Char()
    txt_binary = fields.Binary()
    fecha_desde = fields.Date(string='Fecha Desde', default=date.today().strftime('%Y-%m-01'))
    fecha_hasta = fields.Date(string='Fecha Hasta', default=date.today().strftime('%Y-%m-%d'))


class account_registro_libro_diario(models.TransientModel):
    @api.multi
    def generate_file_data3(self):
        self.ensure_one()
        content = ''
        hoy = datetime.datetime.now()
        anio = hoy.year
        mes = hoy.month
        dia = hoy.day
        # datetime.today().strftime('%m-%d-%Y')
        # obj_facturas = self.env['account.invoice'].search([['type','=','in_invoice'],['create_date','<']])
        self.env.cr.execute("SELECT * FROM account_move WHERE create_date BETWEEN %s AND %s AND date <= (SELECT date_trunc('month',current_date) +'1month' - '1sec' ::INTERVAL) and state = 'posted' ORDER BY date", (self.fecha_desde + ' 00:00:00', self.fecha_hasta +' 23:59:59'))
        data = self.env.cr.dictfetchall()

        correlativo_m2 = 0

        spli_date_to = self.fecha_hasta.split('-')
        for f in data:
            correlativo_m2 += 1
            # self.env.cr.execute("SELECT * "
            #                     "FROM account_move_line WHERE move_id = %s ", [f['id']])
            # move_line = self.env.cr.dictfetchall()
            code_id = self.env['account.invoice'].search([['internal_number', '=', f['ref']]])
            # print (code_id)
            if str(code_id.type) == 'in_invoice':
                code_comprobante = int(code_id.tipo_factura.code)
                serie_comprobante = code_id.serie_factura_proveedor
                numero_comprobante = code_id.correlativo_factura_proveedor
            else:
                print (code_id.internal_number)
                code_comprobante = int(code_id.journal_id.code)
                internal_split = code_id.internal_number.split('-')
                serie_comprobante = internal_split[0]
                numero_comprobante = internal_split[1]
            move_line = self.env['account.move.line'].search([['move_id','=',f['id']]])

            for ml in move_line:
                haber = 0
                debe = 0
                if ml.move_id.journal_id.currency:
                    moneda = ml.move_id.journal_id.currency.name
                    haber = ml.credit
                    debe = ml.debit

                else:
                    moneda='PEN'
                    haber = ml.credit
                    debe = ml.debit

                if ml.move_id.partner_id.doc_type and ml.move_id.partner_id.doc_number:
                    if str(ml.move_id.partner_id.doc_type) == 'ruc':
                        code_doc = '6'
                    elif str(ml.move_id.partner_id.doc_type) == 'dni':
                        code_doc = '1'
                    else:
                        code_doc = '0'
                    doc_number = ml.move_id.partner_id.doc_number
                else:
                    code_doc = '0'
                    doc_number = ''


                date_invoice = str(ml.date).split('-')
                if int(mes) > int(date_invoice[1]):
                    code_ajuste = 8
                else:
                    code_ajuste = 1

                fecha1= datetime.datetime.strptime(str(ml.date), '%Y-%m-%d')
                fecha_format = datetime.date.strftime(fecha1, "%d/%m/%Y")
                fecha2 = datetime.datetime.strptime(str(ml.move_id.date), '%Y-%m-%d')
                fecha_format2 = datetime.date.strftime(fecha2, "%d/%m/%Y")
                fecha3 = datetime.datetime.strptime(str(ml.date_created), '%Y-%m-%d')
                fecha_format3 = datetime.date.strftime(fecha3, "%d/%m/%Y")

                content += str(str(spli_date_to[0]+''+str(spli_date_to[1]).zfill(2)+'00')) + '|' + str(f['ref'] or '') + '|' + str('M00' + str(correlativo_m2).zfill(5) or '') + '|' + str(ml.account_id.code or '') + '|' + str('') + '|' + str('') + '|' + str(moneda or '') + '|' + str(code_doc or '') + '|' + str(doc_number or '') + '|' + str(str(code_comprobante).zfill(2) or '') + '|' + str(serie_comprobante or '') + '|' + str(str(numero_comprobante).zfill(8) or '') + '|' + str(str(fecha_format3) or '') + '|' + str(str(fecha_format) or '') + '|' + str(str(fecha_format2) or '') + '|' + str(str(ml.name) or '') + '|' + str('') + '|' + str(debe) + '|' + str(haber) + '|' + str('') + '|' + str(code_ajuste or '') + '|' + str('') + '\r\n'

        id_c = self.env['res.company']._company_default_get('account.registro.libro.diario')
        company = self.env['res.company'].browse(id_c)
        # print (company.x_ruc)
        date_hasta = str(self.fecha_hasta).split('-')
        # print (date_hasta)
        mes_actual = date.today().strftime('%m')
        anio_actual = date.today().strftime('%Y')
        if int(date_hasta[0]) >= int(anio_actual):
            if int(date_hasta[1]) > int(mes_actual):
                raise Warning('El mes que ha elegido no debe ser mayo que actual!')
        nombre_archivo = 'LE' + str(company.x_ruc) + str(date_hasta[0]) + str(date_hasta[1]) + '00050200001111.txt'
        self.write({
            'txt_filename': nombre_archivo,
            'txt_binary': base64.encodestring(content)
        })

        return {
            'context': self.env.context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.registro.libro.diario',
            'res_id': self.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    _name = 'account.registro.libro.diario'
    # _description = ''

    txt_filename = fields.Char()
    txt_binary = fields.Binary()
    fecha_desde = fields.Date(string='Fecha Desde', default=date.today().strftime('%Y-%m-01'))
    fecha_hasta = fields.Date(string='Fecha Hasta', default=date.today().strftime('%Y-%m-%d'))
