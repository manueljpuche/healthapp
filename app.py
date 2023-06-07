import psycopg2
import os
<<<<<<< HEAD
=======
from striprtf.striprtf import rtf_to_text
from datetime import datetime
from flask import Flask, render_template, request
from flask_cors import CORS
from functions import *
>>>>>>> af99a3f (Alerts)
import socket
from flask import Flask, render_template, request, redirect
from flask_cors import CORS

<<<<<<< HEAD
from functions import writeLogs, establish_connection

app = Flask(__name__, static_folder='static')
app.secret_key = os.urandom(24)
=======
app = Flask(__name__,static_folder='static')

app.secret_key = os.urandom(24)

>>>>>>> af99a3f (Alerts)
CORS(app)

# Configuración de la conexión a la base de datos
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_HOSTS = os.environ.get("DB_HOSTS").split(",")
DB_PORT = os.environ.get("DB_PORT")

<<<<<<< HEAD
conn = establish_connection(DB_NAME,DB_USER,DB_PASSWORD,DB_HOSTS,DB_PORT)
# Ruta principal
=======
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

>>>>>>> af99a3f (Alerts)
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para desbloquear un estudio
@app.route('/desbloqueo', methods=['POST'])
def desbloqueo():
    os = request.form['os']
    cur = conn.cursor()

    try:
        cur.execute(f"SELECT numero, nome, patientid, tipo_exame, sendodigitado, estado, emandamento, data_emandamento, login_emandamento, logindigitando, finalizado,hora_laudo,login_laudo FROM medisystem.exames WHERE numero = '{os}';")
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
                    return redirect('/')
                elif(emandamento == 'T'):
                    cur.execute(f"UPDATE medisystem.exames SET emandamento = 'F', data_emandamento = NULL, login_emandamento = '', hora_laudo = NULL, login_laudo = '' WHERE numero = '{numero}';")
                    conn.commit()
                    cur.execute(f"UPDATE medisystem.exames SET estado = '1' WHERE numero = '{numero}';")
                    conn.commit()
                    writeLogs(f"Estudio en proceso (Andamento), Desbloqueado. OS: '{numero}'")
                    return redirect('/')
        else:
            writeLogs(f"OS: '{numero}' no se encuentra bloqueado o no existe en la BD.")
    except Exception as e:
        conn.rollback()
        print(f"Error al ejecutar la consulta SQL: {e}")
    finally:
        cur.close()

    return redirect('/')

# Ruta para actualizar la modalidad de un estudio
@app.route('/modalidad', methods=['POST'])
def modalidad():
    os = request.form['os']
    mod_new = request.form.getlist('modalidad')[0]
    cur = conn.cursor()

    try:
        cur.execute(f"UPDATE medisystem.exames SET modalidade = '{mod_new}' WHERE numero = '{os}';")
        conn.commit()
        writeLogs(f"Modalidad de Estudio Actualizada. OS: '{os}' Nueva Modalidad: '{mod_new}'")
    except Exception as e:
        conn.rollback()
        print(f"Error al ejecutar la consulta SQL: {e}")
    finally:
        cur.close()

    return redirect('/')

# Ruta para procesar la información de un paciente desde la web
@app.route('/web', methods=['POST'])
def web():
    id_patient = request.form['id_patient']
    cur = conn.cursor()

    try:
<<<<<<< HEAD
        cur.execute(f"SELECT id_pac, nm_pac, senha_pac, cpf_pac FROM mediweb.paciente WHERE cpf_pac = '{id_patient}'")
        result = cur.fetchall()

        if len(result) == 0:
            cur.execute(f"SELECT id_pac, nm_pac, senha_pac, cpf_pac FROM mediweb.paciente WHERE cpf_pac = '{id_patient} '")
            paciente_ = cur.fetchall()

            if len(paciente_) != 0:
                for pac in paciente_:
