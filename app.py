#librerías para renderizar los templates
#Para montar el servidor
from flask import Flask
from flask import render_template, request, redirect, url_for
from flaskext.mysql import MySQL
from datetime import datetime
from flask import send_from_directory
import os

app = Flask(__name__)
mysql = MySQL()

app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'crudpython'
#app.config['MYSQL_DATABASE_PORT'] = 3306

mysql.init_app(app)
CARPETA = os.path.join('uploads')
app.config['CARPETA'] = CARPETA

@app.route('/uploads/<nombre>')
def uploads(nombre):
    return send_from_directory(app.config['CARPETA'], nombre)

#indicar ruta por default
@app.route('/')
def index():
    sql = "SELECT * FROM `empleados`"
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql)
    empleados = cursor.fetchall()
    conn.commit()

    return render_template('empleados/index.html', data=empleados)

@app.route('/create')
def create():
    return render_template('empleados/create.html')

@app.route('/store', methods=['POST'])
def storage():
    _nombre = request.form['txtNombre']
    _correo = request.form['txtCorreo']
    _foto = request.files['txtFoto']

    now = datetime.now()
    fecha = now.strftime("%Y%H%M%S")

    if (_foto.filename != ''):
        nuevoFoto = fecha + _foto.filename
        _foto.save("uploads/"+nuevoFoto)

    sql = "Insert Into `empleados` (`nombre`,`correo`,`foto`) values(%s,%s,%s);"
    datos = (_nombre, _correo, nuevoFoto)
    conn = mysql.connect() #Conexión con base de datos
    cursor = conn.cursor() #Definir el cursor
    cursor.execute(sql, datos) #Mandar query y datos a sustituir
    conn.commit() #Redireccionar al index
    return redirect('/')

@app.route('/destroy/<int:id>')
def destroy(id):
    conn = mysql.connect()
    cursor = conn.cursor()

    cursor.execute("Select Foto from empleados Where id=%s", (id))

    datoFoto = cursor.fetchall()
    os.remove(os.path.join(app.config['CARPETA'], datoFoto[0][0]))

    cursor.execute("Delete From empleados Where id=%s", (id))

    conn. commit()
    return redirect('/')

@app.route('/edit/<int:id>')
def edit(id):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("Select * From empleados Where id=%s", (id))
    empleado = cursor.fetchall()
    conn.commit()
    return render_template('empleados/edit.html', empleado=empleado)

@app.route('/update', methods=['POST'])
def update():
    _nombre = request.form['txtNombre']
    _correo = request.form['txtCorreo']
    _foto = request.files['txtFoto']
    id = request.form['txtId']

    conn = mysql.connect()
    cursor = conn.cursor()

    sql = "Update empleados set nombre=%s, correo=%s WHERE id=%s;"
    datos = (_nombre, _correo, id)

    cursor.execute(sql, datos)
    conn.commit()

    now = datetime.now()
    tiempo = now.strftime("%Y%H%M%S")

    if _foto.filename != '':
        nuevoNombre = tiempo + _foto.filename
        _foto.save("uploads/"+nuevoNombre)
        cursor.execute("Select foto from empleados Where id=%s", id)
        datoFoto = cursor.fetchall()
        os.remove(os.path.join(app.config['CARPETA'], datoFoto[0][0]))
        cursor.execute("Update empleados set foto=%s where id=%s", (nuevoNombre, id))
        conn.commit()

    return redirect('/')

if __name__ == '__main__':
    app.run(debug = True)
