# -*- coding: utf-8 -*-
from openerp import _, api, fields, models


class catalogo_tipo_documento_3(models.Model):
    _name = "catalogo.tipo.documento.3"
    _description = 'Catalogo T3'

    code = fields.Char(string='Codigo', size=4, select=True, required=True)
    name = fields.Char(string='Descripcion', size=255, select=True, required=True)

    @api.multi
    @api.depends('code', 'name')
    def name_get(self):
        result = []
        for table in self:
            l_name = table.code and table.code + ' - ' or ''
            l_name += table.name
            result.append((table.id, l_name))
        return result


class catalogo_tipo_via_5(models.Model):
    _name = "catalogo.tipo.via.5"
    _description = 'Catalogo T5'

    code = fields.Char(string='Codigo', size=4, select=True, required=True)
    name = fields.Char(string='Descripcion', size=255, select=True, required=True)
    
    @api.multi
    @api.depends('code', 'name')
    def name_get(self):
        result = []
        for table in self:
            l_name = table.code and table.code + ' - ' or ''
            l_name +=  table.name
            result.append((table.id, l_name ))
        return result


class catalogo_tipo_zona_6(models.Model):
    _name = "catalogo.tipo.zona.6"
    _description = 'Catalogo T6'

    code = fields.Char(string='Codigo', size=4, select=True, required=True)
    name = fields.Char(string='Descripcion', size=255, select=True, required=True)

    @api.multi
    @api.depends('code', 'name')
    def name_get(self):
        result = []
        for table in self:
            l_name = table.code and table.code + ' - ' or ''
            l_name += table.name
            result.append((table.id, l_name))
        return result


class catalogo_vinculo_familiar_19(models.Model):
    _name = "catalogo.vinculo.familiar.19"
    _description = 'Catalogo T19'

    code = fields.Char(string='Codigo', size=4, select=True, required=True)
    name = fields.Char(string='Descripcion', size=255, select=True, required=True)

    @api.multi
    @api.depends('code', 'name')
    def name_get(self):
        result = []
        for table in self:
            l_name = table.code and table.code + ' - ' or ''
            l_name += table.name
            result.append((table.id, l_name))
        return result


class catalogo_pais_emisor_documento_26(models.Model):
    _name = "catalogo.pais.emisor.documento.26"
    _description = 'Catalogo T26'

    code = fields.Char(string='Codigo', size=4, select=True, required=True)
    name = fields.Char(string='Descripcion', size=255, select=True, required=True)

    @api.multi
    @api.depends('code', 'name')
    def name_get(self):
        result = []
        for table in self:
            l_name = table.code and table.code + ' - ' or ''
            l_name += table.name
            result.append((table.id, l_name))
        return result


class catalogo_doc_acred_vinc_familiar_27(models.Model):
    _name = "catalogo.doc.acred.vinc.familiar.27"
    _description = 'Catalogo T27'

    code = fields.Char(string='Codigo', size=4, select=True, required=True)
    name = fields.Char(string='Descripcion', size=255, select=True, required=True)

    @api.multi
    @api.depends('code', 'name')
    def name_get(self):
        result = []
        for table in self:
            l_name = table.code and table.code + ' - ' or ''
            l_name += table.name
            result.append((table.id, l_name))
        return result


class catalogo_codigo_larga_distancia_nac_29(models.Model):
    _name = "catalogo.codigo.larga.distancia.nac.29"
    _description = 'Catalogo T29'

    code = fields.Char(string='Codigo', size=4, select=True, required=True)
    name = fields.Char(string='Descripcion', size=255, select=True, required=True)

    @api.multi
    @api.depends('code', 'name')
    def name_get(self):
        result = []
        for table in self:
            l_name = table.code and table.code + ' - ' or ''
            l_name += table.name
            result.append((table.id, l_name))
        return result


