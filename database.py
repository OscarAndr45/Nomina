from flask import Flask
import mariadb

def get_connection():
    """Establece la conexión con la base de datos MariaDB."""
    try:
        conn = mariadb.connect(
            host='127.0.0.1',  # Dirección del servidor (localhost en este caso)
            port=3306,          # Puerto de MariaDB (3306 es el predeterminado)
            user='root',        # Usuario de la base de datos
            password='9007',  # Contraseña del usuario
            database='nominas'  # Nombre de la base de datos
        )
        return conn
    except mariadb.Error as e:
        print(f"Error al conectar con la base de datos: {e}")
        return None