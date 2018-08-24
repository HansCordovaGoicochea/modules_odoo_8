# -*- coding: utf-8 -*-
from __future__ import print_function

import logging
import os
import zipfile
from lxml import etree
from xml.dom import minidom
import base64

import requests
import suds
from jinja2 import defaults
from openerp import _, api, fields, models
from suds.wsse import *
import openerp.addons.decimal_precision as dp
from firmado.probando import Probando as credito
from firmado.probandodebito import ProbandoDebito as debito
from firmado.probandoBaja import ProbandoBaja as Comunicacionbaja
from firmado.probandoResumen import ProbandoResumen as ResumenDiario
from firmado.bar import BarCo
from envio.web import EnvioSunat
from envio.webCB import EnvioSunat as envioBaja
from envio.getStatus import getStatusSunat
from openerp.exceptions import except_orm, Warning
import time
import datetime
from datetime import datetime, date, time
import unicodedata

import sys

reload(sys)
sys.setdefaultencoding('utf-8')

from M2Crypto import BIO, EVP, RSA, X509, m2

doc = minidom.Document()


def pago(numero, id1, total, currency):
    # extUBLExtensions = doc.createElement('ext:UBLExtensions')
    extUBLExtension = doc.createElement('ext:UBLExtension')
    # extUBLExtensions.appendChild(extUBLExtension)
    extExtensionContent = doc.createElement('ext:ExtensionContent')
    extUBLExtension.appendChild(extExtensionContent)
    sacAdditionalInformation = doc.createElement('sac:AdditionalInformation')
    extExtensionContent.appendChild(sacAdditionalInformation)
    while numero >= 1:
        id = "1001"
        pago = id1
        sacAdditionalMonetaryTotal = doc.createElement('sac:AdditionalMonetaryTotal')
        cbcID = doc.createElement('cbc:ID')
        text = doc.createTextNode(id)
        cbcID.appendChild(text)
        sacAdditionalMonetaryTotal.appendChild(cbcID)
        cbcPayableAmount = doc.createElement('cbc:PayableAmount')
        cbcPayableAmount.setAttribute('currencyID', currency)
        text = doc.createTextNode(pago)
        cbcPayableAmount.appendChild(text)
        sacAdditionalMonetaryTotal.appendChild(cbcPayableAmount)
        sacAdditionalInformation.appendChild(sacAdditionalMonetaryTotal)
        numero = numero - 1

    # sacAdditionalProperty = doc.createElement('sac:AdditionalProperty')
    # sacAdditionalInformation.appendChild(sacAdditionalProperty)
    cbcID = doc.createElement('cbcID')
    text = doc.createTextNode(id1)
    cbcID.appendChild(text)
    # sacAdditionalProperty.appendChild(cbcID)
    cbcValue = doc.createElement('cbc:Value')
    text = doc.createTextNode(total)
    cbcValue.appendChild(text)
    # sacAdditionalProperty.appendChild(cbcValue)
    xml_str = extUBLExtension.toprettyxml(indent="  ")
    return xml_str


def firma(digestvalor, valorFirma, certificado):
    extUBLExtension = doc.createElement('ext:UBLExtension')
    extExtensionContent = doc.createElement('ext:ExtensionContent')
    extUBLExtension.appendChild(extExtensionContent)

    xml_str = extUBLExtension.toprettyxml(indent="", newl='')
    return xml_str


def declaracionFirma(id, identificacion, nombre, firma):
    cacSignature = doc.createElement('cac:Signature')
    cbcID = doc.createElement('cbc:ID')
    text = doc.createTextNode(id)
    cbcID.appendChild(text)
    cacSignature.appendChild(cbcID)
    cacSignatoreParty = doc.createElement('cac:SignatoryParty')
    cacSignature.appendChild(cacSignatoreParty)
    cacPartyIdentification = doc.createElement('cac:PartyIdentification')
    cacSignatoreParty.appendChild(cacPartyIdentification)
    cbcID = doc.createElement('cbc:ID')
    text = doc.createTextNode(identificacion)
    cbcID.appendChild(text)
    cacPartyIdentification.appendChild(cbcID)
    cacPartyName = doc.createElement('cac:PartyName')
    cacSignatoreParty.appendChild(cacPartyName)
    cbcName = doc.createElement('cbc:Name')
    # text = doc.createCDATASection(nombre)
    text = doc.createTextNode(nombre)
    cbcName.appendChild(text)
    cacPartyName.appendChild(cbcName)
    cacDigitalSignatureAttachment = doc.createElement('cac:DigitalSignatureAttachment')
    cacSignature.appendChild(cacDigitalSignatureAttachment)
    cacExternalReference = doc.createElement('cac:ExternalReference')
    cacDigitalSignatureAttachment.appendChild(cacExternalReference)
    cbcURI = doc.createElement('cbc:URI')
    text = doc.createTextNode(firma)
    cbcURI.appendChild(text)
    cacExternalReference.appendChild(cbcURI)
    xml_str = cacSignature.toprettyxml(indent="  ")
    return xml_str


def DatosProveedor(id, idAdicional, nombre, idDireccion, nombreCalle, nombreCiudad, nombreDepartamento, nombreDistrito,
                   nombreRegistro, codigoID):
    cacAccountingSupplierParty = doc.createElement('cac:AccountingSupplierParty')
    cbcCustomerAssignedAccountID = doc.createElement('cbc:CustomerAssignedAccountID')
    text = doc.createTextNode(id)
    cbcCustomerAssignedAccountID.appendChild(text)
    cacAccountingSupplierParty.appendChild(cbcCustomerAssignedAccountID)
    cbcAdditionalAccountID = doc.createElement('cbc:AdditionalAccountID')
    text = doc.createTextNode(idAdicional)
    cbcAdditionalAccountID.appendChild(text)
    cacAccountingSupplierParty.appendChild(cbcAdditionalAccountID)
    cacParty = doc.createElement('cac:Party')
    cacAccountingSupplierParty.appendChild(cacParty)
    cacPartyName = doc.createElement('cac:PartyName')
    cacParty.appendChild(cacPartyName)
    cbcName = doc.createElement('cbc:Name')
    # text = doc.createCDATASection(nombre)
    text = doc.createTextNode(nombre)
    cbcName.appendChild(text)
    cacPartyName.appendChild(cbcName)
    cacPostalAddress = doc.createElement('cac:PostalAddress')
    cacParty.appendChild(cacPostalAddress)
    cbcID = doc.createElement('cbc:ID')
    text = doc.createTextNode(idDireccion)
    cbcID.appendChild(text)
    cacPostalAddress.appendChild(cbcID)
    cbcStreetName = doc.createElement('cbc:StreetName')
    text = doc.createTextNode(nombreCalle)
    cbcStreetName.appendChild(text)
    cacPostalAddress.appendChild(cbcStreetName)
    cbcCitySubdivisionName = doc.createElement('cbc:CitySubdivisionName')
    text = doc.createTextNode(nombreCalle)
    cbcCitySubdivisionName.appendChild(text)
    cacPostalAddress.appendChild(cbcCitySubdivisionName)
    cbcCityName = doc.createElement('cbc:CityName')
    text = doc.createTextNode(nombreCiudad)
    cbcCityName.appendChild(text)
    cacPostalAddress.appendChild(cbcCityName)
    cbcCountrySubentity = doc.createElement('cbc:CountrySubentity')
    text = doc.createTextNode(nombreDepartamento)
    cbcCountrySubentity.appendChild(text)
    cacPostalAddress.appendChild(cbcCountrySubentity)
    cbcDistrict = doc.createElement('cbc:District')
    text = doc.createTextNode(nombreDistrito)
    cbcDistrict.appendChild(text)
    cacPostalAddress.appendChild(cbcDistrict)
    cacCountry = doc.createElement('cac:Country')
    cacPostalAddress.appendChild(cacCountry)
    cbcIdentificationCode = doc.createElement('cbc:IdentificationCode')
    text = doc.createTextNode(codigoID)
    cbcIdentificationCode.appendChild(text)
    cacCountry.appendChild(cbcIdentificationCode)
    cacPartyLegalEntity = doc.createElement('cac:PartyLegalEntity')
    cacParty.appendChild(cacPartyLegalEntity)
    cbcRegistrationName = doc.createElement('cbc:RegistrationName')
    # text = doc.createCDATASection(nombreRegistro)
    text = doc.createTextNode(nombreRegistro)
    cbcRegistrationName.appendChild(text)
    cacPartyLegalEntity.appendChild(cbcRegistrationName)
    xml_str = cacAccountingSupplierParty.toprettyxml(indent="  ")
    return xml_str


def UBLVersion():
    UBLVersion = doc.createElement('cbc:UBLVersionID')
    text = doc.createTextNode('2.0')
    UBLVersion.appendChild(text)
    xml_str = UBLVersion.toprettyxml(indent="  ")
    return xml_str


def customizationID():
    cbcCustomizationID = doc.createElement('cbc:CustomizationID')
    text = doc.createTextNode('1.0')
    cbcCustomizationID.appendChild(text)
    xml_str = cbcCustomizationID.toprettyxml(indent="  ")
    return xml_str


def id(id):
    cbcID = doc.createElement('cbc:ID')
    text = doc.createTextNode(id)
    cbcID.appendChild(text)
    xml_str = cbcID.toprettyxml(indent="  ")
    return xml_str


def issueDate(fecha):
    cbcIssueDate = doc.createElement('cbc:IssueDate')
    text = doc.createTextNode(fecha)
    cbcIssueDate.appendChild(text)
    xml_str = cbcIssueDate.toprettyxml(indent="  ")
    return xml_str


def ReferenceDate(fecha_doc):
    cbcReference = doc.createElement('cbc:ReferenceDate')
    text = doc.createTextNode(fecha_doc)
    cbcReference.appendChild(text)
    xml_str = cbcReference.toprettyxml(indent="  ")
    return xml_str


def issueDateComunicacion(fecha_baja):
    cbcIssueDate = doc.createElement('cbc:IssueDate')
    text = doc.createTextNode(fecha_baja)
    cbcIssueDate.appendChild(text)
    xml_str = cbcIssueDate.toprettyxml(indent="  ")
    return xml_str


def invoiceTypeCode():
    cbcInvoiceTypeCode = doc.createElement('cbc:InvoiceTypeCode')
    text = doc.createTextNode('01')
    cbcInvoiceTypeCode.appendChild(text)
    xml_str = cbcInvoiceTypeCode.toprettyxml(indent="  ")
    return xml_str


def documentCurrencyCode(currency):
    cbcDocumentCurrencyCode = doc.createElement('cbc:DocumentCurrencyCode')
    text = doc.createTextNode(currency)
    cbcDocumentCurrencyCode.appendChild(text)
    xml_str = cbcDocumentCurrencyCode.toprettyxml(indent="  ")
    return xml_str


def DatosCliente(id, idAdicional, nombre):
    cacAccountingCustomerParty = doc.createElement('cac:AccountingCustomerParty')
    cbcCustomerAssignedAccountID = doc.createElement('cbc:CustomerAssignedAccountID')
    text = doc.createTextNode(id)
    cbcCustomerAssignedAccountID.appendChild(text)
    cacAccountingCustomerParty.appendChild(cbcCustomerAssignedAccountID)
    cbcAdditionalAccountID = doc.createElement('cbc:AdditionalAccountID')
    text = doc.createTextNode(idAdicional)
    cbcAdditionalAccountID.appendChild(text)
    cacAccountingCustomerParty.appendChild(cbcAdditionalAccountID)
    cacParty = doc.createElement('cac:Party')
    cacAccountingCustomerParty.appendChild(cacParty)
    cacPartyLegalEntity = doc.createElement('cac:PartyLegalEntity')
    cacParty.appendChild(cacPartyLegalEntity)
    cbcRegistrationName = doc.createElement('cbc:RegistrationName')
    text = doc.createTextNode(nombre)
    cbcRegistrationName.appendChild(text)
    cacPartyLegalEntity.appendChild(cbcRegistrationName)
    xml_str = cacAccountingCustomerParty.toprettyxml(indent="  ")
    return xml_str


def sumatoriaIGV(monto, currency):
    cacTaxTotal = doc.createElement('cac:TaxTotal')
    cbcTaxAmount = doc.createElement('cbc:TaxAmount')
    cbcTaxAmount.setAttribute('currencyID', currency)
    text = doc.createTextNode(monto)
    cbcTaxAmount.appendChild(text)
    cacTaxTotal.appendChild(cbcTaxAmount)
    cacTaxSubtotal = doc.createElement('cac:TaxSubtotal')
    cacTaxTotal.appendChild(cacTaxSubtotal)
    cbcTaxAmount = doc.createElement('cbc:TaxAmount')
    cbcTaxAmount.setAttribute('currencyID', currency)
    text = doc.createTextNode(monto)
    cbcTaxAmount.appendChild(text)
    cacTaxSubtotal.appendChild(cbcTaxAmount)
    cacTaxCategory = doc.createElement('cac:TaxCategory')
    cacTaxSubtotal.appendChild(cacTaxCategory)
    cacTaxScheme = doc.createElement('cac:TaxScheme')
    cacTaxCategory.appendChild(cacTaxScheme)
    cbcID = doc.createElement('cbc:ID')
    text = doc.createTextNode('1000')
    cbcID.appendChild(text)
    cacTaxScheme.appendChild(cbcID)
    cbcName = doc.createElement('cbc:Name')
    text = doc.createTextNode('IGV')
    cbcName.appendChild(text)
    cacTaxScheme.appendChild(cbcName)
    # cbcTaxTypeCode = doc.createElement('cbc:TaxTypeCode')
    # text = doc.createTextNode('VAT')
    # cbcTaxTypeCode.appendChild(text)
    # cacTaxScheme.appendChild(cbcTaxTypeCode)
    xml_str = cacTaxTotal.toprettyxml(indent="  ")
    return xml_str


def importeTotal(monto, currency):
    cacLegalMonetaryTotal = doc.createElement('cac:LegalMonetaryTotal')
    cbcPayableAmount = doc.createElement('cbc:PayableAmount')
    cbcPayableAmount.setAttribute('currencyID', currency)
    text = doc.createTextNode(monto)
    cbcPayableAmount.appendChild(text)
    cacLegalMonetaryTotal.appendChild(cbcPayableAmount)
    xml_str = cacLegalMonetaryTotal.toprettyxml(indent="  ")
    return xml_str


