# -*- coding: utf-8 -*-

from openerp import models, fields, api
from lxml import etree


class res_users(models.Model):
    _inherit = 'res.users'

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        res = models.Model.fields_view_get(self, cr, uid, view_id=view_id, view_type=view_type, context=context,
                                           toolbar=toolbar, submenu=submenu)
        if view_type == 'form':
            print ('usersssssssssssssssss',str(uid))
            doc = etree.XML(res['arch'])
            # if uid != 1:
            # comentar para pooder activar las caracteristicas generales del administrador
            # y poder hacer cambios
            # for r in range(0, 100, 1):
            #     for sheet in doc.xpath("//field[@name='in_group_"+str(r)+"']"):
            #         parent = sheet.getparent()
            #         index = parent.index(sheet)
            #         for child in sheet:
            #             parent.insert(index, child)
            #             index += 1
            #         parent.remove(sheet)
            #     res['arch'] = etree.tostring(doc)
            #
            # for sheet in doc.xpath(u"//separator[@string='Configuración técnica']"):
            #     parent = sheet.getparent()
            #     index = parent.index(sheet)
            #     for child in sheet:
            #         parent.insert(index, child)
            #         index += 1
            #     parent.remove(sheet)
            # res['arch'] = etree.tostring(doc)
            #
            # for sheet in doc.xpath("//separator[@string='Usabilidad']"):
            #     parent = sheet.getparent()
            #     index = parent.index(sheet)
            #     for child in sheet:
            #         parent.insert(index, child)
            #         index += 1
            #     parent.remove(sheet)
            # res['arch'] = etree.tostring(doc)
            #
            # for sheet in doc.xpath("//separator[@string='Otro']"):
            #     parent = sheet.getparent()
            #     index = parent.index(sheet)
            #     for child in sheet:
            #         parent.insert(index, child)
            #         index += 1
            #     parent.remove(sheet)
            # res['arch'] = etree.tostring(doc)
            #
            # for sheet in doc.xpath("//field[@name='sel_groups_3_4']"):
            #     parent = sheet.getparent()
            #     index = parent.index(sheet)
            #     for child in sheet:
            #         parent.insert(index, child)
            #         index += 1
            #     parent.remove(sheet)
            # res['arch'] = etree.tostring(doc)
            # for sheet in doc.xpath("//field[@name='sel_groups_23_24_25']"):
            #     parent = sheet.getparent()
            #     index = parent.index(sheet)
            #     for child in sheet:
            #         parent.insert(index, child)
            #         index += 1
            #     parent.remove(sheet)
            # res['arch'] = etree.tostring(doc)
            # for sheet in doc.xpath("//field[@name='sel_groups_5']"):
            #     parent = sheet.getparent()
            #     index = parent.index(sheet)
            #     for child in sheet:
            #         parent.insert(index, child)
            #         index += 1
            #     parent.remove(sheet)
            # res['arch'] = etree.tostring(doc)
            #
            # for sheet in doc.xpath("//field[@name='sel_groups_21']"):
            #     sheet.attrib['string'] = 'Chat'
            #     parent = sheet.getparent()
            #     index = parent.index(sheet)
            #     for child in sheet:
            #         parent.insert(index, child)
            #         index += 1
            #     # parent.remove(sheet)
            # res['arch'] = etree.tostring(doc)
        return res