# coding=utf-8
try:
    import pymysql
    import warnings
    warnings.filterwarnings('error', category=pymysql.Warning)
except ImportError:
    pass

import os
import zipfile
from dbfread import DBF

import csv
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

# DB_HOST = 'localhost'
# DB_USER = 'root'
# DB_PASS = ''
# DB_NAME = 'employees'


class PasarDbfToMysql(object):

    def __init__(self, db_host, db_user, db_pass, db_name, campo_where=None):
        self.DB_HOST = db_host
        self.DB_USER = db_user
        self.DB_PASS = db_pass
        self.DB_NAME = db_name
        self.CAMPO_WHERE = campo_where

    def conexion_db(self, db_name=None):
        # Conexion con mysql.
        datos = [self.DB_HOST, self.DB_USER, self.DB_PASS, self.DB_NAME]
        try:
            conn = pymysql.connect(*datos)
            return conn
        except (pymysql.err.OperationalError, pymysql.ProgrammingError, pymysql.InternalError, pymysql.IntegrityError, TypeError) as message:
            raise Warning("Mysql Error %d:\n%s" % (message[0], message[1]))

    def run_query(self, query=''):

        conn = self.conexion_db()
        cursor = conn.cursor()
        try:
            cursor.execute(query)
        except Warning as a_warning:
            print(a_warning[1])

        if query.upper().startswith('SELECT'):
            data = cursor.fetchall()
        else:
            conn.commit()
            data = None

        cursor.close()
        conn.close()

        return data

    def sql_create_table(self, db):
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

    def sql_insert_into(self, db, columna_where=None):
        """ OBS: El id se autoincrementa solo. """

        comilla = "`"
        campos = db.fields
        nombre = comilla + db.name.rstrip(".dbf") + comilla

        conex = self.conexion_db()
        cursor = conex.cursor()  # Creamos un cursor para insertar los datos.
        for record in db:
            columnas_update = []
            columnas = []
            params = []
            for campo in campos:
                columnas.append(comilla + campo.name + comilla)
                params.append("%s")

                columnas_update.append(comilla + campo.name + comilla + '=' + "%s")

            camp_where = ((comilla + columna_where + comilla) if columna_where else columnas[-1]).lower()
            columnas_update.remove(camp_where + '=' + "%s")

            query = ("SELECT * FROM " + db.name + " WHERE " + camp_where + " = %s")

            cursor.execute(query, (record['' + str(camp_where).replace('`', '') + '']))
            data = cursor.fetchone()
            if data:
                q = "UPDATE %s SET %s WHERE %s=%s;" % (nombre, ",".join(columnas_update), camp_where, "'"+str(record[camp_where.replace('`', '')])+"'")
                # print(q)
                del record[camp_where.replace('`', '')]
                cursor.execute(q, tuple(record.values()))

                # record.pop("hello")
            else:
                q = "INSERT INTO %s (%s) VALUES(%s);" % (nombre, ",\n".join(columnas), ",\n".join(params))
                cursor.execute(q, tuple(record.values()))
            print(q, tuple(record.values()))
            print("------------")
            # emp_no = cursor.lastrowid  # ultimo id insertado
            # Indica a BD que guarde los cambios en la transacción actual
        conex.commit()
        cursor.close()
        conex.close()

    def dbftomysql(self, ruta_carpeta=None):
        # 'D:\\archivos_dbf'
        # Conexion con el dbf.
        if ruta_carpeta:
            for folder, subfolders, files in os.walk(ruta_carpeta):
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
                                query_create_table = self.sql_create_table(table)
                                # Establecer una conexion a mysql y ejecutar el script
                                self.run_query(query_create_table)
                                # insertar datos a la tabla, pasar el dato por el cual quieres filtrar para hacer el update
                                self.sql_insert_into(table, self.CAMPO_WHERE)
                                # print(query_insert)
                                stories_zip.close()
                                os.remove(str(info.filename))
            print('¡Proceso Finalizado...!')
        else:
            'Ingrese la ruta donde estan los archivos gracias'


DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASS = ''
DB_NAME = 'employees'
ruta = 'D:\\archivos_dbf'

# def create_db(db_name=''):
#     datos = [DB_HOST, DB_USER, DB_PASS]
#     try:
#         db1 = pymysql.connect(*datos)
#     except (pymysql.err.OperationalError, pymysql.ProgrammingError, pymysql.InternalError, pymysql.IntegrityError,
#             TypeError) as message:
#         raise Warning("Mysql Error %d:\n%s" % (message[0], message[1]))
#
#     cursor = db1.cursor()
#     db_existe = 'SHOW DATABASES LIKE "' + db_name + '";'
#     resp = cursor.execute(db_existe)
#     if resp:
#         """EXISTE LA BD"""
#         return resp
#     else:
#         """NO EXISTE LA BD"""
#         query = 'CREATE DATABASE IF NOT EXISTS ' + db_name + ' CHARACTER SET utf8;'
#         # print(query)
#         res = cursor.execute(query)
#         return res

# crear base de datos
# create_db('employees')

# 'D:\\archivos_dbf'
tomysql = PasarDbfToMysql(DB_HOST, DB_USER, DB_PASS, DB_NAME)
tomysql.dbftomysql(ruta)

