#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Url: http://www.pythondiario.com
# Autor: Diego Caraballo

# --------------- agregado---------------------------

from urllib2 import URLError

from openerp.osv.orm import browse_null
from selenium.common.exceptions import WebDriverException
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver import FirefoxProfile
# --------------- fin -----------------------------

from selenium import webdriver
import time
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

# browser = webdriver.Firefox(executable_path="E:/geckodriver.exe",
#                                     log_path="E:/geckodriver.log")  # para FIRE FOX

from openerp.http import request
import os
import socket


class sunatSelenium(object):
    def sunatUno(self, rucs, user, clave):

        # socket.gethostbyname(socket.gethostname())
        # socket.gethostbyname_ex(socket.gethostname())

        ip = str(request.httprequest.remote_addr)

        print ip

        # si la IP es local se ejecutar el driver de chromme
        # si no buscara el driver en la maquina remota

        if ip == '127.0.0.1':
            browser = webdriver.Chrome(executable_path="C:\Program Files (x86)\Odoo 8.0-20150411\server\openerp\\modulosnuevos\\vrcontadores\chromedriver.exe")  # para Chrome
        else:
            ce = "http://192.168.1.6:4444/wd/hub"
            browser = webdriver.Remote(
                command_executor=ce,
                desired_capabilities={
                    "browserName": os.environ.get("browser", "chrome"),
                    # 'javascriptEnabled': True
                }
            )

        browser.get("https://e-menu.sunat.gob.pe/cl-ti-itmenu/MenuInternet.htm")
        time.sleep(3)

        btn = browser.find_element_by_id("btnPorRuc")
        btn.click()

        # Datos que extraemos de la pagina inspeccionando elemento
        ruc = browser.find_element_by_id("txtRuc")
        ruc.clear()
        username = browser.find_element_by_id("txtUsuario")
        username.clear()
        password = browser.find_element_by_id("txtContrasena")
        password.clear()

        # Cambiar las credenciales
        ruc.send_keys(rucs)
        username.send_keys(user)
        password.send_keys(clave)

        # Emula el hacer click en "Iniciar Sesion"
        # login_attempt = browser.find_element_by_xpath("//*[@type='submit']")
        if clave:
            login_attempt = browser.find_element_by_id("btnAceptar")
            login_attempt.click()
            browser.execute_script('''alert('Porfavor cerrar la ventana Negra que fue iniciada - Conexión SUNAT');''')

        else:
            browser.execute_script('''alert('Porfavor Complete sus Datos!!!!!');''')
        # MATAR PROCESO PARA QUE NO SE CIERRE EL CHROME
        os.system("TASKKILL /F /IM chromedriver.exe")

    def sunatDos(self, rucs, user, clave):

        ip = str(request.httprequest.remote_addr)
        # si la IP es local se ejecutar el driver de chromme
        # si no buscara el driver en la maquina remota

        if ip == '127.0.0.1':
            browser = webdriver.Chrome(executable_path="C:\Program Files (x86)\Odoo 8.0-20150411\server\openerp\\modulosnuevos\\vrcontadores\chromedriver.exe")  # para Chrome
        else:
            ce = "http://192.168.1.6:4444/wd/hub"
            browser = webdriver.Remote(
                command_executor=ce,
                desired_capabilities={
                    "browserName": os.environ.get("browser", "chrome"),
                    # 'javascriptEnabled': True
                }
            )


        browser.get(
            'https://www.sunat.gob.pe/xssecurity/SignOnVerification.htm?signonForwardAction=https%3A%2F%2Fwww.sunat.gob.pe%2Fol-at-itcanal%2Fcanal.do')

        time.sleep(3)
        #
        # Datos que extraemos de la pagina inspeccionando elemento
        ruc = browser.find_element_by_id("txtRuc")
        ruc.clear()
        username = browser.find_element_by_id("txtUsuario")
        username.clear()
        password = browser.find_element_by_id("txtContrasena")
        password.clear()

        # Cambiar las credenciales
        ruc.send_keys(rucs)
        username.send_keys(user)
        password.send_keys(clave)

        # Emula el hacer click en "Iniciar Sesion"
        # login_attempt = browser.find_element_by_xpath("//*[@type='submit']")
        if clave:
            login_attempt = browser.find_element_by_id("btnAceptar")
            login_attempt.click()
            browser.refresh()
            browser.execute_script('''alert('Porfavor cerrar la ventana Negra que fue iniciada - Conexión SUNAT');''')
        else:
            browser.execute_script('''alert('Porfavor Complete sus Datos!!!!!');''')
        os.system("TASKKILL /F /IM chromedriver.exe")