def importeTotaldebito(monto, currency):
    cacLegalMonetaryTotal = doc.createElement('cac:RequestedMonetaryTotal')
    cbcPayableAmount = doc.createElement('cbc:PayableAmount')
    cbcPayableAmount.setAttribute('currencyID', currency)
    text = doc.createTextNode(monto)
    cbcPayableAmount.appendChild(text)
    cacLegalMonetaryTotal.appendChild(cbcPayableAmount)
    xml_str = cacLegalMonetaryTotal.toprettyxml(indent="  ")
    return xml_str


def datosProducto(nombre, identificacion):
    cacItem = doc.createElement('cac:Item')
    cbcDescription = doc.createElement('cbc:Description')
    text = doc.createTextNode(nombre)
    cbcDescription.appendChild(text)
    cacItem.appendChild(cbcDescription)
    cacSellersItemIdentification = doc.createElement('cac:SellersItemIdentification')
    cacItem.appendChild(cacSellersItemIdentification)
    cbcID = doc.createElement('cbc:ID')
    text = doc.createTextNode(identificacion)
    cbcID.appendChild(text)
    cacSellersItemIdentification.appendChild(cbcID)
    xml_str = cacItem.toprettyxml(indent="  ")
    return xml_str


def lineas_comunicacion(nro, tipo, serie, correlativo, motivo):
    cacItem = doc.createElement('sac:VoidedDocumentsLine')
    cbcLine = doc.createElement('cbc:LineID')
    text = doc.createTextNode(nro)
    cbcLine.appendChild(text)
    cacItem.appendChild(cbcLine)
    cbcTipo = doc.createElement('cbc:DocumentTypeCode')
    text = doc.createTextNode(tipo)
    cbcTipo.appendChild(text)
    cacItem.appendChild(cbcTipo)
    cbcSerie = doc.createElement('sac:DocumentSerialID')
    text = doc.createTextNode(serie)
    cbcSerie.appendChild(text)
    cacItem.appendChild(cbcSerie)
    cbcCorrelativo = doc.createElement('sac:DocumentNumberID')
    text = doc.createTextNode(correlativo)
    cbcCorrelativo.appendChild(text)
    cacItem.appendChild(cbcCorrelativo)
    cbcMotivo = doc.createElement('sac:VoidReasonDescription')

    text = doc.createTextNode(motivo)
    cbcMotivo.appendChild(text)
    cacItem.appendChild(cbcMotivo)

    xml_str = cacItem.toprettyxml(indent="  ")
    return xml_str


def lineas_resumen(nro, tipo, serie, correlativo_inicio, correlativo_fin, monto_total, total_gravadas, total_exoneradas,
                   total_inafectas, sumatoria_otros, tax_isc_total, tax_igv_total, tax_otros_total, currency):
    cacItem = doc.createElement('sac:SummaryDocumentsLine')
    cbcLine = doc.createElement('cbc:LineID')
    text = doc.createTextNode(nro)
    cbcLine.appendChild(text)
    cacItem.appendChild(cbcLine)
    cbcTipo = doc.createElement('cbc:DocumentTypeCode')
    text = doc.createTextNode(tipo)
    cbcTipo.appendChild(text)
    cacItem.appendChild(cbcTipo)
    cbcSerie = doc.createElement('sac:DocumentSerialID')
    text = doc.createTextNode(serie)
    cbcSerie.appendChild(text)
    cacItem.appendChild(cbcSerie)
    cbcCorrelativoInicio = doc.createElement('sac:StartDocumentNumberID')
    text = doc.createTextNode(correlativo_inicio)
    cbcCorrelativoInicio.appendChild(text)
    cacItem.appendChild(cbcCorrelativoInicio)
    cbcCorrelativoFin = doc.createElement('sac:EndDocumentNumberID')
    text = doc.createTextNode(correlativo_fin)
    cbcCorrelativoFin.appendChild(text)
    cacItem.appendChild(cbcCorrelativoFin)
    TotalAmount = doc.createElement('sac:TotalAmount')
    TotalAmount.setAttribute('currencyID', currency)
    text = doc.createTextNode(monto_total)
    TotalAmount.appendChild(text)
    cacItem.appendChild(TotalAmount)

    sacBillingPayment = doc.createElement('sac:BillingPayment')
    cacItem.appendChild(sacBillingPayment)
    PaidAmount = doc.createElement('cbc:PaidAmount')
    PaidAmount.setAttribute('currencyID', currency)
    text = doc.createTextNode(total_gravadas)
    PaidAmount.appendChild(text)
    sacBillingPayment.appendChild(PaidAmount)
    InstructionID = doc.createElement('cbc:InstructionID')
    text = doc.createTextNode('01')
    InstructionID.appendChild(text)
    sacBillingPayment.appendChild(InstructionID)

    sacBillingPayment2 = doc.createElement('sac:BillingPayment')
    cacItem.appendChild(sacBillingPayment2)
    PaidAmount2 = doc.createElement('cbc:PaidAmount')
    PaidAmount2.setAttribute('currencyID', currency)
    text = doc.createTextNode(total_exoneradas)
    PaidAmount2.appendChild(text)
    sacBillingPayment2.appendChild(PaidAmount2)
    InstructionID2 = doc.createElement('cbc:InstructionID')
    text = doc.createTextNode('02')
    InstructionID2.appendChild(text)
    sacBillingPayment2.appendChild(InstructionID2)

    sacBillingPayment3 = doc.createElement('sac:BillingPayment')
    cacItem.appendChild(sacBillingPayment3)
    PaidAmount3 = doc.createElement('cbc:PaidAmount')
    PaidAmount3.setAttribute('currencyID', currency)
    text = doc.createTextNode(total_inafectas)
    PaidAmount3.appendChild(text)
    sacBillingPayment3.appendChild(PaidAmount3)
    InstructionID3 = doc.createElement('cbc:InstructionID')
    text = doc.createTextNode('03')
    InstructionID3.appendChild(text)
    sacBillingPayment3.appendChild(InstructionID3)

    AllowanceCharge = doc.createElement('cac:AllowanceCharge')
    cacItem.appendChild(AllowanceCharge)
    ChargeIndicator = doc.createElement('cbc:ChargeIndicator')
    text = doc.createTextNode('true')
    ChargeIndicator.appendChild(text)
    AllowanceCharge.appendChild(ChargeIndicator)
    Amount = doc.createElement('cbc:Amount')
    Amount.setAttribute('currencyID', currency)
    text = doc.createTextNode(sumatoria_otros)
    Amount.appendChild(text)
    AllowanceCharge.appendChild(Amount)

    cacTaxTotal = doc.createElement('cac:TaxTotal')
    cacItem.appendChild(cacTaxTotal)
    cbcTaxAmount = doc.createElement('cbc:TaxAmount')
    cbcTaxAmount.setAttribute('currencyID', currency)
    text = doc.createTextNode(tax_isc_total)
    cbcTaxAmount.appendChild(text)
    cacTaxTotal.appendChild(cbcTaxAmount)
    cacTaxSubtotal = doc.createElement('cac:TaxSubtotal')
    cacTaxTotal.appendChild(cacTaxSubtotal)
    cbcTaxAmount = doc.createElement('cbc:TaxAmount')
    cbcTaxAmount.setAttribute('currencyID', currency)
    text = doc.createTextNode(tax_isc_total)
    cbcTaxAmount.appendChild(text)
    cacTaxSubtotal.appendChild(cbcTaxAmount)
    cacTaxCategory = doc.createElement('cac:TaxCategory')
    cacTaxSubtotal.appendChild(cacTaxCategory)
    cacTaxScheme = doc.createElement('cac:TaxScheme')
    cacTaxCategory.appendChild(cacTaxScheme)
    cbcID = doc.createElement('cbc:ID')
    text = doc.createTextNode('2000')
    cbcID.appendChild(text)
    cacTaxScheme.appendChild(cbcID)
    cbcName = doc.createElement('cbc:Name')
    text = doc.createTextNode('ISC')
    cbcName.appendChild(text)
    cacTaxScheme.appendChild(cbcName)
    cbcTaxTypeCode = doc.createElement('cbc:TaxTypeCode')
    text = doc.createTextNode('EXC')
    cbcTaxTypeCode.appendChild(text)
    cacTaxScheme.appendChild(cbcTaxTypeCode)

    cacTaxTotal = doc.createElement('cac:TaxTotal')
    cacItem.appendChild(cacTaxTotal)
    cbcTaxAmount = doc.createElement('cbc:TaxAmount')
    cbcTaxAmount.setAttribute('currencyID', currency)
    print('>>>>>>>>>>', str(total_gravadas))
    if total_gravadas == '0.0':
        text = doc.createTextNode('0.0')
    else:
        text = doc.createTextNode(tax_igv_total)
    cbcTaxAmount.appendChild(text)
    cacTaxTotal.appendChild(cbcTaxAmount)
    cacTaxSubtotal = doc.createElement('cac:TaxSubtotal')
    cacTaxTotal.appendChild(cacTaxSubtotal)
    cbcTaxAmount = doc.createElement('cbc:TaxAmount')
    cbcTaxAmount.setAttribute('currencyID', currency)
    if total_gravadas == '0.0':
        text = doc.createTextNode('0.0')
    else:
        text = doc.createTextNode(tax_igv_total)
    cbcTaxAmount.appendChild(text)
    cacTaxSubtotal.appendChild(cbcTaxAmount)
    cacTaxCategory = doc.createElement('cac:TaxCategory')
    cacTaxSubtotal.appendChild(cacTaxCategory)
    cacTaxScheme = doc.createElement('cac:TaxScheme')
    cacTaxCategory.appendChild(cacTaxScheme)
    cbcID = doc.createElement('cbc:ID')
    text = doc.createTextNode('1000')
    cbcID.appendChild(text)
    cacTaxScheme.appendChild(cbcID)
    cbcName = doc.createElement('cbc:Name')
    text = doc.createTextNode('IGV')
    cbcName.appendChild(text)
    cacTaxScheme.appendChild(cbcName)
    cbcTaxTypeCode = doc.createElement('cbc:TaxTypeCode')
    text = doc.createTextNode('VAT')
    cbcTaxTypeCode.appendChild(text)
    cacTaxScheme.appendChild(cbcTaxTypeCode)

    cacTaxTotal = doc.createElement('cac:TaxTotal')
    cacItem.appendChild(cacTaxTotal)
    cbcTaxAmount = doc.createElement('cbc:TaxAmount')
    cbcTaxAmount.setAttribute('currencyID', currency)
    text = doc.createTextNode(tax_otros_total)
    cbcTaxAmount.appendChild(text)
    cacTaxTotal.appendChild(cbcTaxAmount)
    cacTaxSubtotal = doc.createElement('cac:TaxSubtotal')
    cacTaxTotal.appendChild(cacTaxSubtotal)
    cbcTaxAmount = doc.createElement('cbc:TaxAmount')
    cbcTaxAmount.setAttribute('currencyID', currency)
    text = doc.createTextNode(tax_otros_total)
    cbcTaxAmount.appendChild(text)
    cacTaxSubtotal.appendChild(cbcTaxAmount)
    cacTaxCategory = doc.createElement('cac:TaxCategory')
    cacTaxSubtotal.appendChild(cacTaxCategory)
    cacTaxScheme = doc.createElement('cac:TaxScheme')
    cacTaxCategory.appendChild(cacTaxScheme)
    cbcID = doc.createElement('cbc:ID')
    text = doc.createTextNode('9999')
    cbcID.appendChild(text)
    cacTaxScheme.appendChild(cbcID)
    cbcName = doc.createElement('cbc:Name')
    text = doc.createTextNode('OTROS')
    cbcName.appendChild(text)
    cacTaxScheme.appendChild(cbcName)
    cbcTaxTypeCode = doc.createElement('cbc:TaxTypeCode')
    text = doc.createTextNode('OTH')
    cbcTaxTypeCode.appendChild(text)
    cacTaxScheme.appendChild(cbcTaxTypeCode)

    xml_str = cacItem.toprettyxml(indent="  ")
    return xml_str


def precioProducto(precio, currency):
    cacPrice = doc.createElement('cac:Price')
    cbcPriceAmount = doc.createElement('cbc:PriceAmount')
    cbcPriceAmount.setAttribute('currencyID', currency)
    text = doc.createTextNode(precio)
    cbcPriceAmount.appendChild(text)
    cacPrice.appendChild(cbcPriceAmount)
    xml_str = cacPrice.toprettyxml(indent="  ")
    return xml_str