class catalogo_regimen_laboral_33(models.Model):
    _name = 'catalogo.regimen.laboral.33'
    # _rec_name = 'name'
    # _description = 'New Description'

    code = fields.Char('CÓDIGO')
    name = fields.Char('DESCRIPCIÓN')
    descripcion_abreviada = fields.Char('DESCRIPCIÓN ABREVIADA')
    sector_privado = fields.Char('SECTOR PRIVADO')
    sector_publico = fields.Char('SECTOR PUBLICO')
    otras_entidades = fields.Char('OTRAS ENTIDADES')

    @api.multi
    @api.depends('code', 'name')
    def name_get(self):
        result = []
        for table in self:
            l_name = table.code and table.code + ' - ' or ''
            l_name += table.name
            result.append((table.id, l_name))
        return result


class catalogo_situacion_educativa_9(models.Model):
    _name = 'catalogo.situacion.educativa.9'
    # _rec_name = 'name'
    # _description = 'New Description'

    code = fields.Char('CÓDIGO')
    name = fields.Char('DESCRIPCIÓN')
    descripcion_abreviada = fields.Char('DESCRIPCIÓN ABREVIADA')

    @api.multi
    @api.depends('code', 'name')
    def name_get(self):
        result = []
        for table in self:
            l_name = table.code and table.code + ' - ' or ''
            l_name += table.name
            result.append((table.id, l_name))
        return result


class catalogo_tipo_contrato_12(models.Model):
    _name = 'catalogo.tipo.contrato.12'
    # _rec_name = 'name'
    # _description = 'New Description'

    code = fields.Char('CÓDIGO')
    name = fields.Char('DESCRIPCIÓN')
    descripcion_abreviada = fields.Char('DESCRIPCIÓN ABREVIADA')

    @api.multi
    @api.depends('code', 'name')
    def name_get(self):
        result = []
        for table in self:
            l_name = table.code and table.code + ' - ' or ''
            l_name += table.name
            result.append((table.id, l_name))
        return result


class catalogo_ocupaciones_10(models.Model):
    _name = 'catalogo.ocupacion.10'
    # _rec_name = 'name'
    # _description = 'New Description'

    code = fields.Char('CÓDIGO')
    name = fields.Char('DESCRIPCIÓN')

    @api.multi
    @api.depends('code', 'name')
    def name_get(self):
        result = []
        for table in self:
            l_name = table.code and table.code + ' - ' or ''
            l_name += table.name
            result.append((table.id, l_name))
        return result


class catalogo_categoria_ocupacional_24(models.Model):
    _name = 'catalogo.categoria.ocupacional.24'
    # _rec_name = 'name'
    # _description = 'New Description'

    code = fields.Char('CÓDIGO')
    name = fields.Char('DESCRIPCIÓN')
    sector_privado = fields.Char('SECTOR PRIVADO')
    sector_publico = fields.Char('SECTOR PUBLICO')
    otras_entidades = fields.Char('OTRAS ENTIDADES')

    @api.multi
    @api.depends('code', 'name')
    def name_get(self):
        result = []
        for table in self:
            l_name = table.code and table.code + ' - ' or ''
            l_name += table.name
            result.append((table.id, l_name))
        return result


class catalogo_tipo_trabajador_8(models.Model):
    _name = 'catalogo.tipo.trabajador.8'
    # _rec_name = 'name'
    # _description = 'New Description'

    code = fields.Char('CÓDIGO')
    name = fields.Char('DESCRIPCIÓN')
    descripcion_abreviada = fields.Char('DESCRIPCIÓN ABREVIADA')
    sector_privado = fields.Char('SECTOR PRIVADO')
    sector_publico = fields.Char('SECTOR PUBLICO')
    otras_entidades = fields.Char('OTRAS ENTIDADES')

    @api.multi
    @api.depends('code', 'name')
    def name_get(self):
        result = []
        for table in self:
            l_name = table.code and table.code + ' - ' or ''
            l_name += table.name
            result.append((table.id, l_name))
        return result

