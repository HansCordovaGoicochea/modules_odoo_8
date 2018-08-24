# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# try:
from PIL import Image
# except ImportError:
#     from PIL import Image
import pytesseract

from PIL import Image, ImageEnhance, ImageFilter

#
img = Image.open('screenshot.jpg')
# img = img.filter(ImageFilter.MedianFilter())
# enhancer = ImageEnhance.Contrast(img)
# img = enhancer.enhance(5)
# img = img.convert('1')
# Obtenemos el ancho y el largo de la imagen
ancho = img.size[0]
alto = img.size[1]
print (ancho, alto)
# Recortamos la parte del captcha teniendo en cuenta el ancho y el largo de la imagen
img_recortada = img.crop((int(ancho / 1.4), int(alto / 4.5), int(ancho / 1.25), int(alto/1.9)))
# Guardamos el recorte
# print (img_recortada)
img_recortada.save("sdfdsfsfd.png")
# Obtenemos el texto del captcha
img_recortada = img_recortada.resize((115, 65), Image.ANTIALIAS)
img_recortada.save("sdfdsfsfd.png")
# print (img_recortada)
pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files (x86)\\Tesseract-OCR\\tesseract'
# Include the above line, if you don't have tesseract executable in your PATH
# Example tesseract_cmd: 'C:\\Program Files (x86)\\Tesseract-OCR\\tesseract'
c = str(pytesseract.image_to_string(img_recortada))
print (c)
captcha = ''
for linea in c:
    if not linea.rstrip() == "":  # salteo lineas en blanco
        captcha += linea.lstrip().rstrip() # saco espacios al
print captcha
# Obtenemos la caja de texto donde se escribe el texto del captcha
# codigo = driver.find_element_by_name("codigo")
# Escribimos el texto
# codigo.send_keys(captcha)

