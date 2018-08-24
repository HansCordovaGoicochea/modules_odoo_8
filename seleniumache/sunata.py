# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time

#Ruta donde guardamos chromedriver.exe
# browser = webdriver.Chrome("C:\Users\Admin\Desktop\chromedriver\chromedriver.exe")
browser = webdriver.Firefox(executable_path="C:/Program Files (x86)/Odoo 8.0-20150411/server/openerp/modulosnuevos/vrcontadores/geckodriver.exe", log_path="d:/geckodriver.log") # para FIRE FOX
# browser = webdriver.Chrome("C:/Program Files (x86)/Odoo 8.0-20150411/server/openerp/modulosnuevos/vrcontadores/chromedriver.exe")  # PARA CHROME
browser.get("https://e-menu.sunat.gob.pe/cl-ti-itmenu/MenuInternet.htm")
time.sleep(5)

btn = browser.find_element_by_id("btnPorRuc")
btn.click()

#Datos que extraemos de la pagina inspeccionando elemento
ruc = browser.find_element_by_id("txtRuc")
ruc.clear()
username = browser.find_element_by_id("txtUsuario")
username.clear()
password = browser.find_element_by_id("txtContrasena")
password.clear()

#Cambiar las credenciales
ruc.send_keys("20495932797")
username.send_keys("ADMINSC2")
password.send_keys("CARNAVAL")

# Emula el hacer click en "Iniciar Sesion"
# login_attempt = browser.find_element_by_xpath("//*[@type='submit']")
login_attempt = browser.find_element_by_id("btnAceptar")
login_attempt.click()