# -*- coding: utf-8 -*- 
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

try:
    import Image
except ImportError:
    from PIL import Image
import pytesseract


def ir_reniec_web(dni):
    fp = webdriver.FirefoxProfile()
    driver = webdriver.Firefox(fp)
    # Definimos nuestra página objetivo
    driver.get("https://cel.reniec.gob.pe/valreg/valreg.do")
    try:
        # Esperamos hasta que se cargue la imagen con el captcha
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "imagcodigo")))
    except:
        print "Element is not present"
    # Hacemos la captura de pantalla correspondiente
    driver.save_screenshot("screenshot.png")
    img = Image.open('screenshot.png')
    # Obtenemos el ancho y el largo de la imagen
    ancho = img.size[0]
    alto = img.size[1]
    # Recortamos la parte del captcha teniendo en cuenta el ancho y el largo de la imagen
    img_recortada = img.crop((int(ancho / 4.26), int(alto / 3.64), int(ancho / 2.8), int(alto / 3)))
    # Guardamos el recorte
    img_recortada.save("recorte.png")
    # Recorremos cada uno de los dígitos del DNI
    for num in dni:
        # Buscamos el boton que tenga como nombre tecla_0
        boton_0 = driver.find_element_by_name("tecla_0")
        # Obtenemos el valor del botón con nombre tecla_0
        valor_0 = boton_0.get_attribute('value')
        # Buscamos el boton que tenga como nombre tecla_1
        boton_1 = driver.find_element_by_name("tecla_1")
        # Obtenemos el valor del botón con nombre tecla_1
        valor_1 = boton_1.get_attribute('value')
        # Buscamos el boton que tenga como nombre tecla_2
        boton_2 = driver.find_element_by_name("tecla_2")
        # Obtenemos el valor del botón con nombre tecla_2
        valor_2 = boton_2.get_attribute('value')
        # Buscamos el boton que tenga como nombre tecla_3
        boton_3 = driver.find_element_by_name("tecla_3")
        # Obtenemos el valor del botón con nombre tecla_3
        valor_3 = boton_3.get_attribute('value')
        # Buscamos el boton que tenga como nombre tecla_4
        boton_4 = driver.find_element_by_name("tecla_4")
        # Obtenemos el valor del botón con nombre tecla_4
        valor_4 = boton_4.get_attribute('value')
        # Buscamos el boton que tenga como nombre tecla_5
        boton_5 = driver.find_element_by_name("tecla_5")
        # Obtenemos el valor del botón con nombre tecla_5
        valor_5 = boton_5.get_attribute('value')
        # Buscamos el boton que tenga como nombre tecla_6
        boton_6 = driver.find_element_by_name("tecla_6")
        # Obtenemos el valor del botón con nombre tecla_6
        valor_6 = boton_6.get_attribute('value')
        # Buscamos el boton que tenga como nombre tecla_7
        boton_7 = driver.find_element_by_name("tecla_7")
        # Obtenemos el valor del botón con nombre tecla_7
        valor_7 = boton_7.get_attribute('value')
        # Buscamos el boton que tenga como nombre tecla_8
        boton_8 = driver.find_element_by_name("tecla_8")
        # Obtenemos el valor del botón con nombre tecla_8
        valor_8 = boton_8.get_attribute('value')
        # Buscamos el boton que tenga como nombre tecla_9
        boton_9 = driver.find_element_by_name("tecla_9")
        # Obtenemos el valor del botón con nombre tecla_9
        valor_9 = boton_9.get_attribute('value')
        '''Consultamos si el dígito del DNI es igual al valor del botón, 
        si es el caso entonces se da click en ese botón'''
        if num == valor_0:
            boton_0.click()
        elif num == valor_1:
            boton_1 = driver.find_element_by_name("tecla_1")
            boton_1.click()
        elif num == valor_2:
            boton_2 = driver.find_element_by_name("tecla_2")
            boton_2.click()
        elif num == valor_3:
            boton_3 = driver.find_element_by_name("tecla_3")
            boton_3.click()
        elif num == valor_4:
            boton_4 = driver.find_element_by_name("tecla_4")
            boton_4.click()
        elif num == valor_5:
            boton_5 = driver.find_element_by_name("tecla_5")
            boton_5.click()
        elif num == valor_6:
            boton_6 = driver.find_element_by_name("tecla_6")
            boton_6.click()
        elif num == valor_7:
            boton_7 = driver.find_element_by_name("tecla_7")
            boton_7.click()
        elif num == valor_8:
            boton_8 = driver.find_element_by_name("tecla_8")
            boton_8.click()
        elif num == valor_9:
            boton_9 = driver.find_element_by_name("tecla_9")
            boton_9.click()
    # Se llama al método romper_captcha para obtener el texto correspondiente
    captcha = romper_captcha("recorte.png")
    try:
        # Obtenemos la caja de texto donde se escribe el texto del captcha
        codigo = driver.find_element_by_name("imagen")
        # Si el captcha está vacio o no se ha logrado romper se cierra el navegador y se termina la aplicación
        if captcha == '':
            driver.close()
            return
        # Escribimos el texto
        codigo.send_keys(captcha)
    except:
        pass
    try:
        # Obtenemos el botón de consulta
        boton_consultar = driver.find_element_by_name("bot_consultar")
        # Damos click al botón de consulta
        boton_consultar.click()
    except:
        print "Element is not present"
        # Obtengo el resultado que aparece en el elemento llamado style2
    resultado = driver.find_element_by_class_name("style2")
    # Partimos el resultado para obtener el nombre
    nombre = resultado.text.split('\n')
    driver.close()
    return nombre[0]


def romper_captcha(nombre_imagen):
    # Abro la imagen
    img = Image.open(nombre_imagen)
    # Obtengo un arreglo de píxeles de la imagen
    pixdata = img.load()
    '''Modifico los píxeles de la imagen de acuerdo al análisis de los colores de las letras 
    y las lineas que cruzan el texto, pintando de negro los píxeles del texto y de blanco las lineas'''
    for y in xrange(img.size[1]):
        for x in xrange(img.size[0]):
            if pixdata[x, y][2] < 146: pixdata[x, y] = (255, 255, 255)
            for y in xrange(img.size[1]):
                for x in xrange(img.size[0]):
                    if pixdata[x, y][1] > 64:
                        pixdata[x, y] = (255, 255, 255)
            else:
                pixdata[x, y] = (0, 0, 0)
    # Guardo la imagen modificada
    img.save("modificado.jpg")
    # Abro la imagen modificado
    image = Image.open("modificado.jpg")
    # Obtenemos el texto de la imagen
    frase = pytesseract.image_to_string(image)
    # Retornamos el texto eliminado los espacios en blanco entre las palabras y convirtiendolas en mayúsculas
    return frase.replace(' ', '').upper()


def main():
    dni = '123456789'
    print ir_reniec_web(dni)


main()