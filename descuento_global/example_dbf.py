# coding=utf-8
try:
    import pymysql
except ImportError:
    pass

import os
import zipfile
from dbfread import DBF

import csv
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASS = ''
DB_NAME = 'repositorio'


def show(*words):
    print('  ' + ' '.join(str(word) for word in words))


def show_field(field):
    print('    {} ({} {})'.format(field.name, field.type, field.length))


def conexion_db():
    # Conexion con mysql.
    datos = [DB_HOST, DB_USER, DB_PASS, DB_NAME]
    conn = pymysql.connect(*datos)
    cursor = conn.cursor()  # Creamos un cursor para insertar los datos.
    return conn

def create_db(db_name=''):
    datos = [DB_HOST, DB_USER, DB_PASS]
    db1 = pymysql.connect(*datos)
    cursor = db1.cursor()
    db_existe = 'SHOW DATABASES LIKE "' + db_name + '";'
    resp = cursor.execute(db_existe)
    if resp:
        """EXISTE LA BD"""
        return resp
    else:
        """NO EXISTE LA BD"""
        query = 'CREATE DATABASE IF NOT EXISTS ' + db_name + ';'
        # print(query)
        res = cursor.execute(query)
        return res


def run_query(query=''):
    datos = [DB_HOST, DB_USER, DB_PASS, DB_NAME]

    conn = pymysql.connect(*datos)
    cursor = conn.cursor()
    cursor.execute(query)

    if query.upper().startswith('SELECT'):
        data = cursor.fetchall()
    else:
        conn.commit()
        data = None

    cursor.close()
    conn.close()

    return data


def sql_create_table(db):
    columnas = []
    campos = db.fields
    columnas.append("id INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY")

    for campo in campos:
        tipo = campo.type
        if tipo == "C":
            tmp = "%s VARCHAR(%s)" % (campo.name, campo.length + 1)
            columnas.append(tmp)
        elif tipo in "NF":
            tmp = "%s NUMERIC(%s, %s)" % (campo.name, campo.length, campo.decimal_count)
            columnas.append(tmp)
        elif tipo in "I":
            tmp = "%s INT(%s)" % (campo.name, campo.length)
            columnas.append(tmp)
        elif tipo == "D":
            tmp = "%s DATE" % (campo.name)
            columnas.append(tmp)
        elif tipo == "L":
            tmp = "%s TINYINT(%s)" % (campo.name, 1)
            columnas.append(tmp)
        elif tipo == "M":
            tmp = "%s LONGTEXT" % (campo.name)
            columnas.append(tmp)
        else:
            raise NotImplementedError('Tipo %s no implementado' % tipo)

    q = "CREATE TABLE IF NOT EXISTS %(nombre)s\n(\n%(columnas)s\n);"
    q = q % dict(nombre=db.name.rstrip(".dbf"), columnas=",\n".join(columnas))

    return q

class Record(object):
    def __init__(self, items):
        for name, value in items:
            setattr(self, name, value)

def sql_insert_into(db):
    """ OBS: El id se autoincrementa solo. """

    comilla = "`"
    campos = db.fields
    nombre = comilla + db.name.rstrip(".dbf") + comilla
    columnas = []
    params = []
    for campo in campos:
        columnas.append(comilla + campo.name + comilla)
        params.append("%s")
    q = "INSERT INTO %s (%s) VALUES(%s);" % (nombre, ",\n".join(columnas), ",\n".join(params))
    conex = conexion_db()
    cursor = conex.cursor()  # Creamos un cursor para insertar los datos.
    for record in db:
        # print(record.name)
        # print(tuple(record.values()))
        # print(list(record.values()))
        # print('------')
        cursor.execute(q, tuple(record.values()))

    # Indica a BD que guarde los cambios en la transacción actual
    conex.commit()
    cursor.close()
    conex.close()


# crear base de datos
create_db('repositorio')


# Conexion con el dbf.
for folder, subfolders, files in os.walk('D:\\archivos_dbf'):
    # print(files)
    # leer zip por zip
    for file_zip in files:
        if file_zip.endswith('.zip'):
            stories_zip = zipfile.ZipFile(folder+'/'+file_zip)
            stories_zip.extractall()
            # stories_zip.close()
            # obtener los nombre de los archivos  comprimidos
            for info in stories_zip.infolist():
                # print(info.filename)
                # leer el archivo dbf
                if info.filename.lower().endswith('.dbf'):
                    table = DBF(str(info.filename), lowernames=True, ignore_missing_memofile=True, encoding='LATIN-1')
                    # Estructura de la tabla
                    query_create_table = sql_create_table(table)
                    # print(sql)
                    # Establecer una conexion a mysql y ejecutar el script
                    res = run_query(query_create_table)
                    # print(res)
                    # insertar datos a la tabla
                    query_insert = sql_insert_into(table)
                    # print(query_insert)

                    stories_zip.close()
                    os.remove(str(info.filename))
                    print('----------------------------*********--------------**********---------------')