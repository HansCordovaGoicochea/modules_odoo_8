# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# try:
from PIL import Image, ImageEnhance, ImageFilter
# except ImportError:
#     from PIL import Image
import pytesseract


def ir_sunat_web(dni):
    driver = webdriver.Firefox()
    # Fijamos nuestra página objetivo
    driver.get("http://ww1.sunat.gob.pe/cl-ti-itmrconsruc/jcrS00Alias")
    try:
        # Debido a que la página tiene frames debemos hacer el cambio al frame con nombre "leftFrame"
        driver.switch_to_frame("leftFrame")
    except:
        return []
        driver.close()
    try:
        # Obtenemos los radio buttons que nos permiten seleccionar el tipo de búsqueda a hacer
        # radios = driver.find_elements_by_name("tQuery")
        # # Seleccionamos la búsqueda por DNI
        # radios[1].click()
        # Obtenemos la caja de texto donde se ingresa el DNI
        documento = driver.find_element_by_name("search1")
        # Escribimos el DNI
        documento.send_keys(dni)
        # Esperamos hasta que el texto esté escrito en la caja de texto del DNI
        WebDriverWait(driver, 5).until(EC.text_to_be_present_in_element_value((By.NAME, "search1"), dni))
    except:
        driver.close()
        return []
    try:
        # Esperamos hasta que se cargue la imagen con el captcha
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.NAME, "imagen")))
        # Hacemos la captura de pantalla correspondiente
        driver.save_screenshot("screenshot.jpg")
        img = Image.open('screenshot.jpg')
        # img = img.filter(ImageFilter.MedianFilter())
        # enhancer = ImageEnhance.Contrast(img)
        # img = enhancer.enhance(100)
        # Obtenemos el ancho y el largo de la imagen
        ancho = img.size[0]
        alto = img.size[1]

        # Recortamos la parte del captcha teniendo en cuenta el ancho y el largo de la imagen
        img_recortada = img.crop((int(ancho / 1.4), int(alto / 4.5), int(ancho / 1.25), int(alto / 1.9)))
        # Guardamos el recorte
        img_recortada.save("recorte.png")
        # Obtenemos el texto del captcha
        img_recortada = img_recortada.resize((115, 65), Image.ANTIALIAS)
        img_recortada.save("recorte.png")
        # Obtenermos el path del tererac ORC
        pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files (x86)\\Tesseract-OCR\\tesseract'
        # Obtenemos el texto del captcha
        c = pytesseract.image_to_string(img_recortada)
        captcha = ''
        print (captcha)
        for linea in c:
            if not linea.rstrip() == "":  # salteo lineas en blanco
                captcha += linea.lstrip().rstrip() # saco espacios al
        # Obtenemos la caja de texto donde se escribe el texto del captcha
        codigo = driver.find_element_by_name("codigo")
        # Escribimos el texto
        codigo.send_keys(captcha)
    except:
        driver.close()
        return []
    try:
        # Obtenemos el botón de búsqueda
        boton = driver.find_element_by_class_name("form-button")
        # Damos click al botón de búsqueda
        boton.click()
        # Cambiamos al frame por defecto
        driver.switch_to_default_content()
        # Cambiamos al frame llamado "mainFrame" que contiene la tabla de resultados con un enlace conteniendo el ruc
        driver.switch_to_frame("mainFrame")
    except:
        driver.close()
        return []
    try:
        # Esperamos que se cargue la tabla de resultados
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "form-table")))
        # Obtenemos el enlace que contiene al RUC
        # enlace = driver.find_element(By.TAG_NAME, "a")
        # Le damos click al enlace
        # enlace.click()
        # Ahora si tenemos una tabla que contiene el detalle de los resultados del RUC consultado
        # Obtenemos todas las filas
        trs = driver.find_elements(By.TAG_NAME, "tr")
        # Obtenemos las celdas de la primera fila
        tds = trs[0].find_elements(By.TAG_NAME, "td")
        # A la segunda celda la partimos ya que tiene el ruc y la razón social separados por un guión
        primera_linea = tds[1].text.split('-')
        ruc = primera_linea[0].strip()
        razon_social = primera_linea[1].strip()
        # Obtenemos la segunda linea que tiene el tipo de contribuyente
        tds = trs[1].find_elements(By.TAG_NAME, "td")
        tipo_contribuyente = tds[1].text.strip()
        # Obtenemos la dirección
        tds = trs[7].find_elements(By.TAG_NAME, "td")
        direccion = tds[1].text.strip()
    except:
        print ('fdddddd')
        # driver.close()
        return []
    driver.close()
    # Devolvemos una lista con los resultados.
    datos = [ruc, razon_social, tipo_contribuyente, direccion]
    return datos


def main():
    # Ingresar DNI
    dni = '20546564674'
    print ir_sunat_web(dni)


main()