class catalogo_nacionalidad_4(models.Model):
    _name = 'catalogo.nacionalidad.4'
    # _rec_name = 'name'
    # _description = 'New Description'

    code = fields.Char('CÓDIGO')
    name = fields.Char('DESCRIPCIÓN')

    @api.multi
    @api.depends('code', 'name')
    def name_get(self):
        result = []
        for table in self:
            l_name = table.code and table.code + ' - ' or ''
            l_name += table.name
            result.append((table.id, l_name))
        return result


class catalogo_motivo_baja_registro_17(models.Model):
    _name = 'catalogo.motivo.baja.registro.17'
    # _rec_name = 'name'
    # _description = 'New Description'

    code = fields.Char('CÓDIGO')
    name = fields.Char('DESCRIPCIÓN')
    descripcion_abreviada = fields.Char('DESCRIPCIÓN ABREVIADA')

    @api.multi
    @api.depends('code', 'name')
    def name_get(self):
        result = []
        for table in self:
            l_name = table.code and table.code + ' - ' or ''
            l_name += table.name
            result.append((table.id, l_name))
        return result


class catalogo_instituciones_educativas_34(models.Model):
    _name = 'catalogo.instituciones.educativas.34'
    # _rec_name = 'name'
    # _description = 'New Description'

    code_regimen = fields.Char('CÓDIGO REGIMEN')
    desc_regimen = fields.Char('DESCRIPCIÓN REGIMEN')
    code_tipo_inst = fields.Char('COD. TIPO INST.')
    desc_tipo_inst = fields.Char('DESC. TIPO INST.')
    cod_institucion = fields.Char('COD. INSTITUCION')
    desc_institucion = fields.Char('DESC. INSTITUCION')
    cod_carrera = fields.Char('COD. CARRERA')
    desc_carrera = fields.Char('DESC. CARRERA')

    @api.multi
    @api.depends('desc_institucion', 'desc_carrera')
    def name_get(self):
        result = []
        for table in self:
            l_name = table.desc_institucion and table.desc_institucion + ' - ' or ''
            l_name += table.desc_carrera
            result.append((table.id, l_name))
        return result


class catalogo_regimen_aseguramiento_32(models.Model):
    _name = 'catalogo.regimen.aseguramiento.32'
    # _rec_name = 'name'
    # _description = 'New Description'

    code = fields.Char('CÓDIGO')
    name = fields.Char('DESCRIPCIÓN')
    descripcion_abreviada = fields.Char('DESCRIPCIÓN ABREVIADA')

    @api.multi
    @api.depends('code', 'name')
    def name_get(self):
        result = []
        for table in self:
            l_name = table.code and table.code + ' - ' or ''
            l_name += table.name
            result.append((table.id, l_name))
        return result


class catalogo_regimen_pensionario_11(models.Model):
    _name = 'catalogo.regimen.pensionario.11'
    # _rec_name = 'name'
    # _description = 'New Description'

    code = fields.Char('CÓDIGO')
    name = fields.Char('DESCRIPCIÓN')
    descripcion_abreviada = fields.Char('DESCRIPCIÓN ABREVIADA')
    sector_privado = fields.Char('SECTOR PRIVADO')
    sector_publico = fields.Char('SECTOR PUBLICO')
    otras_entidades = fields.Char('OTRAS ENTIDADES')

    @api.multi
    @api.depends('code', 'name')
    def name_get(self):
        result = []
        for table in self:
            l_name = table.code and table.code + ' - ' or ''
            l_name += table.name
            result.append((table.id, l_name))
        return result


class catalogo_entidades_prestadoras_salud_14(models.Model):
    _name = 'catalogo.entidades.prestadoras.salud.14'
    _rec_name = 'name'
    # _description = 'New Description'

    code = fields.Char('CÓDIGO')
    ruc_entidad = fields.Char('RUC')
    name = fields.Char('DESCRIPCIÓN')

