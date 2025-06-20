from flask import Flask, render_template, request,redirect, url_for, session, jsonify
from database import get_connection
import pandas as pd
from flask import send_file
import io
import os

app = Flask(__name__, template_folder='Templates', static_folder='statics')

app.secret_key = '123456789'

@app.route('/admin_panel')
def admin_panel():
    if not session.get('admin'):
        return redirect('/admin')
    return render_template('admin_panel.html')

@app.route('/admin', methods=['GET'])
def login_form():
    return render_template('admin_login.html')

@app.route('/login', methods=['POST'])
def login():
    usuario = request.form['usuario']
    clave = request.form['clave']

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM administradores WHERE usuario = %s AND clave = %s", (usuario, clave))
    admin = cursor.fetchone()
    conn.close()

    if admin:
        session['admin'] = True
        return redirect('/admin_panel')
    else:
        return "Credenciales inválidas"
    
@app.route('/')
def inicio():
    return render_template('inicio.html')

@app.route('/formulario')
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

@app.route('/admin/agregar-operacion', methods=['GET', 'POST'])
def agregar_operacion():
    if not session.get('admin'):
        return redirect(url_for('inicio'))

    if request.method == 'POST':
        nombre = request.form['nombre']
        costo = float(request.form['costo'])
        prenda_id = int(request.form['prenda_id'])

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO operaciones (nombre, costo, prenda_id) VALUES (%s, %s, %s)", (nombre, costo, prenda_id))
        conn.commit()
        conn.close()
        return render_template('sucesss.html', mensaje="La operación fue agregada correctamente.")

    # Obtener prendas para el formulario
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre FROM prendas")
    prendas = cursor.fetchall()
    conn.close()
    return render_template('admin/agregar_operacion.html', prendas=prendas)


@app.route('/admin/editar-operacion', methods=['GET', 'POST'])
def editar_operacion():
    if not session.get('admin'):
        return redirect(url_for('inicio'))

    conn = get_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        operacion_id = request.form['operacion_id']
        nuevo_nombre = request.form['nombre']
        nuevo_costo = float(request.form['costo'])

        cursor.execute("UPDATE operaciones SET nombre = %s, costo = %s WHERE id = %s", (nuevo_nombre, nuevo_costo, operacion_id))
        conn.commit()
        conn.close()
        return render_template('sucesss.html', mensaje="La operación fue actualizada correctamente.")
    
    cursor.execute("SELECT id, nombre, costo FROM operaciones")
    operaciones = cursor.fetchall()
    conn.close()
    return render_template('admin/editar_operacion.html', operaciones=operaciones)

@app.route('/admin/agregar-prenda', methods=['GET', 'POST'])
def agregar_prenda():
    if not session.get('admin'):
        return redirect(url_for('inicio'))

    if request.method == 'POST':
        nombre = request.form['nombre']
        colegio_id = int(request.form['colegio_id'])

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO prendas (nombre, colegio_id) VALUES (%s, %s)", (nombre, colegio_id))
        conn.commit()
        conn.close()
        return render_template('sucesss.html', mensaje="La Prenda fue agregada correctamente.")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre FROM colegios")
    colegios = cursor.fetchall()
    conn.close()
    return render_template('admin/agregar_prenda.html', colegios=colegios)


@app.route('/admin/editar-prenda', methods=['GET', 'POST'])
def editar_prenda():
    if not session.get('admin'):
        return redirect(url_for('inicio'))

    conn = get_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        prenda_id = request.form['prenda_id']
        nuevo_nombre = request.form['nombre']
        nuevo_colegio = request.form['colegio_id']

        cursor.execute("UPDATE prendas SET nombre = %s, colegio_id = %s WHERE id = %s", (nuevo_nombre, nuevo_colegio, prenda_id))
        conn.commit()
        conn.close()
        return render_template('sucesss.html', mensaje="La Prenda fue actualizada correctamente.")

    cursor.execute("SELECT id, nombre, colegio_id FROM prendas")
    prendas = cursor.fetchall()
    cursor.execute("SELECT id, nombre FROM colegios")
    colegios = cursor.fetchall()
    conn.close()
    return render_template('admin/editar_prenda.html', prendas=prendas, colegios=colegios)

@app.route('/admin/agregar-colegio', methods=['GET', 'POST'])
def agregar_colegio():
    if not session.get('admin'):
        return redirect(url_for('inicio'))

    if request.method == 'POST':
        nombre = request.form['nombre']

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO colegios (nombre) VALUES (%s)", (nombre,))
        conn.commit()
        conn.close()
        return render_template('sucesss.html', mensaje="El colegio fue agregado correctamente.")

    return render_template('admin/agregar_colegio.html')


@app.route('/admin/editar-colegio', methods=['GET', 'POST'])
def editar_colegio():
    if not session.get('admin'):
        return redirect(url_for('inicio'))

    conn = get_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        colegio_id = request.form['colegio_id']
        nuevo_nombre = request.form['nombre']

        cursor.execute("UPDATE colegios SET nombre = %s WHERE id = %s", (nuevo_nombre, colegio_id))
        conn.commit()
        conn.close()
        return render_template('sucesss.html', mensaje="El colegio fue actualizado correctamente.")

    cursor.execute("SELECT id, nombre FROM colegios")
    colegios = cursor.fetchall()
    conn.close()
    return render_template('admin/editar_colegio.html', colegios=colegios)


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

@app.route('/admin/generar-nomina', methods=['GET', 'POST'])
def generar_nomina():
    if not session.get('admin'):
        return redirect(url_for('inicio'))

    if request.method == 'POST':
        operario = request.form['operario']
        fecha_inicio = request.form['fecha_inicio']
        fecha_fin = request.form['fecha_fin']

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT r.fecha, o.nombre as operacion, o.costo as precio, p.nombre as prenda, c.nombre as colegio, r.cantidad, r.total
        FROM registro r
        JOIN operaciones o ON r.operacion_id = o.id
        JOIN prendas p ON r.prenda_id = p.id
        JOIN colegios c ON r.colegio_id = c.id
        WHERE r.operario = %s AND r.fecha BETWEEN %s AND %s
        ORDER BY r.fecha
    """, (operario, fecha_inicio, fecha_fin))
        rows = cursor.fetchall()
        conn.close()

        # Si no hay registros, muestra mensaje amigable
        if not rows:
            return render_template('admin/generar_nomina.html', mensaje="No hay registros para ese operario y rango de fechas.")

        # Crear DataFrame
        df = pd.DataFrame(rows, columns=['Fecha', 'Operación', 'Precio', 'Prenda', 'Colegio', 'Cantidad', 'Total'])

        # Calcula el total a pagar
        total_pagar = df['Total'].sum()

        # Crear archivo Excel en memoria
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Nómina')
            # Escribir total al final
            ws = writer.sheets['Nómina']
            ws.append(['', '', '', '', '', 'TOTAL', total_pagar])

        output.seek(0)
        filename = f"nomina_{operario}_{fecha_inicio}_a_{fecha_fin}.xlsx"

        return send_file(
            output,
            download_name=filename,
            as_attachment=True,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    return render_template('admin/generar_nomina.html')

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