def Producto(idP, cantidad, montoT, monto, nombre, identificacion, precio, currency):
    cacInvoiceLine = doc.createElement('cac:CreditNoteLine')
    cbcID = doc.createElement('cbc:ID')
    text = doc.createTextNode(idP)
    cbcID.appendChild(text)
    cacInvoiceLine.appendChild(cbcID)
    cbcInvoiceQuantity = doc.createElement('cbc:CreditedQuantity')
    cbcInvoiceQuantity.setAttribute('unitCode', 'NIU')
    text = doc.createTextNode(cantidad)
    cbcInvoiceQuantity.appendChild(text)
    cacInvoiceLine.appendChild(cbcInvoiceQuantity)
    cbcLineExtensionAmount = doc.createElement('cbc:LineExtensionAmount')
    cbcLineExtensionAmount.setAttribute('currencyID', currency)
    text = doc.createTextNode(montoT)
    cbcLineExtensionAmount.appendChild(text)
    cacInvoiceLine.appendChild(cbcLineExtensionAmount)
    cacPricingReference = doc.createElement('cac:PricingReference')
    cacInvoiceLine.appendChild(cacPricingReference)
    cacAlternativeConditionPrice = doc.createElement('cac:AlternativeConditionPrice')
    cacPricingReference.appendChild(cacAlternativeConditionPrice)
    cbcPriceAmount = doc.createElement('cbc:PriceAmount')
    cbcPriceAmount.setAttribute('currencyID', currency)
    text = doc.createTextNode(montoT)
    cbcPriceAmount.appendChild(text)
    cacAlternativeConditionPrice.appendChild(cbcPriceAmount)
    cbcPriceTypeCode = doc.createElement('cbc:PriceTypeCode')
    text = doc.createTextNode('01')
    cbcPriceTypeCode.appendChild(text)
    cacAlternativeConditionPrice.appendChild(cbcPriceTypeCode)

    cacTaxTotal = doc.createElement('cac:TaxTotal')
    cacInvoiceLine.appendChild(cacTaxTotal)
    cbcTaxAmount = doc.createElement('cbc:TaxAmount')
    cbcTaxAmount.setAttribute('currencyID', currency)
    text = doc.createTextNode(monto)
    cbcTaxAmount.appendChild(text)
    cacTaxTotal.appendChild(cbcTaxAmount)
    cacTaxSubtotal = doc.createElement('cac:TaxSubtotal')
    cacTaxTotal.appendChild(cacTaxSubtotal)
    cbcTaxAmount = doc.createElement('cbc:TaxAmount')
    cbcTaxAmount.setAttribute('currencyID', currency)
    text = doc.createTextNode(monto)
    cbcTaxAmount.appendChild(text)
    cacTaxSubtotal.appendChild(cbcTaxAmount)
    cacTaxCategory = doc.createElement('cac:TaxCategory')
    cacTaxSubtotal.appendChild(cacTaxCategory)
    cbcTaxExemptionReasonCode = doc.createElement('cbc:TaxExemptionReasonCode')
    text = doc.createTextNode('10')
    cbcTaxExemptionReasonCode.appendChild(text)
    cacTaxCategory.appendChild(cbcTaxExemptionReasonCode)
    cacTaxScheme = doc.createElement('cac:TaxScheme')
    cacTaxCategory.appendChild(cacTaxScheme)
    cbcID = doc.createElement('cbc:ID')
    text = doc.createTextNode('1000')
    cbcID.appendChild(text)
    cacTaxScheme.appendChild(cbcID)
    cbcName = doc.createElement('cbc:Name')
    text = doc.createTextNode('IGV')
    cbcName.appendChild(text)
    cacTaxScheme.appendChild(cbcName)
    cbcTaxTypeCode = doc.createElement('cbc:TaxTypeCode')
    text = doc.createTextNode('VAT')
    cbcTaxTypeCode.appendChild(text)
    cacTaxScheme.appendChild(cbcTaxTypeCode)

    cacItem = doc.createElement('cac:Item')
    cacInvoiceLine.appendChild(cacItem)
    cbcDescription = doc.createElement('cbc:Description')
    text = doc.createTextNode(nombre)
    cbcDescription.appendChild(text)
    cacItem.appendChild(cbcDescription)
    cacSellersItemIdentification = doc.createElement('cac:SellersItemIdentification')
    cacItem.appendChild(cacSellersItemIdentification)
    cbcID = doc.createElement('cbc:ID')
    text = doc.createTextNode(identificacion)
    cbcID.appendChild(text)
    cacSellersItemIdentification.appendChild(cbcID)

    cacPrice = doc.createElement('cac:Price')
    cbcPriceAmount = doc.createElement('cbc:PriceAmount')
    cbcPriceAmount.setAttribute('currencyID', currency)
    text = doc.createTextNode(precio)
    cbcPriceAmount.appendChild(text)
    cacPrice.appendChild(cbcPriceAmount)

    cacPrice = doc.createElement('cac:Price')
    cacInvoiceLine.appendChild(cacPrice)
    cbcPriceAmount = doc.createElement('cbc:PriceAmount')
    cbcPriceAmount.setAttribute('currencyID', currency)
    text = doc.createTextNode(precio)
    cbcPriceAmount.appendChild(text)
    cacPrice.appendChild(cbcPriceAmount)

    xml_str = cacInvoiceLine.toprettyxml(indent="  ")
    return xml_str


def Productodebito(idP, cantidad, montoT, monto, nombre, identificacion, precio, currency):
    cacInvoiceLine = doc.createElement('cac:DebitNoteLine')
    cbcID = doc.createElement('cbc:ID')
    text = doc.createTextNode(idP)
    cbcID.appendChild(text)
    cacInvoiceLine.appendChild(cbcID)
    cbcInvoiceQuantity = doc.createElement('cbc:DebitedQuantity')
    cbcInvoiceQuantity.setAttribute('unitCode', 'NIU')
    text = doc.createTextNode(cantidad)
    cbcInvoiceQuantity.appendChild(text)
    cacInvoiceLine.appendChild(cbcInvoiceQuantity)
    cbcLineExtensionAmount = doc.createElement('cbc:LineExtensionAmount')
    cbcLineExtensionAmount.setAttribute('currencyID', currency)
    text = doc.createTextNode(montoT)
    cbcLineExtensionAmount.appendChild(text)
    cacInvoiceLine.appendChild(cbcLineExtensionAmount)
    cacPricingReference = doc.createElement('cac:PricingReference')
    cacInvoiceLine.appendChild(cacPricingReference)
    cacAlternativeConditionPrice = doc.createElement('cac:AlternativeConditionPrice')
    cacPricingReference.appendChild(cacAlternativeConditionPrice)
    cbcPriceAmount = doc.createElement('cbc:PriceAmount')
    cbcPriceAmount.setAttribute('currencyID', currency)
    text = doc.createTextNode(montoT)
    cbcPriceAmount.appendChild(text)
    cacAlternativeConditionPrice.appendChild(cbcPriceAmount)
    cbcPriceTypeCode = doc.createElement('cbc:PriceTypeCode')
    text = doc.createTextNode('01')
    cbcPriceTypeCode.appendChild(text)
    cacAlternativeConditionPrice.appendChild(cbcPriceTypeCode)

    cacTaxTotal = doc.createElement('cac:TaxTotal')
    cacInvoiceLine.appendChild(cacTaxTotal)
    cbcTaxAmount = doc.createElement('cbc:TaxAmount')
    cbcTaxAmount.setAttribute('currencyID', currency)
    text = doc.createTextNode(monto)
    cbcTaxAmount.appendChild(text)
    cacTaxTotal.appendChild(cbcTaxAmount)
    cacTaxSubtotal = doc.createElement('cac:TaxSubtotal')
    cacTaxTotal.appendChild(cacTaxSubtotal)
    cbcTaxAmount = doc.createElement('cbc:TaxAmount')
    cbcTaxAmount.setAttribute('currencyID', currency)
    text = doc.createTextNode(monto)
    cbcTaxAmount.appendChild(text)
    cacTaxSubtotal.appendChild(cbcTaxAmount)
    cacTaxCategory = doc.createElement('cac:TaxCategory')
    cacTaxSubtotal.appendChild(cacTaxCategory)
    cbcTaxExemptionReasonCode = doc.createElement('cbc:TaxExemptionReasonCode')
    text = doc.createTextNode('10')
    cbcTaxExemptionReasonCode.appendChild(text)
    cacTaxCategory.appendChild(cbcTaxExemptionReasonCode)
    cacTaxScheme = doc.createElement('cac:TaxScheme')
    cacTaxCategory.appendChild(cacTaxScheme)
    cbcID = doc.createElement('cbc:ID')
    text = doc.createTextNode('1000')
    cbcID.appendChild(text)
    cacTaxScheme.appendChild(cbcID)
    cbcName = doc.createElement('cbc:Name')
    text = doc.createTextNode('IGV')
    cbcName.appendChild(text)
    cacTaxScheme.appendChild(cbcName)
    cbcTaxTypeCode = doc.createElement('cbc:TaxTypeCode')
    text = doc.createTextNode('VAT')
    cbcTaxTypeCode.appendChild(text)
    cacTaxScheme.appendChild(cbcTaxTypeCode)

    cacItem = doc.createElement('cac:Item')
    cacInvoiceLine.appendChild(cacItem)
    cbcDescription = doc.createElement('cbc:Description')
    text = doc.createTextNode(nombre)
    cbcDescription.appendChild(text)
    cacItem.appendChild(cbcDescription)
    cacSellersItemIdentification = doc.createElement('cac:SellersItemIdentification')
    cacItem.appendChild(cacSellersItemIdentification)
    cbcID = doc.createElement('cbc:ID')
    text = doc.createTextNode(identificacion)
    cbcID.appendChild(text)
    cacSellersItemIdentification.appendChild(cbcID)

    cacPrice = doc.createElement('cac:Price')
    cbcPriceAmount = doc.createElement('cbc:PriceAmount')
    cbcPriceAmount.setAttribute('currencyID', currency)
    text = doc.createTextNode(precio)
    cbcPriceAmount.appendChild(text)
    cacPrice.appendChild(cbcPriceAmount)

    cacPrice = doc.createElement('cac:Price')
    cacInvoiceLine.appendChild(cacPrice)
    cbcPriceAmount = doc.createElement('cbc:PriceAmount')
    cbcPriceAmount.setAttribute('currencyID', currency)
    text = doc.createTextNode(precio)
    cbcPriceAmount.appendChild(text)
    cacPrice.appendChild(cbcPriceAmount)

    xml_str = cacInvoiceLine.toprettyxml(indent="  ")
    return xml_str


def discrepancyResponse(id, code, description):
    cacDiscrepancyResponse = doc.createElement('cac:DiscrepancyResponse')
    cbcReferenceID = doc.createElement('cbc:ReferenceID')
    text = doc.createTextNode(id)
    cbcReferenceID.appendChild(text)
    cacDiscrepancyResponse.appendChild(cbcReferenceID)
    cbcResponseCode = doc.createElement('cbc:ResponseCode')
    text = doc.createTextNode(code)
    cbcResponseCode.appendChild(text)
    cacDiscrepancyResponse.appendChild(cbcResponseCode)
    cbcDescription = doc.createElement('cbc:Description')
    text = doc.createTextNode(description)
    cbcDescription.appendChild(text)
    cacDiscrepancyResponse.appendChild(cbcDescription)
    xml_str = cacDiscrepancyResponse.toprettyxml(indent="  ")
    return xml_str


def billingReference(id, type):
    cacBillingReference = doc.createElement('cac:BillingReference')
    cacInvoiceDocumentReference = doc.createElement('cac:InvoiceDocumentReference')
    cacBillingReference.appendChild(cacInvoiceDocumentReference)
    cbcID = doc.createElement('cbc:ID')
    text = doc.createTextNode(id)
    cbcID.appendChild(text)
    cacInvoiceDocumentReference.appendChild(cbcID)
    cbcDocumentTypeCode = doc.createElement('cbc:DocumentTypeCode')
    text = doc.createTextNode(type)
    cbcDocumentTypeCode.appendChild(text)
    cacInvoiceDocumentReference.appendChild(cbcDocumentTypeCode)
    xml_str = cacBillingReference.toprettyxml(indent="  ")
    return xml_str


ruc = ""
razon = ""


