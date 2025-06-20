from flask import Flask
import mysql.connector
import os

def get_connection():
    """Establece la conexión con la base de datos MySQL de InfinityFree."""
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "sql102.infinityfree.com"),        # Dirección del servidor
            port=int(os.getenv("DB_PORT", 3306)),                       # Puerto
            user=os.getenv("DB_USER", "if0_39276113"),                  # Usuario
            password=os.getenv("DB_PASSWORD", "59ABM0y8Nt9yK1i"),       # Contraseña
            database=os.getenv("DB_NAME", "if0_39276113_nominas")       # Nombre de la base de datos
        )
        return conn
    except mysql.connector.Error as e:
        print(f"Error al conectar con la base de datos: {e}")
        return None