=======
        cur.execute(f"SELECT id_pac, nm_pac, senha_pac,cpf_pac FROM mediweb.paciente where cpf_pac = '{id_patient}'")
    except:
        conn.rollback()
        print(f"Error al ejecutar la consulta SQL: {e}")
        
    result = cur.fetchall()
    
    if len(result) == 0:      
        try:
            cur.execute(f"SELECT id_pac, nm_pac, senha_pac,cpf_pac FROM mediweb.paciente where cpf_pac = '{id_patient} '")
        except Exception as e:
            conn.rollback()
            print(f"Error al ejecutar la consulta SQL: {e}")   
        
        paciente_ = cur.fetchall()
        
        if len(paciente_) != 0:
            for pac in paciente_:
                try:
                    writeLogs(f"UPDATE mediweb.paciente SET cpf_pac = '{id_patient}' WHERE id_pac = '{pac[0]}';")
                    cur.execute(f"UPDATE mediweb.paciente SET cpf_pac = '{id_patient}' WHERE id_pac = '{pac[0]}';")
                    conn.commit()
                    return render_template('index.html')
                except Exception as e:
                    conn.rollback()
                    print(f"Error al ejecutar la consulta SQL: {e}")
        else:
        
            try:
                cur.execute(f"SELECT id_pac,nm_pac,cpf_pac,senhaweb FROM mediclinic.pacientes WHERE cpf_pac = '{id_patient}'")
            except Exception as e:
                conn.rollback()
                print(f"Error al ejecutar la consulta SQL: {e}")
            
            paciente = cur.fetchone()
            if len(paciente) > 1:
                render_template('index.html',alert_message="Paciente duplicado, primero asocia los registros en mediclinic y luego intenta nuevamente")
                
                
            if len(paciente) > 0:
                try:
                    cur.execute(f"SELECT * FROM mediclinic.laudos_finais WHERE patientid = '{paciente[0]}'")
                except Exception as e:
                    conn.rollback()
                    print(f"Error al ejecutar la consulta SQL: {e}")
                    
                informes = cur.fetchone()
                
                if len(informes) == 0:
                    print("Paciente no tiene informes finalizados")
                else:
>>>>>>> af99a3f (Alerts)
                    try:
                        writeLogs(f"UPDATE mediweb.paciente SET cpf_pac = '{id_patient}' WHERE id_pac = '{pac[0]}';")
                        cur.execute(f"UPDATE mediweb.paciente SET cpf_pac = '{id_patient}' WHERE id_pac = '{pac[0]}';")
                        conn.commit()
<<<<<<< HEAD
                        return redirect('/')
=======
                        alert_message = f"Registro de Usuario insertado a la base de Datos de MediWeb\nNombre: {paciente[1]}\nID: {paciente[0]}\nContraseña: {paciente[2]}"
                        return render_template('index.html', alert_message=alert_message)
>>>>>>> af99a3f (Alerts)
                    except Exception as e:
                        conn.rollback()
                        print(f"Error al ejecutar la consulta SQL: {e}")
            else:
                cur.execute(f"SELECT id_pac, nm_pac, cpf_pac, senhaweb FROM mediclinic.pacientes WHERE cpf_pac = '{id_patient}'")
                paciente = cur.fetchone()

                if paciente is not None:
                    cur.execute(f"SELECT * FROM mediclinic.laudos_finais WHERE patientid = '{paciente[0]}'")
                    informes = cur.fetchone()

                    if informes is not None:
                        try:
                            writeLogs(f"INSERT INTO mediweb.paciente (id_pac, nm_pac, senha_pac, cpf_pac) VALUES ('{paciente[0]}', '{paciente[1]}', '{paciente[3]}', '{paciente[2]}');")
                            cur.execute(f"INSERT INTO mediweb.paciente (id_pac, nm_pac, senha_pac, cpf_pac) VALUES ('{paciente[0]}', '{paciente[1]}', '{paciente[3]}', '{paciente[2]}');")
                            conn.commit()
                            alert_message = f"Registro de Usuario insertado a la base de Datos de MediWeb\nNombre: {paciente[1]}\nID: {paciente[0]}\nContraseña: {paciente[2]}"
                            return redirect('/')
                        except Exception as e:
                            conn.rollback()
                            print(f"Error al ejecutar la consulta SQL: {e}")
                    else:
                        print("Paciente no tiene informes finalizados")
                else:
                    print("Paciente no registra en la BD")
    except Exception as e:
        conn.rollback()
        print(f"Error al ejecutar la consulta SQL: {e}")
    finally:
        cur.close()

    return redirect('/')

if __name__ == '__main__':
<<<<<<< HEAD
    app.run(debug=True)
=======
    app.run(debug=True)
    


#216553
>>>>>>> af99a3f (Alerts)