class einvoice_nota_credito(models.Model):


    @api.multi
    def do_nota_credito_tasks(self):
        if int(self.referencia.journal_id.code) == 1:
            seq = self.env['ir.sequence'].next_by_code('nota.credito.secue.f')
        else:
            seq = self.env['ir.sequence'].next_by_code('nota.credito.secue.b')

        account_move = self.env['account.move'].search([['id', '=', self.referencia.move_id.id]])
        order_id = 'id'
        line_move = self.env['account.move.line'].search([['move_id', '=', account_move.id]], order=order_id)
        lml = []

        for move_lines in line_move:
            amount_cu = 0
            if move_lines.currency_id:
                if move_lines['credit'] > 0 and move_lines['debit'] == 0:
                    amount_cu = abs(move_lines.amount_currency)
                elif move_lines['debit'] > 0 and move_lines['credit'] == 0:
                    amount_cu = -(move_lines.amount_currency)

            lml.append((0, 0, {
                'date_maturity': move_lines.date_maturity,
                'partner_id': self.referencia.partner_id.id,
                'name': move_lines.name,
                'date': move_lines.date,
                'debit': move_lines['credit'],
                'credit': move_lines['debit'],
                'account_id': move_lines.account_id.id,
                'analytic_lines': move_lines.analytic_lines.id,
                'amount_currency': amount_cu,
                'currency_id': move_lines.currency_id.id,
                'tax_code_id': move_lines.tax_code_id.id,
                'tax_amount': move_lines.tax_amount,
                'ref': move_lines.ref,
                'quantity': move_lines.quantity,
                'product_id': move_lines.product_id.id,
                'product_uom_id': move_lines.product_uom_id.id,
                'analytic_account_id': move_lines.analytic_account_id.id,
                'type': move_lines.type
            }))
        line = self.referencia.finalize_invoice_move_lines([l for l in lml])
        move_vals = {
            'ref': str(self.referencia.internal_number),
            'name': self.referencia.internal_number,
            'line_id': line,
            'journal_id': self.referencia.journal_id.id,
            'date': self.referencia.date_invoice,
            'narration': self.referencia.comment,
            'period_id': self.referencia.period_id.id,
            'company_id': self.referencia.company_id.id,
            'state': 'posted',
        }

        move = self.env['account.move'].create(move_vals)
        self.referencia.write({'state': 'anulado'})
        self.referencia._log_event()
        # raise Warning('ddddddddddddd')
        self.write({'numeracion': seq, 'state': 'enviar_sunat', 'move_id': move.id})

    @api.multi
    def action_enviar_sunat(self):
        global ruc, razon
        ruc = self.env['res.company'].browse(1)
        razon = self.env['res.company'].browse(1)

        typo = ''
        serie = ''
        idadicional = ''
        if str(self.referencia.partner_id.doc_type) == 'dni':
            typo = '07'
            idadicional = '1'
        elif str(self.referencia.partner_id.doc_type) == 'ruc':
            typo = '07'
            idadicional = '6'

        b = pago(1, str(self.subtotal), str(self.numero_to_letras(self.subtotal)), str(self.currency_id.name))
        c = firma('', "", '')
        d = UBLVersion()
        n = customizationID()
        o = id(str(self.numeracion))
        e = issueDate(str(self.fecha_emision))
        # g = invoiceTypeCode()
        h = documentCurrencyCode(str(self.currency_id.name))
        i = declaracionFirma('SignSUNAT', ruc.x_ruc, razon.name, '#SignSUNAT')

        j = DatosProveedor(razon.x_ruc,
                           '6',
                           razon.name,
                           str(razon.partner_id.zip),
                           str(razon.partner_id.street),
                           str(razon.partner_id.state_id.name),
                           str(razon.partner_id.state_id.name),
                           str(razon.partner_id.state_id.name),
                           razon.name,
                           str(razon.partner_id.country_id.code))
        if self.referencia.partner_id.parent_id:
            k = DatosCliente(str(self.referencia.partner_id.parent_id.doc_number), idadicional,
                             str(self.referencia.partner_id.parent_id.name))
        else:
            k = DatosCliente(str(self.referencia.partner_id.doc_number), idadicional,
                             str(self.referencia.partner_id.name))
        l = sumatoriaIGV(str(self.impuesto), str(self.currency_id.name))
        q = importeTotal(str(self.importe_total), str(self.currency_id.name))
        m = Producto('1', '1', str(self.subtotal), str(self.impuesto), '001', 'Servicio', str(self.subtotal),
                     str(self.currency_id.name))
        # print (str(self.descripcion.rstrip('\n')))
        r = discrepancyResponse(str(self.referencia.number), str(self.tipo.code), str(self.descripcion.strip()))
        s = billingReference(str(self.referencia.number), str(int(self.referencia.journal_id.code)).zfill(2))

        # f = open(r'D:\notacredito.XML', 'w')
        nombre = self.generate_document_name(ruc.x_ruc)

        f = open(nombre, 'w')
        xm = doc.toprettyxml()

        xm = xm.replace('<?xml version="1.0" ?>',
                        '<?xml version="1.0" encoding="ISO-8859-1" standalone="no"?><CreditNote xmlns="urn:oasis:names:specification:ubl:schema:xsd:CreditNote-2" xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2" xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2" xmlns:ccts="urn:un:unece:uncefact:documentation:2" xmlns:ds="http://www.w3.org/2000/09/xmldsig#" xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2" xmlns:qdt="urn:oasis:names:specification:ubl:schema:xsd:QualifiedDatatypes-2" xmlns:sac="urn:sunat:names:specification:ubl:peru:schema:xsd:SunatAggregateComponents-1" xmlns:udt="urn:un:unece:uncefact:data:specification:UnqualifiedDataTypesSchemaModule:2" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">')
        f.write(xm)
        f.write('<ext:UBLExtensions>\n')
        f.write(b)
        f.write(c)
        f.write('</ext:UBLExtensions>\n')
        f.write(d)
        f.write(n)
        f.write(o)
        f.write(e)
        # f.write(g)
        f.write(h)
        f.write(r)
        f.write(s)
        f.write(i)
        f.write(j)
        f.write(k)
        f.write(l)
        f.write(q)
        f.write(m)
        f.write('</CreditNote>')
        f.close()

        rfirmado = credito()
        valor_resumen = rfirmado.sign_xml(fichero_xml=nombre)
        self.write({'digest_value': str(valor_resumen)})

        envio = EnvioSunat()
        nombre2 = nombre.replace(".xml", "")
        p5 = nombre2.find('envio')
        pathrecortado = str(nombre2[p5 + 6::])
        cdr = envio.Envio(zip=pathrecortado + '.zip')

        bar = BarCo()
        imagen = bar.generate_image(str(valor_resumen.encode(encoding="ISO-8859-1").strip()))
        # print (imagen)
        self.write({'image_bar': imagen})

        avc = self.env['warning_box'].info(title='Enviado a SUNAT',
                                           message="Usted acaba de enviar la Nota de Credito a SUNAT")

        path2 = os.path.abspath(
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models/archivos/recepcionado'))

        path2 = path2.replace('\\', '/')
        path2 = r"" + path2
        ruta_zip = path2 + '/R-' + ruc.x_ruc + '-07-' + self.numeracion + '.zip'
        print(ruta_zip)
        dir_rep = ruta_zip
        try:
            zipe = zipfile.ZipFile(dir_rep)
        except zipfile.BadZipfile, err:
            message = ("Porfavor verifique en la página de SUNAT")
            raise Exception(message)
        cortando2 = dir_rep.replace('.zip', '.xml')
        cortando3 = cortando2.replace(path2, '')
        cortando3 = cortando3.replace('/', '')
        file = zipe.read(cortando3)
        g = file.find('<cbc:ResponseCode>')
        f = file.find('</cbc:ResponseCode>')
        cadena = file[g + 18:f]
        print(cadena)
        zipe.close()
        if int(cadena) > -1:
            ge = file.find('<cbc:Description>')
            fe = file.find('</cbc:Description>')
            cadena2 = file[ge + 17:fe]
            print(cadena2)
            self.write({'mensaje_cdr': str(cadena2)})

        template = self.env.ref('comprobantes_sunat.correo_nota_de_credito', False)  # obtener el id del template a copiar
        id_copia = template.copy()  # copiamos el template esto genera el mismo nombre y le agrega al final (copia)
        id_copia.write({'name': str(self.numeracion)+'-credito'})  # ACTUALIZAMOS AL NOMBRE QUE QUERAMOS PARA PODER BUSCARLO A LA HORA DE ENVIAR EL EMAIL
        # print (id_copia)
        # raise Warning(template)
        attachment_obj = self.env['ir.attachment']
        nombre = nombre.replace('.xml', '.zip')
        f_e2 = open(nombre, 'rb')
        data_file2 = f_e2.read()
        filename2 = ruc.x_ruc + '-07-' + self.numeracion + '.zip'
        vals2 = \
            {'name': filename2
                , 'datas': base64.b64encode(str(data_file2))
                , 'datas_fname': filename2
                , 'res_model': 'einvoice.nota.credito'
                , 'type': 'binary'
                , 'res_id': 0
                , 'description': False
             }
        res2 = attachment_obj.create(vals2)
        self._cr.execute(
            """ INSERT INTO email_template_attachment_rel(email_template_id, attachment_id) VALUES(%s, %s)""",
            (id_copia.id, res2.id))
        f_e2.close()

        f_e = open(dir_rep, 'rb')
        data_file = f_e.read()
        filename = 'R-' + ruc.x_ruc + '-07-' + self.numeracion + '.zip'
        vals = \
            {'name': filename
                , 'datas': base64.b64encode(str(data_file))
                , 'datas_fname': filename
                , 'res_model': 'einvoice.nota.credito'
                , 'type': 'binary'
                , 'res_id': 0
                , 'description': False
             }
        res = attachment_obj.create(vals)
        self._cr.execute(
            """ INSERT INTO email_template_attachment_rel(email_template_id, attachment_id) VALUES(%s, %s)""",
            (id_copia.id, res.id))
        f_e.close()

        return avc, self.write({'state': 'enviado'})

    def generate_document_name(self, tdoc):
        path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models/archivos/envio'))
        path = path.replace('\\', '/')
        base_dir = r"" + path

        filename = tdoc + '-07-' + str(self.numeracion) + '.xml'

        # TODO: Add types as constants in diferent classes
        return os.path.join(base_dir, filename)

    def get_emp_det(self, cr, uid, ids, referencia, context=None):
        v = {}
        if referencia:
            fac = self.pool.get('account.invoice').browse(cr, uid, referencia, context=context)
            if fac.amount_untaxed:
                v['subtotal'] = fac.amount_untaxed
            if fac.amount_tax:
                v['impuesto'] = fac.amount_tax
            if fac.amount_total:
                v['importe_total'] = fac.amount_total
            if fac:
                if fac.partner_id.parent_id:
                    v['ruc'] = fac.partner_id.parent_id.doc_number
                    v['cliente'] = fac.partner_id.display_name
                else:
                    v['ruc'] = fac.partner_id.doc_number
                    v['cliente'] = fac.partner_id.name
            if fac.currency_id.name:
                v['currency_id'] = fac.currency_id.id

        return {'value': v}

    def numero_to_letras(self, numero):
        indicador = [("", ""), ("MIL", "MIL"), ("MILLON", "MILLONES"), ("MIL", "MIL"), ("BILLON", "BILLONES")]
        entero = int(numero)
        decimal = int(round((numero - entero) * 100))
        # print 'decimal : ',decimal
        contador = 0
        numero_letras = ""
        while entero > 0:
            a = entero % 1000
            if contador == 0:
                en_letras = self.convierte_cifra(a, 1).strip()
            else:
                en_letras = self.convierte_cifra(a, 0).strip()
            if a == 0:
                numero_letras = en_letras + " " + numero_letras
            elif a == 1:
                if contador in (1, 3):
                    numero_letras = indicador[contador][0] + " " + numero_letras
                else:
                    numero_letras = en_letras + " " + indicador[contador][0] + " " + numero_letras
            else:
                numero_letras = en_letras + " " + indicador[contador][1] + " " + numero_letras
            numero_letras = numero_letras.strip()
            contador = contador + 1
            entero = int(entero / 1000)
        numero_letras = numero_letras + " con " + str(decimal) + "/100"
        # print 'numero: ', numero
        return numero_letras

    def convierte_cifra(self, numero, sw):
        lista_centana = ["", ("CIEN", "CIENTO"), "DOSCIENTOS", "TRESCIENTOS", "CUATROCIENTOS", "QUINIENTOS",
                         "SEISCIENTOS",
                         "SETECIENTOS", "OCHOCIENTOS", "NOVECIENTOS"]
        lista_decena = ["", (
            "DIEZ", "ONCE", "DOCE", "TRECE", "CATORCE", "QUINCE", "DIECISEIS", "DIECISIETE", "DIECIOCHO", "DIECINUEVE"),
                        ("VEINTE", "VEINTI"), ("TREINTA", "TREINTA Y "), ("CUARENTA", "CUARENTA Y "),
                        ("CINCUENTA", "CINCUENTA Y "), ("SESENTA", "SESENTA Y "),
                        ("SETENTA", "SETENTA Y "), ("OCHENTA", "OCHENTA Y "),
                        ("NOVENTA", "NOVENTA Y ")
                        ]
        lista_unidad = ["", ("UN", "UNO"), "DOS", "TRES", "CUATRO", "CINCO", "SEIS", "SIETE", "OCHO", "NUEVE"]
        centena = int(numero / 100)
        decena = int((numero - (centena * 100)) / 10)
        unidad = int(numero - (centena * 100 + decena * 10))
        # print "centena: ",centena, "decena: ",decena,'unidad: ',unidad

        texto_centena = ""
        texto_decena = ""
        texto_unidad = ""

        # Validad las centenas
        texto_centena = lista_centana[centena]
        if centena == 1:
            if (decena + unidad) != 0:
                texto_centena = texto_centena[1]
            else:
                texto_centena = texto_centena[0]

        # Valida las decenas
        texto_decena = lista_decena[decena]
        if decena == 1:
            texto_decena = texto_decena[unidad]
        elif decena > 1:
            if unidad != 0:
                texto_decena = texto_decena[1]
            else:
                texto_decena = texto_decena[0]
        # Validar las unidades
        # print "texto_unidad: ",texto_unidad
        if decena != 1:
            texto_unidad = lista_unidad[unidad]
            if unidad == 1:
                texto_unidad = texto_unidad[sw]

        return "%s %s %s" % (texto_centena, texto_decena, texto_unidad)

    @api.multi
    def invoice_print(self):
        """ Print the invoice and mark it as sent, so that we can see more
            easily the next step of the workflow
        """
        assert len(self) == 1, 'This option should only be used for a single id at a time.'
        # self.sent = True
        return self.env['report'].get_action(self, 'comprobantes_sunat.report_nota_credito_document')

    @api.multi
    def action_credito_sent(self):
        assert len(self) == 1, 'This option should only be used for a single id at a time.'
        # template = self.env.ref('account.email_template_edi_invoice')
        # template1 = self.env.ref('comprobantes_sunat.correo_nota_de_credito', False)
        template = self.env['email.template'].search([['name', '=', str(self.numeracion)+'-credito']], limit=1)
        # print (template)
        if not template:
            raise Warning('Aviso!', 'La plantilla no existe!')
        # else:
        #     template1 = self.env.ref('comprobantes_sunat.correo_nota_de_credito',
        #                             False)  # obtener el id del template a copiar
        #     id_copia = template1.copy()  # copiamos el template esto genera el mismo nombre y le agrega al final (copia)
        #     id_copia.write({'name': str(self.numeracion) + '-credito'})  # ACTUALIZAMOS AL NOMBRE QUE QUERAMOS PARA PODER BUSCARLO A LA HORA DE ENVIAR EL EMAIL
        #     template = self.env['email.template'].search([['name', '=', str(self.numeracion) + '-credito']], limit=1)

        compose_form = self.env.ref('mail.email_compose_message_wizard_form')
        # print (template)
        # par = self.env['account.bank.statement.line'].search([['id', '=', self.id]], limit=1)
        # par = self.env['account.invoice'].search([['id', '=', self.referencia.id]], limit=1)
        # print(par.partner_id.id)

        ctx = dict(
            default_model='einvoice.nota.credito',
            default_res_id=self.id,
            default_use_template=bool(template),
            default_new_template_id=template.id,
            default_composition_mode='comment',
            mark_invoice_as_sent=False,

        )
        print(ctx)
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }

    def _get_serie(self, serie):
        n = serie.split('-')
        return n[0]

    def _get_numeracion(self, numeracion):
        n = numeracion.split('-')
        return n[1]

    _name = 'einvoice.nota.credito'
    _inherit = ['mail.thread']
    _rec_name = 'numeracion'
    _description = 'Nota de Credito'
    _order = "fecha_emision desc"

    numeracion = fields.Char(string='Nota de Credito', copy=False)
    cliente = fields.Char("Cliente", required=True, )
    tipo = fields.Many2one('einvoice.catalog.09', 'Tipo', required=True, )
    referencia = fields.Many2one('account.invoice', string='Referencia', required=True, ondelete='cascade')
    fecha_emision = fields.Date(string="Fecha Emision", required=True,
                                default=lambda *a: datetime.now().strftime('%Y-%m-%d'))
    ruc = fields.Char(string="RUC/DNI", required=True, )
    descripcion = fields.Text(string="Motivo o Sustento", size=250, help="Maximo 250 Caracteres", default='', required=True)
    subtotal = fields.Float(string="SubTotal", required=True)
    impuesto = fields.Float(string="impuesto")
    importe_total = fields.Float(string="Importe Total", required=True)
    currency_id = fields.Many2one('res.currency', "Tipo de Moneda", required=True)
    digest_value = fields.Char(string='Resumen', copy=False)
    image_bar = fields.Binary(string="", copy=False)

    move_id = fields.Many2one('account.move', string='Asiento Contable', readonly=1, index=True, ondelete='restrict',
                              copy=False, store=True,
                              help="Link to the automatically generated Journal Items.")

    # ticket = fields.Char(string='Ticket')
    mensaje_cdr = fields.Char(string='Resultado CDR', readonly=True, store=True, copy=False)

    state = fields.Selection([
        ('borrador', 'Borrador'),
        ('enviar_sunat', 'Enviar a Sunat'),
        ('enviado', 'Enviado'),
        ('error', 'Cancelada'),
    ], string='Estado', index=True, readonly=True, default='borrador',
        track_visibility='onchange', copy=False)

    count_letras = fields.Integer(string='Caracteres', default=250, compute="_count_letras")

    descripcion_servicio = fields.Text(string='Descripcion', required=True)

    @api.multi
    def error_plush(self):
        self.write({'state': 'error'})

    @api.one
    @api.depends('descripcion')
    def _count_letras(self):
        abc = [' ', '!', '"', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',', '-', '.', '/', '0', '1', '2', '3', '4',
               '5', '6', '7', '8', '9', ':', ';', '<', '=', '>', '?', '@', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I',
               'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '[', '\\', ']', '^',
               '_', '`', 'a', 'á', 'b', 'c', 'd', 'e', 'é', 'f', 'g', 'h', 'i', 'í', 'j', 'k', 'l', 'm', 'n', 'o', 'ó',
               'p', 'q', 'r', 's', 't', 'u', 'ú', 'v', 'w', 'x', 'y', 'z', '{', '|', '}', '~']
        self.count_letras = 250
        for c in str(self.descripcion):
            for l in abc:
                if l == c:
                    self.count_letras -= 1
        if self.count_letras < 0:
            raise Warning('Solo pueden haber 250 caracteres, se paso ' + str(abs(self.count_letras)) + ' caracteres')


