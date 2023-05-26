import psycopg2
import os
from striprtf.striprtf import rtf_to_text
from datetime import datetime
from flask import Flask, render_template, request, send_file
from flask_cors import CORS
from functions import *
from dotenv import load_dotenv
import socket

app = Flask(__name__,static_folder='static')
CORS(app)

load_dotenv()

# Configuración de la conexión a la base de datos
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOSTS = os.getenv("DB_HOSTS").split(",") 
DB_PORT = os.getenv("DB_PORT")

HOST_CONNECT = ""

for host in DB_HOSTS:
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=host,
            port=DB_PORT
        )
        break  # Si se conecta, salir del ciclo
    except psycopg2.OperationalError as e:
        print(f"No se pudo conectar a la base de datos en {host}: {e}")
    finally:
        writeLogs(f"Conectado a la base de datos en {host} desde {socket.gethostbyname(socket.gethostname())}")
        

cur = conn.cursor()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/desbloqueo', methods=['POST'])
def desbloqueo():
    os = request.form['os']
    log=""
    try:
        cur.execute(f"SELECT numero, nome, patientid, tipo_exame, sendodigitado, estado, emandamento, data_emandamento, login_emandamento, logindigitando, finalizado FROM medisystem.exames WHERE numero = '{os}';")
        
    except Exception as e:
        conn.rollback()
        print(f"Error al ejecutar la consulta SQL: {e}")
        data = {'valid': False}  
        
    result = cur.fetchone()
    if result:
        numero, nome, patientid, tipo_exame, sendodigitado, estado, emandamento, data_emandamento, login_emandamento, logindigitando, finalizado = result
        if(finalizado == 'T'):
            writeLogs(f"Estudio se encuentra finalizado. OS: '{numero}'")
        else:
            if(sendodigitado == 'T'):
                cur.execute(f"UPDATE medisystem.exames SET estado = '1', sendodigitado = 'F', logindigitando = '' WHERE numero = '{numero}';")
                conn.commit()
                writeLogs(f"Estudio siendo digitado, Desbloqueado. OS: '{numero}'")
                return render_template('index.html')
            elif(emandamento == 'T'):
                cur.execute(f"UPDATE medisystem.exames SET estado = '1', emandamento = 'F', data_emandamento = '', login_emandamento = '' WHERE numero = '{numero}';")
                conn.commit()
                writeLogs(f"Estudio en proceso (Andamento), Desbloqueado. OS: '{numero}'")
                return render_template('index.html')
                
    return render_template('index.html')


@app.route('/modalidad',methods=['POST'])
def modalidad():
    os = request.form['os']
    mod_new = request.form.getlist('modalidad')[0]
    print(f"UPDATE medisystem.exames SET modalidade='{mod_new}' WHERE numero = '{os}';")
    try:
        cur.execute(f"UPDATE medisystem.exames SET modalidade = '{mod_new}' WHERE numero = '{os}';")
        conn.commit()
        writeLogs(f"Modalidad de Estudio Actualizada. OS: '{os}' Nueva Modalidad: '{mod_new}'")
    except Exception as e:
        conn.rollback()
        print(f"Error al ejecutar la consulta SQL: {e}")
    return render_template('index.html')
    

@app.route('/resultados', methods=['POST'])
def resultados():
    
    palabras_clave_str = request.form['palabras_clave']
    fecha_inicio_str = request.form['fecha_inicio']
    fecha_fin_str = request.form['fecha_fin']
    check_palabras = request.form.getlist('check_palabras')
    modalidades_seleccionadas = request.form.getlist('modalidades')
    #medico = request.form['medico']
    
    if 'todas' in modalidades_seleccionadas:
        # No se necesita filtrar por modalidad en la consulta SQL
        sql_modalidades = ''
    else:
        modalidades_str = ','.join([f"'{modalidade}'" for modalidade in modalidades_seleccionadas])
        sql_modalidades = f"AND modalidade IN ({modalidades_str})"
        
    #if medico:
    #    sql_medico = f"AND medico = {medico}"
    #else:
    #    sql_medico = ''

    # Separar las palabras clave en una lista
    palabras_clave = palabras_clave_str.split(",")


    # Convertir las fechas a objetos datetime de Python
    fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d')
    fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d')

    # Realizar una consulta SQL para recuperar los datos del campo blob y el número de identificación de la tabla que contiene los informes
    cur.execute(f"SELECT num_exame, desc_lfinal, servico, nm_pac, data_exame FROM mediclinic.laudos_finais WHERE data_exame between '{fecha_inicio}' and '{fecha_fin}' {sql_modalidades}")
    
    with open("Buscador\\Lista.txt","w",encoding="utf-8"):
        # Iterar sobre los resultados de la consulta
        for result in cur.fetchall():
            texto_informe = ""
            contenido = bytes(result[1])
            txt = contenido.decode(encoding="ISO-8859-1")
            try:
                texto_informe = rtf_to_text(txt)
            except UnicodeEncodeError:
                with open("Buscador\\error_log","a",encoding="utf-8") as error:
                    error.writelines(f"Se produjo un error al codificar el texto del informe {result[0]}.\n\n")
            
            os = result[0]
            servicio = result[2]
            paciente = result[3]
            fecha = result[4]
            
            if check_palabras:
                list_equals(texto_informe, palabras_clave, servicio, os, paciente, fecha)
            else:
                list_not_equals(texto_informe, palabras_clave, servicio, os, paciente, fecha)                            
    return send_file("Lista.txt", as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
    


