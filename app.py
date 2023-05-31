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
                return render_template('index.html', alert_info=f"Estudio siendo digitado, Desbloqueado. OS: '{numero}'")
            elif(emandamento == 'T'):
                cur.execute(f"UPDATE medisystem.exames SET estado = '1', emandamento = 'F', data_emandamento = '', login_emandamento = '' WHERE numero = '{numero}';")
                conn.commit()
                writeLogs(f"Estudio en proceso (Andamento), Desbloqueado. OS: '{numero}'")
                return render_template('index.html',  alert_info=f"Estudio en proceso (Andamento), Desbloqueado. OS: '{numero}'")
                
    return render_template('index.html', alert_info=f"OS: '{numero}' no se encuentra bloqueado o no existe en la BD.")


@app.route('/modalidad',methods=['POST'])
def modalidad():
    os = request.form['os']
    mod_new = request.form.getlist('modalidad')[0]
    print(f"UPDATE medisystem.exames SET modalidade='{mod_new}' WHERE numero = '{os}';")
    try:
        cur.execute(f"UPDATE medisystem.exames SET modalidade = '{mod_new}' WHERE numero = '{os}';")
        conn.commit()
        writeLogs(f"Modalidad de Estudio Actualizada. OS: '{os}' Nueva Modalidad: '{mod_new}'")
        return render_template('index.html', alert_info=f"Modalidad de Estudio Actualizada. OS: '{os}' Nueva Modalidad: '{mod_new}'")
    except Exception as e:
        conn.rollback()
        print(f"Error al ejecutar la consulta SQL: {e}")
    return render_template('index.html', alert_info=f"OS: '{os}' no existe en la BD.")
    

if __name__ == '__main__':
    app.run(debug=True)
    