class einvoice_nota_debito(models.Model):
    _order = "fecha_emision desc"

    @api.multi
    def do_nota_debito_tasks(self):
        if int(self.referencia.journal_id.code) == 1:
            seq = self.env['ir.sequence'].next_by_code('nota.debito.secue.f')
        else:
            seq = self.env['ir.sequence'].next_by_code('nota.debito.secue.b')
        self.write({'numeracion': seq, 'state': 'enviar_sunat'})

    @api.multi
    def action_enviar_sunat(self):
        global ruc, razon
        ruc = self.env['res.company'].browse(1)
        razon = self.env['res.company'].browse(1)

        typo = ''
        serie = ''
        idadicional = ''
        # if self.referencia.partner_id.parent_id:
        if str(self.referencia.partner_id.parent_id.doc_type) == 'dni':
            typo = '08'
            idadicional = '1'
        else:
            typo = '08'
            idadicional = '6'

        b = pago(1, str(self.subtotal), str(self.numero_to_letras(self.subtotal)), str(self.currency_id.name))
        c = firma('', '', '')
        d = UBLVersion()
        n = customizationID()
        o = id(str(self.numeracion))
        e = issueDate(str(self.fecha_emision))
        # g = invoiceTypeCode()
        h = documentCurrencyCode(str(self.currency_id.name))
        i = declaracionFirma('SignSUNAT', ruc.x_ruc, razon.name, '#SignSUNAT')
        j = DatosProveedor(razon.x_ruc,
                           '6',
                           razon.name,
                           str(razon.partner_id.zip),
                           str(razon.partner_id.street),
                           str(razon.partner_id.state_id.name),
                           str(razon.partner_id.state_id.name),
                           str(razon.partner_id.state_id.name),
                           razon.name,
                           str(razon.partner_id.country_id.code))
        if self.referencia.partner_id.parent_id:
            k = DatosCliente(str(self.referencia.partner_id.parent_id.doc_number), idadicional,
                             str(self.referencia.partner_id.parent_id.name))
        else:
            k = DatosCliente(str(self.referencia.partner_id.doc_number), idadicional,
                             str(self.referencia.partner_id.name))

        l = sumatoriaIGV(str(self.impuesto), str(self.currency_id.name))
        q = importeTotaldebito(str(self.importe_total), str(self.currency_id.name))
        m = Productodebito('1', '1', '0.00', '0.00', '001', 'Prod-258963', str(self.subtotal),
                           str(self.currency_id.name))
        r = discrepancyResponse(str(self.referencia.number), str(self.tipo.code), str(self.descripcion))
        s = billingReference(str(self.referencia.number), str(self.referencia.journal_id.code).zfill(2))

        nombre = self.generate_document_name(ruc.x_ruc)
        f = open(nombre, 'w')
        xm = doc.toprettyxml()
        xm = xm.replace('<?xml version="1.0" ?>',
                        '<?xml version="1.0" encoding="ISO-8859-1" standalone="no"?><DebitNote xmlns="urn:oasis:names:specification:ubl:schema:xsd:DebitNote-2" xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2" xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2" xmlns:ccts="urn:un:unece:uncefact:documentation:2" xmlns:ds="http://www.w3.org/2000/09/xmldsig#" xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2" xmlns:qdt="urn:oasis:names:specification:ubl:schema:xsd:QualifiedDatatypes-2" xmlns:sac="urn:sunat:names:specification:ubl:peru:schema:xsd:SunatAggregateComponents-1" xmlns:udt="urn:un:unece:uncefact:data:specification:UnqualifiedDataTypesSchemaModule:2" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">')
        f.write(xm)
        f.write('<ext:UBLExtensions>\n')
        f.write(b)
        f.write(c)
        f.write('</ext:UBLExtensions>\n')
        f.write(d)
        f.write(n)
        f.write(o)
        f.write(e)
        # f.write(g)
        f.write(h)
        f.write(r)
        f.write(s)
        f.write(i)
        f.write(j)
        f.write(k)
        f.write(l)
        f.write(q)
        f.write(m)
        f.write('</DebitNote>')
        f.close()

        rfirmado = debito()
        valor_resumen = rfirmado.sign_xml(fichero_xml=nombre)
        self.write({'digest_value': str(valor_resumen)})

        envio = EnvioSunat()
        nombre2 = nombre.replace(".xml", "")
        print(nombre2)
        p5 = nombre2.find('envio')
        pathrecortado = str(nombre2[p5 + 6::])
        print('>>>>>>' + pathrecortado)
        envio.Envio(zip=pathrecortado + '.zip')
        bar = BarCo()
        imagen = bar.generate_image(str(valor_resumen.encode(encoding="ISO-8859-1").strip()))
        # print (imagen)

        self.write({'image_bar': imagen})
        avc = self.env['warning_box'].info(title='Enviado a SUNAT',
                                           message="Usted acaba de enviar la Nota de Debito a SUNAT")

        path2 = os.path.abspath(
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models/archivos/recepcionado'))
        path2 = path2.replace('\\', '/')
        path2 = r"" + path2
        ruta_zip = path2 + '/R-' + ruc.x_ruc + '-08-' + self.numeracion + '.zip'
        print(ruta_zip)
        dir_rep = ruta_zip
        try:
            zipe = zipfile.ZipFile(dir_rep)
        except zipfile.BadZipfile, err:
            message = ("Porfavor verifique en la página de SUNAT")
            raise Exception(message)
        cortando2 = dir_rep.replace('.zip', '.xml')
        cortando3 = cortando2.replace(path2, '')
        cortando3 = cortando3.replace('/', '')
        file = zipe.read(cortando3)
        g = file.find('<cbc:ResponseCode>')
        f = file.find('</cbc:ResponseCode>')
        cadena = file[g + 18:f]
        print(cadena)
        zipe.close()
        if int(cadena) > -1:
            ge = file.find('<cbc:Description>')
            fe = file.find('</cbc:Description>')
            cadena2 = file[ge + 17:fe]
            print(cadena2)
            self.write({'mensaje_cdr': str(cadena2)})
        self.write({'estado': 'enviado'})

        template = self.env.ref('comprobantes_sunat.correo_nota_de_debito', False)
        id_copy_template = template.copy()
        id_copy_template.write({'name': str(self.numeracion)+'-debito'})
        attachment_obj = self.env['ir.attachment']
        # raise Warning(nombre)
        nombre = nombre.replace('.xml', '.zip')

        f_e2 = open(nombre, 'rb')
        data_file2 = f_e2.read()
        filename2 = ruc.x_ruc + '-08-' + self.numeracion + '.zip'
        vals2 = \
            {'name': filename2
                , 'datas': base64.b64encode(str(data_file2))
                , 'datas_fname': filename2
                , 'res_model': 'einvoice.nota.credito'
                , 'type': 'binary'
                , 'res_id': 0
                , 'description': False
             }
        res2 = attachment_obj.create(vals2)
        self._cr.execute(
            """ INSERT INTO email_template_attachment_rel(email_template_id, attachment_id) VALUES(%s, %s)""",
            (id_copy_template.id, res2.id))
        f_e2.close()

        f_e = open(dir_rep, 'rb')
        data_file = f_e.read()
        filename = 'R-' + ruc.x_ruc + '-08-' + self.numeracion + '.zip'
        vals = \
            {'name': filename
                , 'datas': base64.b64encode(str(data_file))
                , 'datas_fname': filename
                , 'res_model': 'einvoice.nota.debito'
                , 'type': 'binary'
                , 'res_id': 0
                , 'description': False
             }
        res = attachment_obj.create(vals)
        self._cr.execute(
            """ INSERT INTO email_template_attachment_rel(email_template_id, attachment_id) VALUES(%s, %s)""",
            (id_copy_template.id, res.id))
        f_e.close()

        return avc

    def generate_document_name(self, tdoc):
        path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models/archivos/envio'))
        path = path.replace('\\', '/')
        base_dir = r"" + path

        filename = tdoc + '-08-' + str(self.numeracion) + '.xml'

        # TODO: Add types as constants in diferent classes
        return os.path.join(base_dir, filename)

    def get_emp_det(self, cr, uid, ids, referencia, context=None):
        v = {}
        if referencia:
            fac = self.pool.get('account.invoice').browse(cr, uid, referencia, context=context)
            if fac.amount_untaxed:
                v['subtotal'] = fac.amount_untaxed
            if fac.amount_tax:
                v['impuesto'] = fac.amount_tax
            if fac.amount_total:
                v['importe_total'] = fac.amount_total
            if fac:
                if fac.partner_id.parent_id:
                    v['ruc'] = fac.partner_id.parent_id.doc_number
                    v['cliente'] = fac.partner_id.display_name
                else:
                    v['ruc'] = fac.partner_id.doc_number
                    v['cliente'] = fac.partner_id.name
            if fac.currency_id:
                v['currency_id'] = fac.currency_id.id

        return {'value': v}

    def numero_to_letras(self, numero):
        indicador = [("", ""), ("MIL", "MIL"), ("MILLON", "MILLONES"), ("MIL", "MIL"), ("BILLON", "BILLONES")]
        entero = int(numero)
        decimal = int(round((numero - entero) * 100))
        # print 'decimal : ',decimal
        contador = 0
        numero_letras = ""
        while entero > 0:
            a = entero % 1000
            if contador == 0:
                en_letras = self.convierte_cifra(a, 1).strip()
            else:
                en_letras = self.convierte_cifra(a, 0).strip()
            if a == 0:
                numero_letras = en_letras + " " + numero_letras
            elif a == 1:
                if contador in (1, 3):
                    numero_letras = indicador[contador][0] + " " + numero_letras
                else:
                    numero_letras = en_letras + " " + indicador[contador][0] + " " + numero_letras
            else:
                numero_letras = en_letras + " " + indicador[contador][1] + " " + numero_letras
            numero_letras = numero_letras.strip()
            contador = contador + 1
            entero = int(entero / 1000)
        numero_letras = numero_letras + " con " + str(decimal) + "/100"
        # print 'numero: ', numero
        return numero_letras

    def convierte_cifra(self, numero, sw):
        lista_centana = ["", ("CIEN", "CIENTO"), "DOSCIENTOS", "TRESCIENTOS", "CUATROCIENTOS", "QUINIENTOS",
                         "SEISCIENTOS",
                         "SETECIENTOS", "OCHOCIENTOS", "NOVECIENTOS"]
        lista_decena = ["", (
            "DIEZ", "ONCE", "DOCE", "TRECE", "CATORCE", "QUINCE", "DIECISEIS", "DIECISIETE", "DIECIOCHO", "DIECINUEVE"),
                        ("VEINTE", "VEINTI"), ("TREINTA", "TREINTA Y "), ("CUARENTA", "CUARENTA Y "),
                        ("CINCUENTA", "CINCUENTA Y "), ("SESENTA", "SESENTA Y "),
                        ("SETENTA", "SETENTA Y "), ("OCHENTA", "OCHENTA Y "),
                        ("NOVENTA", "NOVENTA Y ")
                        ]
        lista_unidad = ["", ("UN", "UNO"), "DOS", "TRES", "CUATRO", "CINCO", "SEIS", "SIETE", "OCHO", "NUEVE"]
        centena = int(numero / 100)
        decena = int((numero - (centena * 100)) / 10)
        unidad = int(numero - (centena * 100 + decena * 10))
        # print "centena: ",centena, "decena: ",decena,'unidad: ',unidad

        texto_centena = ""
        texto_decena = ""
        texto_unidad = ""

        # Validad las centenas
        texto_centena = lista_centana[centena]
        if centena == 1:
            if (decena + unidad) != 0:
                texto_centena = texto_centena[1]
            else:
                texto_centena = texto_centena[0]

        # Valida las decenas
        texto_decena = lista_decena[decena]
        if decena == 1:
            texto_decena = texto_decena[unidad]
        elif decena > 1:
            if unidad != 0:
                texto_decena = texto_decena[1]
            else:
                texto_decena = texto_decena[0]
        # Validar las unidades
        # print "texto_unidad: ",texto_unidad
        if decena != 1:
            texto_unidad = lista_unidad[unidad]
            if unidad == 1:
                texto_unidad = texto_unidad[sw]

        return "%s %s %s" % (texto_centena, texto_decena, texto_unidad)

    @api.multi
    def invoice_print(self):
        """ Print the invoice and mark it as sent, so that we can see more
            easily the next step of the workflow
        """
        assert len(self) == 1, 'This option should only be used for a single id at a time.'
        return self.env['report'].get_action(self, 'comprobantes_sunat.report_nota_debito_document')

    @api.multi
    def action_debito_sent(self):
        assert len(self) == 1, 'This option should only be used for a single id at a time.'
        # template = self.env.ref('account.email_template_edi_invoice')
        template0 = self.env.ref('comprobantes_sunat.correo_nota_de_debito', False)
        template = self.env['email.template'].search([['name','=', str(self.numeracion)+'-debito']])
        compose_form = self.env.ref('mail.email_compose_message_wizard_form')

        # par = self.env['account.bank.statement.line'].search([['id', '=', self.id]], limit=1)
        # par = self.env['account.invoice'].search([['id', '=', self.referencia.id]], limit=1)
        # print(par.partner_id.id)

        ctx = dict(
            default_model='einvoice.nota.debito',
            default_res_id=self.id,
            default_use_template=bool(template),
            default_new_template_id=template.id,
            default_composition_mode='comment',
            mark_invoice_as_sent=False,

        )
        print(ctx)
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }

    _name = 'einvoice.nota.debito'
    _rec_name = 'numeracion'
    _description = 'Nota de debito'

    numeracion = fields.Char(string="Nota de debito")
    cliente = fields.Char("Cliente", required=True)
    tipo = fields.Many2one('einvoice.catalog.10', 'Tipo', required=True)
    referencia = fields.Many2one('account.invoice', string='Referencia',
                                 domain="['&',('state','in',['open', 'paid']),('type','=','in_invoice')]",
                                 ondelete='cascade', required=True)
    fecha_emision = fields.Date(string="Fecha Emision", required=True)
    ruc = fields.Char(string="RUC/DNI", required=True)
    descripcion = fields.Text(string="Motivo o Sustento")
    subtotal = fields.Float(string="SubTotal", required=True)
    impuesto = fields.Float(string="impuesto")
    importe_total = fields.Float(string="Importe Total", required=True)
    currency_id = fields.Many2one('res.currency', "Tipo de Moneda", required=True)
    digest_value = fields.Char(string='Resumen')
    image_bar = fields.Binary()

    mensaje_cdr = fields.Char(string='Resultado CDR', readonly=True, store=True)

    state = fields.Selection([
        ('borrador', 'Borrador'),
        ('enviar_sunat', 'Enviar a Sunat'),
        ('enviado', 'Enviado'),
    ], string='Estado', index=True, readonly=True, default='borrador',
        track_visibility='onchange', copy=False)
    count_letras = fields.Integer(string='Caracteres', default=250, compute="_count_letras")

    @api.one
    @api.depends('descripcion')
    def _count_letras(self):
        abc = [' ', '!', '"', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',', '-', '.', '/', '0', '1', '2', '3', '4',
               '5', '6', '7', '8', '9', ':', ';', '<', '=', '>', '?', '@', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I',
               'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '[', '\\', ']', '^',
               '_', '`', 'a', 'á', 'b', 'c', 'd', 'e', 'é', 'f', 'g', 'h', 'i', 'í', 'j', 'k', 'l', 'm', 'n', 'o', 'ó',
               'p', 'q', 'r', 's', 't', 'u', 'ú', 'v', 'w', 'x', 'y', 'z', '{', '|', '}', '~']
        self.count_letras = 250
        for c in str(self.descripcion):
            for l in abc:
                if l == c:
                    self.count_letras -= 1
        if self.count_letras < 0:
            raise Warning('Solo pueden haber 250 caracteres, se paso ' + str(abs(self.count_letras)) + ' caracteres')


