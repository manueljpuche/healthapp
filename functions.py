import datetime
import psycopg2
import socket

def writeLogs(text :str):
    with open("log.txt","a",encoding="UTF-8") as log:
        log.writelines(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]: {text}\n")
                

# Función para establecer la conexión a la base de datos
def establish_connection(db_name, db_user, db_password, db_hosts, db_port):
    conn = None

    for host in db_hosts:
        try:
            conn = psycopg2.connect(
                dbname=db_name,
                user=db_user,
                password=db_password,
                host=host,
                port=db_port
            )
            break  # Si se conecta, salir del ciclo
        except psycopg2.OperationalError as e:
            print(f"No se pudo conectar a la base de datos en {host}: {e}")
        finally:
            write_logs(f"Conectado a la base de datos en {host} desde {socket.gethostbyname(socket.gethostname())}")

    return conn

def list_equals(texto_informe: str, palabras_clave: list, servicio: str, os: str, paciente :str, fecha: str):
            
    # Crear una lista para almacenar las palabras clave encontradas
    palabras_encontradas = []
    # Verificar si cada palabra clave se encuentra en el texto extraído
    for palabra in palabras_clave:
        if palabra.lower() in texto_informe.lower():
            # La palabra clave fue encontrada en el informe
            palabras_encontradas.append(palabra)
            if sorted(palabras_clave) == sorted(palabras_encontradas):
                #Escribir datos en un archivo
                with open("Buscador\\Lista.txt","a",encoding="utf-8") as lista:
                    lista.writelines(f"Estudio: {servicio}\nOS: {os}\nPaciente: {paciente}\nFecha: {fecha}\nPalabras: {palabras_encontradas}\n-----------\n\n") # Verificar si cada palabra clave se encuentra en el texto extraído
        for palabra in palabras_clave:
            if palabra.lower() in texto_informe.lower():
                # La palabra clave fue encontrada en el informe
                palabras_encontradas.append(palabra)
                if sorted(palabras_clave) == sorted(palabras_encontradas):
                    #Escribir datos en un archivo
                    with open("Buscador\\Lista.txt","a",encoding="utf-8") as lista:
                        lista.writelines(f"Estudio: {servicio}\nOS: {os}\nPaciente: {paciente}\nFecha: {fecha}\nPalabras: {palabras_encontradas}\n-----------\n\n") 
                

def list_not_equals(texto_informe: str, palabras_clave: list, servicio: str, os: str, paciente :str, fecha: str):
   
    # Crear una lista para almacenar las palabras clave encontradas
    palabras_encontradas = []

    # Verificar si cada palabra clave se encuentra en el texto extraído
    for palabra in palabras_clave:
        if palabra.lower() in texto_informe.lower():
            # La palabra clave fue encontrada en el informe
            palabras_encontradas.append(palabra)
                #Escribir datos en un archivo
            with open("Buscador\\Lista.txt","a",encoding="utf-8") as lista:
                lista.writelines(f"Estudio: {servicio}\nOS: {os}\nPaciente: {paciente}\nFecha: {fecha}\nPalabras: {palabras_encontradas}\n-----------\n\n")
            


            