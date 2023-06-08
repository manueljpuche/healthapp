import psycopg2
import os
from striprtf.striprtf import rtf_to_text
from datetime import datetime
from flask import Flask, render_template, request,redirect
from flask_cors import CORS
from functions import *
import socket

app = Flask(__name__,static_folder='static')

app.secret_key = os.urandom(24)

CORS(app)

# Configuración de la conexión a la base de datos
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_HOSTS = os.environ.get("DB_HOSTS").split(",") 
DB_PORT = os.environ.get("DB_PORT")

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
        



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/desbloqueo', methods=['POST'])
def desbloqueo():
    cur = conn.cursor()
    os = request.form['os']
    try:
        cur.execute(f"SELECT numero, nome, patientid, tipo_exame, sendodigitado, estado, emandamento, data_emandamento, login_emandamento, logindigitando, finalizado,hora_laudo,login_laudo FROM medisystem.exames WHERE numero = '{os}';")
        
    except Exception as e:
        conn.rollback()
        cur.close()
        conn.close()
        print(f"Error al ejecutar la consulta SQL: {e}")
        data = {'valid': False}  
        
    result = cur.fetchone()
    if result:
        numero, nome, patientid, tipo_exame, sendodigitado, estado, emandamento, data_emandamento, login_emandamento, logindigitando, finalizado, hora_laudo, login_laudo = result
        if(finalizado == 'T'):
            writeLogs(f"Estudio se encuentra finalizado. OS: '{numero}'")
        else:
            if(sendodigitado == 'T'):
                cur.execute(f"UPDATE medisystem.exames SET estado = '1', sendodigitado = 'F', logindigitando = '' WHERE numero = '{numero}';")
                conn.commit()
                writeLogs(f"Estudio siendo digitado, Desbloqueado. OS: '{numero}'")
                cur.close()
                conn.close()
                return redirect('/')
                #return render_template('index.html', alert_info=f"Estudio siendo digitado, Desbloqueado. OS: '{numero}'")
            elif(emandamento == 'T'):
                cur.execute(f"UPDATE medisystem.exames SET emandamento = 'F', data_emandamento = NULL, login_emandamento = '', hora_laudo = NULL, login_laudo = '' WHERE numero = '{numero}';")
                conn.commit()
                cur.execute(f"UPDATE medisystem.exames SET estado = '1' WHERE numero = '{numero}';")
                conn.commit()
                cur.close()
                conn.close()
                writeLogs(f"Estudio en proceso (Andamento), Desbloqueado. OS: '{numero}'")
                return redirect('/')
                #return render_template('index.html',  alert_info=f"Estudio en proceso (Andamento), Desbloqueado. OS: '{numero}'")
    
    return redirect('/')            
    #return render_template('index.html', alert_info=f"OS: '{numero}' no se encuentra bloqueado o no existe en la BD.")

@app.route('/modalidad',methods=['POST'])
def modalidad():
    cur = conn.cursor()
    os = request.form['os']
    mod_new = request.form.getlist('modalidad')[0]
    print(f"UPDATE medisystem.exames SET modalidade='{mod_new}' WHERE numero = '{os}';")
    try:
        cur.execute(f"UPDATE medisystem.exames SET modalidade = '{mod_new}' WHERE numero = '{os}';")
        conn.commit()
        cur.close()
        conn.close()
        writeLogs(f"Modalidad de Estudio Actualizada. OS: '{os}' Nueva Modalidad: '{mod_new}'")
        return redirect('/')
        #return render_template('index.html', alert_info=f"Modalidad de Estudio Actualizada. OS: '{os}' Nueva Modalidad: '{mod_new}'")
    except Exception as e:
        conn.rollback()
        cur.close()
        conn.close()
        print(f"Error al ejecutar la consulta SQL: {e}")
    
    return redirect('/')
    #return render_template('index.html', alert_info=f"OS: '{os}' no existe en la BD.")

@app.route('/web', methods=['POST'])
def web():
    cur = conn.cursor()
    id_patient = request.form['id_patient']
    try:
        cur.execute(f"SELECT id_pac, nm_pac, senha_pac,cpf_pac FROM mediweb.paciente where cpf_pac = '{id_patient}'")
    except:
        conn.rollback()
        cur.close()
        conn.close()
        print(f"Error al ejecutar la consulta SQL: {e}")
        
    result = cur.fetchall()
    
    if len(result) == 0:      
        try:
            cur.execute(f"SELECT id_pac, nm_pac, senha_pac,cpf_pac FROM mediweb.paciente where cpf_pac = '{id_patient} '")
        except Exception as e:
            conn.rollback()
            cur.close()
            conn.close()
            print(f"Error al ejecutar la consulta SQL: {e}")   
        
        paciente_ = cur.fetchall()
        
        if len(paciente_) != 0:
            for pac in paciente_:
                try:
                    writeLogs(f"UPDATE mediweb.paciente SET cpf_pac = '{id_patient}' WHERE id_pac = '{pac[0]}';")
                    cur.execute(f"UPDATE mediweb.paciente SET cpf_pac = '{id_patient}' WHERE id_pac = '{pac[0]}';")
                    conn.commit()
                    cur.close()
                    conn.close()
                    return redirect('/')
                    #return render_template('index.html')
                except Exception as e:
                    conn.rollback()
                    cur.close()
                    conn.close()
                    print(f"Error al ejecutar la consulta SQL: {e}")
        else:
        
            try:
                cur.execute(f"SELECT id_pac,nm_pac,cpf_pac,senhaweb FROM mediclinic.pacientes WHERE cpf_pac = '{id_patient}'")
            except Exception as e:
                conn.rollback()
                cur.close()
                conn.close()
                print(f"Error al ejecutar la consulta SQL: {e}")
            
            paciente = cur.fetchone()
            if len(paciente) > 1:
                render_template('index.html',alert_message="Paciente duplicado, primero asocia los registros en mediclinic y luego intenta nuevamente")
                
                
            if len(paciente) > 0:
                try:
                    cur.execute(f"SELECT * FROM mediclinic.laudos_finais WHERE patientid = '{paciente[0]}'")
                except Exception as e:
                    conn.rollback()
                    cur.close()
                    conn.close()
                    print(f"Error al ejecutar la consulta SQL: {e}")
                    
                informes = cur.fetchone()
                
                if len(informes) == 0:
                    print("Paciente no tiene informes finalizados")
                else:
                    try:
                        writeLogs(f"INSERT INTO mediweb.paciente (id_pac,nm_pac,senha_pac,cpf_pac) VALUES ('{paciente[0]}', '{paciente[1]}', '{paciente[3]}','{paciente[2]}');")
                        cur.execute(f"INSERT INTO mediweb.paciente (id_pac,nm_pac,senha_pac,cpf_pac) VALUES ('{paciente[0]}', '{paciente[1]}', '{paciente[3]}','{paciente[2]}');")
                        conn.commit()
                        cur.close()
                        conn.close()
                        alert_message = f"Registro de Usuario insertado a la base de Datos de MediWeb\nNombre: {paciente[1]}\nID: {paciente[0]}\nContraseña: {paciente[2]}"
                        return redirect('/')
                        #return render_template('index.html', alert_message=alert_message)
                    except Exception as e:
                        conn.rollback()
                        cur.close()
                        conn.close()
                        print(f"Error al ejecutar la consulta SQL: {e}")
            else:
                print("Paciente no registra en la BD")
        
    return redirect('/')   
    #return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
    


#216553