class einvoice_comunicacion_baja(models.Model):
    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('einvoice.comunicacion.baja.secue')
        vals['identificador'] = seq
        if 'comunicacion_ids' in vals:
            for idx, line in enumerate(vals['comunicacion_ids']):
                line[2]['sequence'] = idx + 1
        return super(einvoice_comunicacion_baja, self).create(vals)

    @api.multi
    def do_comunicacion_baja_tasks(self):
        global ruc, razon
        count = 0
        ruc = self.env['res.company'].browse(1)
        razon = self.env['res.company'].browse(1)

        path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models/archivos/envio'))
        path = path.replace('\\', '/')
        base_dir = r"" + path
        path2 = os.path.abspath(
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models/archivos/recepcionado'))
        path2 = path2.replace('\\', '/')
        base_dir2 = r"" + path2
        abc_zip = base_dir + '/' + str(ruc.x_ruc) + '-' + str(self.identificador) + '.zip'
        abc_xml = base_dir + '/' + str(ruc.x_ruc) + '-' + str(self.identificador) + '.xml'
        abc_zip_cdr = base_dir2 + '/R-' + str(ruc.x_ruc) + '-' + str(self.identificador) + '.zip'
        print(abc_zip_cdr)
        if os.path.isfile(abc_zip):
            print('Eliminandoooo...', str(abc_zip))
            os.remove(abc_zip)
        if os.path.isfile(abc_xml):
            print('Eliminandoooo...', str(abc_xml))
            os.remove(abc_xml)
        if os.path.isfile(abc_zip_cdr):
            print('Eliminandoooo cdrrrrrrrr...', str(abc_zip_cdr))
            os.remove(abc_zip_cdr)
        #
        # raise Warning('ggggggggg')

        for baja in self.env['einvoice.comunicacion.baja'].browse(self.id):
            c = firma('', "", '')
            d = UBLVersion()
            n = customizationID()
            o = id(str(self.identificador))
            e1 = ReferenceDate(str(self.fecha_doc))
            e2 = issueDateComunicacion(str(self.fecha_baja))
            # g = invoiceTypeCode()
            # h = documentCurrencyCode()
            i = declaracionFirma('SignSUNAT', ruc.x_ruc, razon.name, '#SignSUNAT')

            j = DatosProveedor(razon.x_ruc,
                               '6',
                               razon.name,
                               str(razon.partner_id.zip),
                               str(razon.partner_id.street),
                               str(razon.partner_id.state_id.name),
                               str(razon.partner_id.state_id.name),
                               str(razon.partner_id.state_id.name),
                               razon.name,
                               str(razon.partner_id.zip))

            # f = open(r'D:\notacredito.XML', 'w')
            nombre = self.generate_document_name(ruc.x_ruc)

            f = open(nombre, 'w')
            xm = doc.toprettyxml()

            xm = xm.replace('<?xml version="1.0" ?>',
                            '<?xml version="1.0" encoding="ISO-8859-1" standalone="no"?><VoidedDocuments xmlns="urn:sunat:names:specification:ubl:peru:schema:xsd:VoidedDocuments-1" xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2" xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2" xmlns:ds="http://www.w3.org/2000/09/xmldsig#" xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2" xmlns:sac="urn:sunat:names:specification:ubl:peru:schema:xsd:SunatAggregateComponents-1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">')
            f.write(xm)
            f.write('<ext:UBLExtensions>\n')
            # f.write(b)
            f.write(c)
            f.write('</ext:UBLExtensions>\n')
            f.write(d)
            f.write(n)
            f.write(o)
            f.write(e1)
            f.write(e2)
            # f.write(h)
            f.write(i)
            f.write(j)

            for line in baja.comunicacion_ids:
                count += 1
                z = lineas_comunicacion(str(count),
                                        str(line.tipo_documento),
                                        str(line.serie),
                                        str(line.correlativo),
                                        elimina_tildes(str(line.motivo).decode('utf-8')))
                f.write(z)
                #
                # isss = self.env['account.invoice'].search([['number', '=', str(line.serie + '-' + line.correlativo)]])
                # print (isss)

            f.write('</VoidedDocuments>')
            f.close()
            # try:
        rfirmado = Comunicacionbaja()
        valor_resumen = rfirmado.sign_xml(fichero_xml=nombre)
        self.write({'digest_value': str(valor_resumen)})

        envio = envioBaja()
        nombre2 = nombre.replace(".xml", "")
        print(nombre2)
        p5 = nombre2.find('envio')
        pathrecortado = str(nombre2[p5 + 6::])
        print('>>>>>>' + pathrecortado)
        ticket = envio.Envio(zip=pathrecortado + '.zip')
        self.write({'ticket': str(ticket)})

        path2 = os.path.abspath(
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models/archivos/recepcionado'))
        path2 = path2.replace('\\', '/')
        path2 = r"" + path2
        ruta_zip = path2 + '/R-' + ruc.x_ruc + '-' + self.identificador + '.zip'
        print(ruta_zip)
        dir_rep = ruta_zip
        try:
            zipe = zipfile.ZipFile(dir_rep)
        except zipfile.BadZipfile, err:
            message = ("Porfavor verifique en la página de SUNAT")
            raise Exception(message)
        cortando2 = dir_rep.replace('.zip', '.xml')
        cortando3 = cortando2.replace(path2, '')
        cortando3 = cortando3.replace('/', '')
        file = zipe.read(cortando3)
        g = file.find('<cbc:ResponseCode>')
        f = file.find('</cbc:ResponseCode>')
        cadena = file[g + 18:f]
        print(cadena)
        zipe.close()
        if int(cadena) > -1:
            ge = file.find('<cbc:Description>')
            fe = file.find('</cbc:Description>')
            cadena2 = file[ge + 17:fe]
            print(cadena2)
            self.write({'mensaje_cdr': str(cadena2)})
            for line in self.comunicacion_ids:
                seq = (str(line.serie), str(line.correlativo))
                num_factura = '-'.join(seq)
                fac = self.env['account.invoice'].search([['internal_number', '=', str(num_factura)]], limit=1)
                fac.write({'state': 'cancel'})

        return {
            'type': 'ir.actions.client',
            'tag': 'action_warn',
            'name': _('Aviso'),
            'params': {
                'title': _('Aviso'),
                'text': _(u'Comunicacion Baja Enviada y Recepcionada!'),
                'sticky': False
            },
            'type': 'reload'
        }

    @api.multi
    def verificar_sunat_tasks(self):
        if self.ticket and self.ticket != None:
            ruc = self.env['res.company'].browse(1)
            getcdr = getStatusSunat()
            getcdr.getStatus(ticket=str(self.ticket), zip=str(ruc.x_ruc + '-' + self.identificador + '.zip'))

            path2 = os.path.abspath(
                os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models/archivos/recepcionado'))
            path2 = path2.replace('\\', '/')
            path2 = r"" + path2
            ruta_zip = path2 + '/R-' + ruc.x_ruc + '-' + self.identificador + '.zip'
            print(ruta_zip)
            dir_rep = ruta_zip
            try:
                zipe = zipfile.ZipFile(dir_rep)
            except zipfile.BadZipfile, err:
                message = ("Porfavor verifique en la página de SUNAT")
                raise Exception(message)
            cortando2 = dir_rep.replace('.zip', '.xml')
            cortando3 = cortando2.replace(path2, '')
            cortando3 = cortando3.replace('/', '')
            file = zipe.read(cortando3)
            g = file.find('<cbc:ResponseCode>')
            f = file.find('</cbc:ResponseCode>')
            cadena = file[g + 18:f]
            print(cadena)
            zipe.close()
            if int(cadena) > -1:
                ge = file.find('<cbc:Description>')
                fe = file.find('</cbc:Description>')
                cadena2 = file[ge + 17:fe]
                print(cadena2)
                self.write({'mensaje_cdr': str(cadena2)})
                for line in self.comunicacion_ids:
                    seq = (str(line.serie), str(line.correlativo))
                    num_factura = '-'.join(seq)
                    fac = self.env['account.invoice'].search([['internal_number', '=', str(num_factura)]], limit=1)
                    fac.write({'state': 'cancel'})

                return {'type': 'ir.actions.client', 'type': 'reload'}

    def generate_document_name(self, tdoc):

        path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models/archivos/envio'))
        path = path.replace('\\', '/')
        base_dir = r"" + path

        filename = tdoc + '-' + str(self.identificador) + '.xml'
        # TODO: Add types as constants in diferent classes
        return os.path.join(base_dir, filename)

    # default = lambda obj: obj.env['ir.sequence'].next_by_code('einvoice.comunicacion.baja.secue')

    _name = "einvoice.comunicacion.baja"
    _description = 'Comunicacion de baja'
    _rec_name = 'identificador'
    _order = "identificador desc, id desc"

    identificador = fields.Char(string='N°')
    fecha_baja = fields.Date(string="Fecha de la Comunicación de Baja",
                             default=lambda *a: datetime.now().strftime('%Y-%m-%d'), required=True)
    fecha_doc = fields.Date(string="Fecha del Documento a dar de Baja", required=True)
    comunicacion_ids = fields.One2many('einvoice.detalle.comunicacion.baja',
                                       'comunicacion_id',
                                       ondelete='cascade',
                                       copy=True)
    move_line_ids = fields.One2many('account.invoice', 'comunicacion_id', 'Entry lines'),
    digest_value = fields.Char(string='Resumen')
    ticket = fields.Char(string='Ticket')
    mensaje_cdr = fields.Char(string='Resultado CDR', readonly=True, store=True)


class einvoice_detalle_comunicacion_baja(models.Model):
    _name = "einvoice.detalle.comunicacion.baja"
    _description = 'Detalle de comunicacion de baja'

    sequence = fields.Integer(string='N#', default=1)
    tipo_documento = fields.Char('Tipo Documento', required=True)
    comprobante = fields.Char('Comprobante', required=True)
    serie = fields.Char(string='Serie', required=True)
    correlativo = fields.Char(string='Correlativo', required=True)
    motivo = fields.Text(string="Motivo o Sustento", required=True)
    motivo_opcion = fields.Many2one('einvoice.catalog.14', 'Tipo Motivo')
    fecha_doc = fields.Date(string="Fecha")
    comunicacion_id = fields.Many2one('einvoice.comunicacion.baja', string='Detalle Comunicacion', ondelete='cascade')
    count_letras = fields.Integer(string='Caracteres', default=100, compute="_count_letras")

    @api.one
    @api.depends('motivo')
    def _count_letras(self):
        abc = [' ', '!', '"', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',', '-', '.', '/', '0', '1', '2', '3', '4',
               '5', '6', '7', '8', '9', ':', ';', '<', '=', '>', '?', '@', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I',
               'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '[', '\\', ']', '^',
               '_', '`', 'a', 'á', 'b', 'c', 'd', 'e', 'é', 'f', 'g', 'h', 'i', 'í', 'j', 'k', 'l', 'm', 'n', 'o', 'ó',
               'p', 'q', 'r', 's', 't', 'u', 'ú', 'v', 'w', 'x', 'y', 'z', '{', '|', '}', '~']
        self.count_letras = 100
        for c in str(self.motivo):
            for l in abc:
                if l == c:
                    self.count_letras -= 1
        if self.count_letras < 0:
            raise Warning('Solo pueden haber 100 caracteres, se paso ' + str(abs(self.count_letras)) + ' caracteres')


class einvoice_resumen_diario(models.Model):
    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('einvoice.resumen.diario.secue')
        vals['identificador'] = seq
        if 'resumendetalle_ids' in vals:
            for idx, line in enumerate(vals['resumendetalle_ids']):
                line[2]['sequence'] = idx + 1
        return super(einvoice_resumen_diario, self).create(vals)

    @api.multi
    def do_resumen_diario_tasks(self):
        global ruc, razon
        count = 0
        ruc = self.env['res.company'].browse(1)
        razon = self.env['res.company'].browse(1)

        for resumen in self.env['einvoice.resumen.diario'].browse(self.id):
            c = firma('', "", '')
            d = UBLVersion()
            n = customizationID()
            o = id(str(self.identificador))
            e1 = ReferenceDate(str(self.fecha_doc))
            e2 = issueDateComunicacion(str(self.fecha_resumen))
            # g = invoiceTypeCode()
            h = documentCurrencyCode()
            i = declaracionFirma('SignSUNAT', ruc.x_ruc, razon.name, '#SignSUNAT')

            j = DatosProveedor(razon.x_ruc,
                               '6',
                               razon.name,
                               str(razon.partner_id.zip),
                               str(razon.partner_id.street),
                               str(razon.partner_id.state_id.name),
                               str(razon.partner_id.state_id.name),
                               str(razon.partner_id.state_id.name),
                               razon.name,
                               str(razon.partner_id.zip))

            # f = open(r'D:\notacredito.XML', 'w')
            nombre = self.generate_document_name(ruc.x_ruc)

            f = open(nombre, 'w')
            xm = doc.toprettyxml()

            xm = xm.replace('<?xml version="1.0" ?>',
                            '<?xml version="1.0" encoding="ISO-8859-1" standalone="no"?><SummaryDocuments xmlns="urn:sunat:names:specification:ubl:peru:schema:xsd:SummaryDocuments-1" xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2" xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2" xmlns:ds="http://www.w3.org/2000/09/xmldsig#" xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2" xmlns:sac="urn:sunat:names:specification:ubl:peru:schema:xsd:SunatAggregateComponents-1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">')
            f.write(xm)
            f.write('<ext:UBLExtensions>\n')
            # f.write(b)
            f.write(c)
            f.write('</ext:UBLExtensions>\n')
            f.write(d)
            f.write(n)
            f.write(o)
            f.write(e1)
            f.write(e2)
            # f.write(h)
            f.write(i)
            f.write(j)

            for line in resumen.resumendetalle_ids:
                count += 1
                z = lineas_resumen(str(count),
                                   str(line.tipo_documento),
                                   str(line.serie),
                                   str(line.correlativo_inicio),
                                   str(line.correlativo_fin),
                                   str(line.importe_total_venta),
                                   str(line.ventas_gravadas),
                                   str(line.ventas_exoneradas),
                                   str(line.ventas_inafectas),
                                   str(line.importe_otros_items),
                                   str(line.total_isc),
                                   str(line.total_igv),
                                   str(line.total_otros_tributos))
                f.write(z)
            f.write('</SummaryDocuments>')
            f.close()

            rfirmado = ResumenDiario()
            valor_resumen = rfirmado.sign_xml(fichero_xml=nombre)
            self.write({'digest_value': str(valor_resumen)})

            envio = envioBaja()
            nombre2 = nombre.replace(".xml", "")
            print(nombre2)
            p5 = nombre2.find('envio')
            pathrecortado = str(nombre2[p5 + 6::])
            print('>>>>>>' + pathrecortado)
            ticket = envio.Envio(zip=pathrecortado + '.zip')
            self.write({'ticket': str(ticket)})
            return {
                'type': 'ir.actions.client',
                'tag': 'action_warn',
                'name': _('Aviso'),
                'params': {
                    'title': _('Aviso'),
                    'text': _(u'Resumen Diario Enviado y Ticket Recepcionado!'),
                    'sticky': False
                }}

    def generate_document_name(self, tdoc):
        path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models/archivos/envio'))
        path = path.replace('\\', '/')
        base_dir = r"" + path

        filename = tdoc + '-' + str(self.identificador) + '.xml'
        # TODO: Add types as constants in diferent classes
        return os.path.join(base_dir, filename)

    _name = "einvoice.resumen.diario"
    _rec_name = 'identificador'
    _description = 'Resumen diario'

    identificador = fields.Char(string='N°')
    fecha_resumen = fields.Date(string="Fecha de la Generacion del resumen",
                                default=lambda *a: datetime.now().strftime('%Y-%m-%d'), required=True)
    fecha_doc = fields.Date(string="Fecha de emisión de los documentos", required=True)
    resumendetalle_ids = fields.One2many('einvoice.detalle.resumen.diario',
                                         'resumen_id',
                                         ondelete='cascade',
                                         copy=True)
    # move_line_ids = fields.One2many('account.move.line', 'resumen_id', 'Entry lines'),
    digest_value = fields.Char(string='Resumen')
    ticket = fields.Char(string='Ticket')


class einvoice_detalle_resumen_diario(models.Model):
    def get_series(self):
        lst = []
        query = "SELECT DISTINCT SUBSTRING(number,0,5) as serie FROM account_invoice ai INNER JOIN account_journal aj ON ai.journal_id = aj.id where number is not null AND aj.code = '03'"
        self._cr.execute(query)
        resultados = self._cr.dictfetchall()
        for sel in resultados:
            lst.append((sel['serie'], sel['serie']))
        return lst

    @api.onchange('serie', 'correlativo_inicio', 'correlativo_fin', 'tipo_documento')
    def onchange_place(self):
        print('>>>>>Entre>>>>>>')
        s = {}
        if self.tipo_documento and self.tipo_documento == '03':
            if self.serie and self.correlativo_inicio and self.correlativo_fin:
                query = "SELECT SUBSTRING(ai.number,0,5) AS serie, aic.conceptos_tributarios, SUM(aic.monto_total) AS monto_total FROM account_invoice_conceptos aic INNER JOIN account_invoice ai  ON aic.invoice_id = ai.id WHERE SUBSTRING(ai.number,0,5) = %s AND aic.conceptos_tributarios = '1' AND SUBSTRING(ai.number,6,13) BETWEEN %s AND %s GROUP BY 1,2 UNION SELECT SUBSTRING(ai.number,0,5) AS serie,aic.conceptos_tributarios, SUM(aic.monto_total) AS monto_total FROM account_invoice_conceptos aic INNER JOIN  account_invoice ai  ON aic.invoice_id = ai.id WHERE SUBSTRING(ai.number,0,5) = %s AND aic.conceptos_tributarios = '2' AND SUBSTRING(ai.number,6,13) BETWEEN %s AND %s GROUP BY 1,2 UNION SELECT SUBSTRING(ai.number,0,5) AS serie,aic.conceptos_tributarios, SUM(aic.monto_total) AS monto_total FROM account_invoice_conceptos aic INNER JOIN account_invoice ai ON aic.invoice_id = ai.id WHERE SUBSTRING(ai.number,0,5) = %s AND aic.conceptos_tributarios = '3' AND SUBSTRING(ai.number,6,13) BETWEEN %s AND %s GROUP BY 1,2"
                self._cr.execute(query, (
                    self.serie.upper(), str(self.correlativo_inicio).zfill(8), str(self.correlativo_fin).zfill(8),
                    self.serie.upper(), str(self.correlativo_inicio).zfill(8), str(self.correlativo_fin).zfill(8),
                    self.serie.upper(), str(self.correlativo_inicio).zfill(8), str(self.correlativo_fin).zfill(8),))
                sente = self._cr.dictfetchall()
                for s in sente:
                    conce = s['conceptos_tributarios']
                    if conce == 1:
                        monto = s['monto_total']
                        self.ventas_gravadas = monto
                        self.ventas_exoneradas = 0.0
                        self.ventas_inafectas = 0.0
                    if conce == 3:
                        monto = s['monto_total']
                        self.ventas_exoneradas = monto
                        self.ventas_inafectas = 0.0
                        self.ventas_gravadas = 0.0
                    if conce == 2:
                        monto = s['monto_total']
                        self.ventas_inafectas = monto
                        self.ventas_gravadas = 0.0
                        self.ventas_exoneradas = 0.0

        elif self.tipo_documento and self.tipo_documento == '07':
            if self.serie and self.correlativo_inicio and self.correlativo_fin:
                query = "SELECT SUBSTRING(ai.number,0,5) as serie, aic.conceptos_tributarios, SUM(aic.monto_total) as monto_total FROM account_invoice_conceptos aic INNER JOIN account_invoice ai  ON aic.invoice_id = ai.id INNER JOIN einvoice_nota_credito enc ON enc.referencia = ai.id WHERE SUBSTRING(ai.number,0,5) = %s AND aic.conceptos_tributarios = '1' AND SUBSTRING(ai.number,6,13) BETWEEN %s AND %s GROUP BY 1,2 UNION SELECT SUBSTRING(ai.number,0,5) as serie,aic.conceptos_tributarios, SUM(aic.monto_total) as monto_total FROM account_invoice_conceptos aic INNER JOIN  account_invoice ai  ON aic.invoice_id = ai.id INNER JOIN einvoice_nota_credito enc ON enc.referencia = ai.id WHERE SUBSTRING(ai.number,0,5) = %s AND aic.conceptos_tributarios = '2' AND SUBSTRING(ai.number,6,13) BETWEEN %s AND %s GROUP BY 1,2 UNION SELECT SUBSTRING(ai.number,0,5) as serie,aic.conceptos_tributarios, SUM(aic.monto_total) as monto_total FROM account_invoice_conceptos aic INNER JOIN account_invoice ai ON aic.invoice_id = ai.id INNER JOIN einvoice_nota_credito enc ON enc.referencia = ai.id WHERE SUBSTRING(ai.number,0,5) = %s AND aic.conceptos_tributarios = '3' AND SUBSTRING(ai.number,6,13) BETWEEN %s AND %s GROUP BY 1,2"

                self._cr.execute(query, (
                    self.serie.upper(), str(self.correlativo_inicio).zfill(8), str(self.correlativo_fin).zfill(8),
                    self.serie.upper(), str(self.correlativo_inicio).zfill(8), str(self.correlativo_fin).zfill(8),
                    self.serie.upper(), str(self.correlativo_inicio).zfill(8), str(self.correlativo_fin).zfill(8),))
                sente = self._cr.dictfetchall()
                for s in sente:
                    conce = s['conceptos_tributarios']
                    if conce == 1:
                        monto = s['monto_total']
                        self.ventas_gravadas = monto
                    if conce == 3:
                        monto = s['monto_total']
                        self.ventas_exoneradas = monto
                    if conce == 2:
                        monto = s['monto_total']
                        self.ventas_inafectas = monto

        elif self.tipo_documento and self.tipo_documento == '08':
            if self.serie and self.correlativo_inicio and self.correlativo_fin:
                query = "SELECT SUBSTRING(ai.number,0,5) as serie, aic.conceptos_tributarios, SUM(aic.monto_total) as monto_total FROM account_invoice_conceptos aic INNER JOIN account_invoice ai  ON aic.invoice_id = ai.id INNER JOIN einvoice_nota_debito enc ON enc.referencia = ai.id WHERE SUBSTRING(ai.number,0,5) = %s AND aic.conceptos_tributarios = '1' AND SUBSTRING(ai.number,6,13) BETWEEN %s AND %s GROUP BY 1,2 UNION SELECT SUBSTRING(ai.number,0,5) as serie,aic.conceptos_tributarios, SUM(aic.monto_total) as monto_total FROM account_invoice_conceptos aic INNER JOIN  account_invoice ai  ON aic.invoice_id = ai.id INNER JOIN einvoice_nota_debito enc ON enc.referencia = ai.id WHERE SUBSTRING(ai.number,0,5) = %s AND aic.conceptos_tributarios = '2' AND SUBSTRING(ai.number,6,13) BETWEEN %s AND %s GROUP BY 1,2 UNION SELECT SUBSTRING(ai.number,0,5) as serie,aic.conceptos_tributarios, SUM(aic.monto_total) as monto_total FROM account_invoice_conceptos aic INNER JOIN account_invoice ai ON aic.invoice_id = ai.id INNER JOIN einvoice_nota_debito enc ON enc.referencia = ai.id WHERE SUBSTRING(ai.number,0,5) = %s AND aic.conceptos_tributarios = '3' AND SUBSTRING(ai.number,6,13) BETWEEN %s AND %s GROUP BY 1,2"

                self._cr.execute(query, (
                    self.serie.upper(), str(self.correlativo_inicio).zfill(8), str(self.correlativo_fin).zfill(8),
                    self.serie.upper(), str(self.correlativo_inicio).zfill(8), str(self.correlativo_fin).zfill(8),
                    self.serie.upper(), str(self.correlativo_inicio).zfill(8), str(self.correlativo_fin).zfill(8),))
                sente = self._cr.dictfetchall()
                for s in sente:
                    conce = s['conceptos_tributarios']
                    if conce == 1:
                        monto = s['monto_total']
                        self.ventas_gravadas = monto
                    if conce == 3:
                        monto = s['monto_total']
                        self.ventas_exoneradas = monto
                    if conce == 2:
                        monto = s['monto_total']
                        self.ventas_inafectas = monto
        else:
            raise except_orm(_('Error!'), _("Vuelva a elegir un tipo de comprobante correcto!!!!!!!!"))

        return {'value': s}

    @api.one
    @api.depends('ventas_gravadas', 'ventas_exoneradas',
                 'ventas_inafectas', 'importe_otros_items', 'total_isc', 'total_igv', 'total_otros_tributos',
                 'importe_total_venta')
    def _compute_monto(self):
        tigv = (self.ventas_gravadas + self.ventas_exoneradas + self.ventas_inafectas + self.importe_otros_items)
        self.total_igv = ((tigv * 0.18) or 0.0)
        self.importe_total_venta = tigv + self.total_igv

    _name = "einvoice.detalle.resumen.diario"
    _description = 'Detalle de resumen diario'
    sequence = fields.Integer(string='N#', default=1)
    tipo_documento = fields.Selection([('03', 'Boletas'), ('07', 'Nota de Credito'), ('08', 'Nota de Debito')],
                                      'Tipo Documento', default='03')
    # serie = fields.Char(string='Serie')
    serie = fields.Selection(get_series, string='Serie')
    # serie = fields.Many2one('account.invoice', string='Serie', domain='')
    correlativo_inicio = fields.Char(string='Inicio de Rango')
    correlativo_fin = fields.Char(string='Fin de Rango')
    ventas_gravadas = fields.Float(string='Total ventas gravadas', default=0.00, digits=dp.get_precision('Account'))
    ventas_exoneradas = fields.Float(string='Total ventas exoneradas', default=0.00, digits=dp.get_precision('Account'))
    ventas_inafectas = fields.Float(string='Total ventas inafectas', default=0.00, digits=dp.get_precision('Account'))
    importe_otros_items = fields.Float(string='Sumatorio otros cargos del Item', default=0.00,
                                       digits=dp.get_precision('Account'))
    total_isc = fields.Float(string='Total ISC', default=0.00, digits=dp.get_precision('Account'))
    total_igv = fields.Float(compute='_compute_monto', string='Total IGV', default=0.00,
                             digits=dp.get_precision('Account'))
    total_otros_tributos = fields.Float(string='Total Otros Tributos', default=0.00, digits=dp.get_precision('Account'))
    importe_total_venta = fields.Float(compute='_compute_monto', string='Importe total', default=0.00,
                                       digits=dp.get_precision('Account'), help="Importe total de la venta o servicio")
    resumen_id = fields.Many2one('einvoice.resumen.diario', string='Detalle Resumen Diario', ondelete='cascade')


class einvoice_extractos(models.Model):
    # funcion que permite quitar los sheet al modulo
    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        res = models.Model.fields_view_get(self, cr, uid, view_id=view_id, view_type=view_type, context=context,
                                           toolbar=toolbar, submenu=submenu)
        if view_type == 'form':
            doc = etree.XML(res['arch'])
            for sheet in doc.xpath("//sheet"):
                parent = sheet.getparent()
                index = parent.index(sheet)
                for child in sheet:
                    parent.insert(index, child)
                    index += 1
                parent.remove(sheet)
            res['arch'] = etree.tostring(doc)
        return res

    _inherit = "account.bank.statement"
    debitos = fields.Float(string='Debitos', default=0.00, digits=dp.get_precision('Account'))
    creditos_depositos = fields.Float(string='Creditos/Depositos', default=0.00, digits=dp.get_precision('Account'))
    descripcion = fields.Char(string='Descripcion')
    codigo_transaccion = fields.Char(string='Codigo Transaccion')
    balance_end_dolares = fields.Float(string='Saldo Calculado Dolares', compute='_end_balance_dolares', store=True)

    @api.one
    @api.depends('line_ids.importe_extranjera')
    def _end_balance_dolares(self):
        # print ('ddddddd')
        self.balance_end_dolares = sum(line.importe_extranjera for line in self.line_ids)

    @api.multi
    def button_dummy(self):
        res = super(einvoice_extractos, self).button_dummy()
        self.balance_end_real = self.balance_end or 0.0
        return res


class einvoice_extractos_line(models.Model):
    @api.multi
    def send_mail_template(self):
        """ Open a window to compose an email, with the edi invoice template
            message loaded by default
        """
        assert len(self) == 1, 'This option should only be used for a single id at a time.'
        # template = self.env.ref('account.email_template_edi_invoice')
        template = self.env.ref('comprobantes_sunat.example_email_template', False)
        compose_form = self.env.ref('mail.email_compose_message_wizard_form')

        # par = self.env['account.bank.statement.line'].search([['id', '=', self.id]], limit=1)
        par = self.env['account.invoice'].search([['number', '=', self.ref]], limit=1)
        # print(par.partner_id.id)

        ctx = dict(
            default_model='account.invoice',
            default_res_id=par.id,
            default_use_template=bool(template),
            default_new_template_id=template.id,
            default_composition_mode='comment',
            mark_invoice_as_sent=False,
            # default_bank_line_id = self.id,
        )
        print(ctx)
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }

    @api.one
    @api.depends('amount', 'importe_nacional')
    def _compute_h(self):
        if self.amount:
            self.importe_nacional = self.amount
            if self.amount < 0:
                currency = \
                self.env['res.currency.rate'].search([['currency_id.name', '=', 'USD'], ['name', '=', self.date]])[
                    'rate_compra']
            else:
                currency = \
                self.env['res.currency.rate'].search([['currency_id.name', '=', 'USD'], ['name', '=', self.date]])[
                    'rate']

            if self.statement_id.journal_id.currency.id == 3:
                ### Dolares
                self.importe_nacional = (self.amount / currency) or 0.0
                self.importe_extranjera = self.amount
                # self.importe_extranjera = self.importe_nacional  * currency
            else:
                ### Soles
                self.importe_nacional = self.amount or 0.0
                self.importe_extranjera = (self.amount * currency) or 0.0

    _inherit = ['mail.thread']
    _inherit = 'account.bank.statement.line'
    importe_nacional = fields.Float(string='Importe Moneda Nacional Soles', default=0.00, digits_compute=dp.get_precision('Account'), compute="_compute_h", store=True)
    # importe_nacional = fields.Float(string='Importe Moneda Nacional Soles', default=0.00, digits_compute=dp.get_precision('Account'), readonly=True, store=True)
    entrega_factura = fields.Boolean(string='Entrega Factura Física')
    importe_extranjera = fields.Float(string='Importe Moneda Extranjera Dolares', default=0.00, digits_compute=dp.get_precision('Account'), compute="_compute_h", store=True)
    adjunto = fields.Char(string='Factura', type="binary", nodrop=True, readonly=True)
    line_detail_ids = fields.One2many(comodel_name="einvoice.extract.line.detail", inverse_name="line_detail_id",
                                      string="Detalle")

    @api.multi
    def calcular_montos_totales(self):
        # print (self._context)
        amount = sum(line.amount for line in self.line_detail_ids)
        amount_currency = sum(line.amount_currency for line in self.line_detail_ids)
        importe_nacional = sum(line.importe_nacional for line in self.line_detail_ids)
        importe_extranjera = sum(line.importe_extranjera for line in self.line_detail_ids)
        self.amount = amount
        self.amount_currency = amount_currency
        self.importe_nacional = importe_nacional
        self.importe_extranjera = importe_extranjera


class einvoice_extract_line_detail(models.Model):



    _name = 'einvoice.extract.line.detail'
    date = fields.Date('Fecha', required=True)
    name = fields.Char('Comunicación', required=True)
    ref = fields.Char('Referencia')
    partner_id = fields.Many2one('res.partner', 'Empresa')
    amount = fields.Float('Monto',  digits=(16, 3))
    amount_currency = fields.Float('Monto Divisa', digits_compute=dp.get_precision('Account'))
    currency_id = fields.Many2one('res.currency', 'Moneda')
    importe_nacional = fields.Float(string='Importe Moneda Nacional Soles', digits_compute=dp.get_precision('Account'))
    importe_extranjera = fields.Float(string='Importe Moneda Extranjera Dolares', digits=(16, 3))
    # importe_extranjera = fields.Float(string='Importe Moneda Extranjera Dolares', digits=dp.get_precision('Product Price'), compute='_compute_2', inverse='_compute_3', store=True)
    tipo_cambio_actual = fields.Float(string='Tipo de Cambio', digits=dp.get_precision('Account'),
                                      compute="_compute_tipo", store=True)

    line_detail_id = fields.Many2one('account.bank.statement.line', 'Detalle', ondelete='cascade')

    @api.one
    @api.depends('date', 'amount')
    def _compute_tipo(self):
        if self.amount:
            if self.amount < 0:
                currency = \
                self.env['res.currency.rate'].search([['currency_id.name', '=', 'USD'], ['name', '=', self.date]])[
                    'tc_compra_rate']
            elif self.amount > 0:
                currency = \
                self.env['res.currency.rate'].search([['currency_id.name', '=', 'USD'], ['name', '=', self.date]])[
                    'tc_venta_rate']
            self.tipo_cambio_actual = currency

    # @api.one
    # @api.depends('date', 'amount')
    @api.onchange('amount')
    def _compute_moneda_extranjera(self):
        if self.amount:
            print ('_compute_moneda_extranjera')
            print (self._context)
            print ('_compute_moneda_extranjera')
            id_line_extracto = self._context.get('line_detail', False)
            if not id_line_extracto:
                id_line_extracto = self._context.get('id_extracto_line', False)
                obj_extracto = self.env['account.bank.statement.line'].browse(id_line_extracto)
                moneda = obj_extracto.statement_id.journal_id.currency.id
            obj_extracto = self.env['account.bank.statement.line'].browse(id_line_extracto)
            moneda = obj_extracto.statement_id.journal_id.currency.id
            if obj_extracto:
                if self.amount < 0:
                    currency = \
                    self.env['res.currency.rate'].search([['currency_id.name', '=', 'USD'], ['name', '=', self.date]])[
                        'rate_compra']
                elif self.amount > 0:
                    currency = \
                    self.env['res.currency.rate'].search([['currency_id.name', '=', 'USD'], ['name', '=', self.date]])[
                        'rate']

                if moneda == 3:
                    ### Dolares
                    self.importe_nacional = (self.amount / currency) or 0.0
                    self.importe_extranjera = self.amount
                else:
                    ### Soles
                    self.importe_extranjera = (self.amount * currency) or 0.0
                    self.importe_nacional = self.amount

    @api.onchange('importe_extranjera')
    def _inverse_extranjera(self):
        if self.importe_extranjera:
            id_line_extracto = self._context.get('id_extracto_line', False)
            obj_extracto = self.env['account.bank.statement.line'].browse(id_line_extracto)
            if self.importe_extranjera < 0:
                currency = \
                self.env['res.currency.rate'].search([['currency_id.name', '=', 'USD'], ['name', '=', self.date]])[
                    'rate_compra']
            elif self.importe_extranjera > 0:
                currency = \
                self.env['res.currency.rate'].search([['currency_id.name', '=', 'USD'], ['name', '=', self.date]])[
                    'rate']

            self.importe_nacional = (self.importe_extranjera / currency) or 0.0
            if obj_extracto.statement_id.journal_id.currency.id == 3:
                self.amount = self.importe_extranjera
            else:
                self.amount = self.importe_nacional

            # self.importe_extranjera = ss
        # pass


    @api.onchange('importe_nacional')
    def _importe_nacional_onchange(self):
        print('_importe_nacional_onchange')
        if self.importe_nacional:
            id_line_extracto = self._context.get('id_extracto_line', False)
            obj_extracto = self.env['account.bank.statement.line'].browse(id_line_extracto)
            if obj_extracto:
                if self.importe_nacional < 0:
                    currency = \
                    self.env['res.currency.rate'].search([['currency_id.name', '=', 'USD'], ['name', '=', self.date]])[
                        'rate_compra']
                elif self.importe_nacional > 0:
                    currency = \
                    self.env['res.currency.rate'].search([['currency_id.name', '=', 'USD'], ['name', '=', self.date]])[
                        'rate']

                self.importe_extranjera = (self.importe_nacional * currency) or 0.0
                if obj_extracto.statement_id.journal_id.currency.id == 3:
                    self.amount = self.importe_extranjera
                else:
                    self.amount = self.importe_nacional

    # @api.onchange('amount')
    # def _importe_amount_change(self):
    #     if self.amount:
    #         id_line_extracto = self._context.get('id_extracto', False)
    #         obj_extracto = self.env['account.bank.statement.line'].browse(id_line_extracto)
    #         if self.amount < 0:
    #             currency = \
    #             self.env['res.currency.rate'].search([['currency_id.name', '=', 'USD'], ['name', '=', self.date]])[
    #                 'rate_compra']
    #         elif self.amount > 0:
    #             currency = \
    #             self.env['res.currency.rate'].search([['currency_id.name', '=', 'USD'], ['name', '=', self.date]])[
    #                 'rate']
    #         else:
    #             currency = 0.0
    #         if obj_extracto.statement_id.journal_id.currency.id == 3:
    #             print('entreeeeee efefef')
    #             self.importe_nacional = (self.amount * currency) or 0.0
    #             self.importe_extranjera = self.amount
    #         else:
    #             print('entreeeeee efesssssssssssss-------fef')
    #             self.importe_extranjera = (self.amount * currency) or 0.0
    #             self.importe_nacional = self.amount


class mail_compose_message(models.Model):
    _inherit = 'mail.compose.message'

    @api.multi
    def send_mail(self):
        context = self._context
        if context.get('default_model') == 'account.invoice' and context.get('default_res_id') and context.get(
                'mark_invoice_as_sent') == False:
            par = self.env['account.invoice'].search([['id', '=', context['default_res_id']]], limit=1)
            id_line = self.env['account.bank.statement.line'].search([['ref', '=', par.number], ['amount', '>', 0]],
                                                                     limit=1)
            statement = self.env['account.bank.statement.line'].browse(id_line.id)
            print('ssssssss>>>>', str(statement))
            statement.write({'entrega_factura': True})
            # statement.message_post(body=_("Invoice sent"))
        return super(mail_compose_message, self).send_mail()


def elimina_tildes(cadena):
    s = ''.join((c for c in unicodedata.normalize('NFD', unicode(cadena)) if unicodedata.category(c) != 'Mn'))
    return s.decode()