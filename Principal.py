from flask import Flask, render_template, request, jsonify
from database import get_connection
import os
app = Flask(__name__)

@app.route('/')
def index():
    """Página principal: formulario para registrar datos."""
    conn = get_connection()
    cursor = conn.cursor()

    # Obtener los colegios
    cursor.execute("SELECT id, nombre FROM colegios")
    colegios = cursor.fetchall()

    conn.close()
    return render_template('form.html', colegios=colegios)

@app.route('/prendas/<int:colegio_id>')
def obtener_prendas(colegio_id):
    """Obtener prendas según el colegio seleccionado."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, nombre FROM prendas WHERE colegio_id = %s", (colegio_id,))
    prendas = cursor.fetchall()

    conn.close()
    return jsonify(prendas)

@app.route('/operaciones/<int:prenda_id>')
def obtener_operaciones(prenda_id):
    """Obtener operaciones según la prenda seleccionada."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, nombre, costo FROM operaciones WHERE prenda_id = %s", (prenda_id,))
    operaciones = cursor.fetchall()

    conn.close()
    return jsonify(operaciones)

@app.route('/guardar', methods=['POST'])
def guardar():
    """Guardar el registro en la base de datos."""
    fecha = request.form['fecha']
    hora = request.form['hora']
    colegio_id = request.form['colegio']
    prenda_id = request.form['prenda']
    operacion_id = request.form['operacion']
    cantidad = int(request.form['cantidad'])
    operario = request.form['operario']

    # Obtener el costo de la operación
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT costo FROM operaciones WHERE id = %s", (operacion_id,))
    costo = cursor.fetchone()[0]

    # Calcular el total
    total = cantidad * costo

    # Insertar el registro
    cursor.execute('''
        INSERT INTO registro (fecha, hora, colegio_id, prenda_id, operacion_id, cantidad, total, operario)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    ''', (fecha, hora, colegio_id, prenda_id, operacion_id, cantidad, total, operario))
    conn.commit()
    conn.close()

    return render_template('success.html', operario=operario, total=total)

if __name__ == "__main__":
    app.run(debug=True,)
