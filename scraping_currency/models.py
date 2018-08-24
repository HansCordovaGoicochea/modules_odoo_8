# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import except_orm
import urllib2
from bs4 import BeautifulSoup
import time
# import datetime
import calendar
from datetime import datetime, date, timedelta

from openerp import tools

# from datetime import date, datetime, timedelta
# import time
import pytz


# clase para heredar el modulo de las tasas moneda
class scraping_currency(models.Model):
    _inherit = 'res.currency.rate'

    name = fields.Date('Date')

    rate_compra = fields.Float(string="Tasa Venta", digits=(12, 6), )
    tc_compra_rate = fields.Float(string="Precio Venta Soles", digits=(12, 6), )
    tc_venta_rate = fields.Float(string="Precio Compra Soles", digits=(12, 6), )

    _defaults = {
        'name': None
    }


# clase para heredar el modulo de monedas general
class scraping_currency(models.Model):

    _inherit = 'res.currency'

    ratio_silent_venta = fields.Float(string='Ratio Actual Venta', digits=(12,6), compute='_get_current_rate2', store= True)


    @api.model
    def _cron_periodic_button_verificar(self):
        self.button_verificar()

        # funcionar para traer los valores de compra y venta de sunat
    @api.multi
    def button_verificar(self):
        print ('Actualizandoooooooo tipo de cambio!')
        # print(self.id)
        # currency_br = self.env['res.currency'].browse(self.id)[0]
        currency_br = self.env['res.currency'].search([['name', '=', 'USD']], limit=1)[0]
        if currency_br.name.upper() != 'USD':
            raise except_orm(_('Error!'),
                             _("Por el momento solo funciona para Dolares (USD).\nDisculpa las Molestias :( "))
        else:
            url1 = "http://www.asesorempresarial.com/web/efinanzas-tipo-cambio.php"  # change to whatever your url is
            # url1 = "http://www.asesorempresarial.com/web/efinanzas-tipo-cambio.php?ano=2017&mes=1"  # change to whatever your url is
            page1 = urllib2.urlopen(url1).read()
            # print (page)
            soup1 = BeautifulSoup(page1, "lxml")
            mes_cambio = soup1.find_all('select', attrs={'id': 'mes'})[0].find_all('option', selected=True)
            anio_cambio = soup1.find_all('select', attrs={'id': 'ano'})[0].find_all('option', selected=True)

            array_meses = []
            for mc in mes_cambio:
                array_meses.append(int(mc['value']))
                array_meses.append(int(mc['value'])-1)
                mcambio = mc['value']
            for ac in anio_cambio:
                acambio = ac['value']
            # print(sorted(array_meses))
            for mes in sorted(array_meses):
                if mes == 0:
                    acambio = acambio - 1
                    mes = 12

                url = "http://www.asesorempresarial.com/web/efinanzas-tipo-cambio.php?ano=" + str(acambio) + "&mes=" + str(mes) + "&button2=Actualizar&type=#data"  # change to whatever your url is
                # print(url)
                # url = "http://www.asesorempresarial.com/web/efinanzas-tipo-cambio.php?ano=2018&mes=5&button2=Actualizar&type=#data"  # change to whatever your url is

                anio_i = url.find('ano=')
                anio_f = url.find('&')
                mes_i = url.find('mes=')
                mes_f = url.find('&button2')
                anio_cambio = url[anio_i + 4:anio_f]
                mes_cambio = url[mes_i + 4:mes_f]

                page = urllib2.urlopen(url).read()
                # print (page)
                soup = BeautifulSoup(page, "lxml")


                dias = []
                compra = []
                venta = []

                # for fila in soup.find_all(name='tr')[2:-8]:
                #     print 'ssssssssssssss'
                #     print fila
                #     cambio_dia = fila.findAll('td')[0].div.text.strip()
                #     cambio_compra = fila.findAll('td')[5].div.text.strip()
                #     cambio_venta = fila.findAll('td')[6].div.text.strip()
                #     dias.append(cambio_dia)
                #     compra.append(cambio_compra)
                #     venta.append(cambio_venta)
                for fila in soup.find_all(name='table')[15].find_all(name='tr')[2:-1]:
                    # print fila
                    cambio_dia = fila.findAll('td')[0].div.text.strip()
                    cambio_compra = fila.findAll('td')[5].div.text.strip()
                    cambio_venta = fila.findAll('td')[6].div.text.strip()
                    dias.append(cambio_dia)
                    compra.append(cambio_compra)
                    venta.append(cambio_venta)
                    # print (cambio_dia, cambio_compra, cambio_venta)
                # print (dias, compra, venta)
                # raise Warning('fdd')
                ini = -1
                for dia in dias:
                    ini += 1
                    f = str('%s-%s-%s') % (anio_cambio, str(mes_cambio).zfill(2), dia.zfill(2))
                    # print ('f', str(f))
                    # if self.name == f:
                    self._cr.execute(
                        """ DELETE FROM res_currency_rate WHERE name = %s""", [f])
                    slist = f.split("-")
                    sdate = date(int(slist[0]), int(slist[1]), int(slist[2]))
                    valor_soles_compra = 1 / float(compra[ini])
                    valor_soles_venta = 1 / float(venta[ini])
                    # print (f, valor_soles_compra, valor_soles_venta)

                    # guardar los valores en un diccionario para guardarlos
                    valores = {
                        'currency_id': currency_br.id,
                        'name': sdate,
                        'rate': valor_soles_compra,
                        'rate_compra': valor_soles_venta,
                        'tc_compra_rate': float(venta[ini]),
                        'tc_venta_rate': float(compra[ini]),
                    }
                    currency_br2 = self.env['res.currency'].search([['name', '=', 'PEN']], limit=1)[0]
                    valores2 = {
                        'currency_id': currency_br2.id,
                        'name': sdate,
                        'rate': 1,
                        'rate_compra': 1,
                        'tc_compra_rate': 1,
                        'tc_venta_rate': 1
                    }
                    # print (valores)
                    self.env['res.currency.rate'].create(valores)  # guardar los valores en la tabla directamente
                    self.env['res.currency.rate'].create(valores2)  # guardar los valores en la tabla directamente
            # print('-----compra--------')
            # print(compra)
            # print('-----venta--------')
            # print(currency_br.id)
            self._cr.execute(
                """ update res_currency set tc_compra = %s, tc_venta = %s WHERE id = 3""", (float(compra[-1]), float(venta[-1])))
            return self.write({'tc_compra': float(compra[-1]), 'tc_venta': float(venta[-1])})  # refrescar la pagina

    @api.one
    @api.depends('rate_ids')
    def _get_current_rate2(self, context=None):
        # print ('ghghgggfgfgfgf')
        if self.rate_ids:
            date = self._context.get('date') or time.strftime('%Y-%m-%d')
            self._cr.execute('SELECT rate_compra FROM res_currency_rate '
                       'WHERE currency_id = %s '
                         'AND name <= %s '
                       'ORDER BY name desc LIMIT 1',
                       (self.id, date))
            if self._cr.rowcount:
                self.ratio_silent_venta = self._cr.fetchone()[0]
            else:
                self.ratio_silent_venta = 0



class ir_cron(models.Model):
    # _name = 'new_module.new_module'
    _inherit = 'ir.cron'

    @api.model
    def create(self, vals):
        if 'nextcall' in vals:
            start = datetime.strptime(vals['nextcall'], "%Y-%m-%d %H:%M:%S") - timedelta(hours=5)
            tz = pytz.timezone('America/Bogota')
            start2 = tz.localize(start)
            tz_date = start2.strftime("%Y-%m-%d %H:%M:%S")
            vals['nextcall'] = tz_date

        return super(ir_cron, self).create(vals)

    @api.multi
    def write(self, vals):
        if 'nextcall' in vals:
            start = datetime.strptime(vals['nextcall'], "%Y-%m-%d %H:%M:%S") - timedelta(hours=5)
            tz = pytz.timezone('America/Bogota')
            start2 = tz.localize(start)
            tz_date = start2.strftime("%Y-%m-%d %H:%M:%S")
            vals['nextcall'] = tz_date

        return super(ir_cron, self).write(vals)
