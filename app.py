import os
import bcrypt
import json
from flask import Flask
from flask import render_template , request, redirect, session
from flask_session import Session
from flaskext.mysql import MySQL
from datetime import datetime
from flask import send_from_directory
from time import strftime, gmtime
from flask_weasyprint import HTML, render_pdf

app=Flask(__name__)
app.secret_key="develoteca"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.config['MYSQL_DATABASE_HOST']='localhost' #aqui va el dominio de la pagina web 
app.config['MYSQL_DATABASE_USER']='admin@outlook.com'
app.config['MYSQL_DATABASE_PASSWORD']=']cJe1)D]/Fzf@YCb'
app.config['MYSQL_DATABASE_DB']='CECATI'
mysql=MySQL()
mysql.init_app(app)

@app.route('/')
def inicio():
    return render_template('sitio/index.html')

@app.route('/img/<imagen>')
def imagenes(imagen):
    print(imagen)
    return send_from_directory(os.path.join('templates/sitio/img'),imagen)

@app.route("/css/<archivocss>")
def css_link(archivocss):
    return send_from_directory(os.path.join('templates/sitio/css'),archivocss)

@app.route('/Estilismo y Diseño De Imagen')
def EstilismoyDiseñoDeImagen():
    return render_template('sitio/Estilismo y Diseño De Imagen.html')

@app.route('/Informatica')
def Informatica():
    return render_template('sitio/Informatica.html')

@app.route('/SOPORTE A INSTALACIONES ELECTRICAS Y MOTORES ELECTRICOS')
def SOPORTEAINSTALACIONESELECTRICASYMOTORESELECTRICOS():
    return render_template('sitio/SOPORTE A INSTALACIONES ELECTRICAS Y MOTORES ELECTRICOS.html')

@app.route('/USO DE LA LENGUA INGLESA EN DIVERSOS CONTEXTOS')
def USODELALENGUAINGLESAENDIVERSOSCONTEXTOS():
    return render_template('sitio/USO DE LA LENGUA INGLESA EN DIVERSOS CONTEXTOS.html')

@app.route('/Mantenimiento Electro Mecánico Del Automóvil')
def MantenimientoElectroMecánicoDelAutomóvil():
    return render_template('sitio/Mantenimiento Electro Mecánico Del Automóvil.html')

@app.route('/CAED')
def CAED():
    return render_template('sitio/CAED.html')

@app.route('/nosotros')
def nosotros():
    datos = json.load(open('personal.json'))
    per = ""
    for i in datos:
        per += render_template('personal.html', datos = i)
    return render_template('sitio/nosotros.html', personal = per)
@app.route('/requisitos')
def requisitos():
    return render_template('sitio/requisitos.html')

@app.route('/Cursos')
def Cursos():
    return render_template('sitio/Cursos.html')

@app.route('/Eventos')
def Eventos():
    datos = json.load(open('eventos.json'))
    ev = ""
    for i in datos:
        ev += render_template('evento.html', datos = i)
    return render_template('sitio/Eventos.html', eventos=ev)

@app.route('/sistema/')
def admin_index():
    if not 'login' in session:
        return redirect("/admin/login")
    return render_template('admin/index.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if session.get('id'):
        return redirect('/estudiante')
    if session.get('usuario') == 'Administrador':
        return redirect('/admin')
    if request.method == 'GET':
        return render_template('/sistema/login.html')
    _usuario=request.form['email']
    _password=request.form['pass']
    print (_usuario)
    print (_password)
    if _usuario=="admin@admin" and _password=="1234":
        session["login"]=True
        session["usuario"]="Administrador"
        return redirect("/admin")
    else:
        query="SELECT id, password, nombre, pr_apellido, se_apellido FROM Estudiantes WHERE email=%s"
        db = mysql.get_db()
        cursor = db.cursor()
        cursor.execute(query, (_usuario))
        data = cursor.fetchone()
        db.close()
        if data !=  None:
            if bcrypt.checkpw(_password.encode('utf-8'), data[1].encode('utf-8')):
                session['usuario'] = data[2] + " " + data[3] + " " + data[4]
                session['id'] = data[0]
                return redirect('/estudiante')
    return render_template('/sistema/login.html')

@app.route('/cerrar')
def admin_login_cerrar():
    session.clear()
    return redirect('/login')

@app.route('/registrar', methods= ['POST', 'GET'])
def registrar():
    if request.method == 'GET':
        return render_template('sistema/registrar.html')
    d = request.form
    db = mysql.get_db()
    cursor = db.cursor()
    query = """
    INSERT INTO Estudiantes(
            curp,
            password,
            fecha_n,
            nombre,
            pr_apellido,
            se_apellido,
            telefono, 
            tel_movil,
            email,
            cod_post,
            calle,
            num_ext,
            num_int,
            colonia,
            estado,
            municipio,
            est_civil,
            discapacidad,
            nom_empresa,
            cod_post_emp,
            calle_emp,
            num_ext_emp,
            num_int_emp,
            col_emp,
            mun_emp,
            est_emp,
            tel_emp,
            ext_tel_emp
            )
    VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    dat = (
            d['curp'],
            bcrypt.hashpw(d['password'].encode('utf-8'), bcrypt.gensalt()),
            d['fecha_n'],
            d['nombre'],
            d['pr_apellido'],
            d['se_apellido'],
            d['telefono'],
            d['tel_movil'],
            d['email'],
            d['cod_post'],
            d['calle'],
            d['num_ext'],
            d['num_int'],
            d['colonia'],
            d['estado'],
            d['municipio'],
            d['est_civil'],
            d['discapacidad'],
            d['nom_empresa'],
            None if not d['cod_post_emp'].isnumeric() else int(d['cod_post_emp']),
            d['calle_emp'],
            None if not d['num_ext_emp'].isnumeric() else int(d['num_ext_emp']),
            None if not d['num_int_emp'].isnumeric() else int(d['num_int_emp']),
            d['col_emp'],
            d['mun_emp'],
            d['est_emp'],
            d['tel_emp'],
            d['ext_tel_emp'])
    cursor.execute(query, dat)
    db.commit()
    session['id'] = cursor.lastrowid
    return redirect("/estudiante")

@app.route('/estudiante')
def estudiante():
    
    db = mysql.get_db()
    cursor = db.cursor()
    query = """SELECT
    nombre
    FROM Estudiantes WHERE id=%s"""
    cursor.execute(query, (session.get('id')))
    data=cursor.fetchone()
    d = {
       "nombre" : data[0],
    }
    cursor.execute('SELECT * FROM Especialidades')
    especialidades = cursor.fetchall()
    cursor.execute('SELECT nombre FROM Inscripciones LEFT JOIN Cursos on curso=Cursos.id WHERE estudiante=%s', (session['id']))
    inscripciones = cursor.fetchall()
    return render_template("sistema/estudiante.html", data=d, especialidades = especialidades, insc = inscripciones)

@app.route('/estudiante/especialidad', methods=['GET'])
def estudiante_especialidad():
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM Cursos WHERE especialidad=%s', (request.args.get('id')))
    return render_template('estudiante_especialidad.html', cursos = cursor.fetchall())

@app.route('/inscribir', methods = ['GET'])
def inscribir():
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT nombre FROM Cursos WHERE id=%s', (request.args.get('id')))
    return render_template('inscribir.html', curso = cursor.fetchone()[0], id = request.args.get('id'))

@app.route('/confirmar_inscripcion', methods = ['GET'])
def confirmar():
    cursor = mysql.get_db().cursor()
    try:
        cursor.execute('INSERT INTO Inscripciones(estudiante, curso) VALUES(%s, %s)', (session['id'], request.args.get('id')))
        mysql.get_db().commit()
    finally:
        return redirect('/estudiante')
    

@app.route('/estudiante/set_empleo', methods=['POST'])
def set_empleo():
    query = """
    UPDATE Estudiantes set 
    nom_empresa=%s,
    cod_post_emp=%s,
    calle_emp=%s,
    num_ext_emp=%s,
    num_int_emp=%s,
    col_emp=%s,
    mun_emp=%s,
    est_emp=%s,
    tel_emp=%s,
    ext_tel_emp=%s
    WHERE id=%s
    """
    d = request.form
    data = (
        d['nombre'],
        d['cod_post'],
        d['calle'],
        d['num_ext'],
        d['num_int'],
        d['colonia'],
        d['municipio'],
        d['estado'],
        d['telefono'],
        d['extension'],
        session['id']
    )
    db = mysql.get_db()
    cursor = db.cursor()
    cursor.execute(query, data)
    db.commit()
    return redirect('/estudiante')

@app.route('/rec_pass')
def rec_pass():
    return render_template("rec_pass.html")

@app.route('/admin')
def admin():
    cursor = mysql.get_db().cursor()
    cursor.execute("SELECT * FROM Especialidades")
    return render_template("admin.html", especialidades = cursor.fetchall())

@app.route('/especialidad', methods = ['GET'])
def especialidad():
    db = mysql.get_db()
    cursor = mysql.get_db().cursor()
    cursor.execute("SELECT * FROM Especialidades WHERE id=%s", (request.args.get('id')))
    dat = cursor.fetchone()
    nombre = dat[1]
    id = dat[0]
    cursor.execute("SELECT * FROM Cursos WHERE especialidad=%s", (request.args.get('id')))
    return render_template('especialidad.html', nombre = nombre, id = id, cursos = cursor.fetchall())

@app.route('/reg_especialidad', methods=['POST'])
def reg_especialidad():
    if session["usuario"] == "Administrador":
        db = mysql.get_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO Especialidades(nombre) VALUES(%s)", (request.form['nombre']))
        db.commit()
    return redirect('/admin')

@app.route('/reg_curso', methods=['POST'])
def reg_curso():
    if session["usuario"] == "Administrador":
        db = mysql.get_db()
        cursor = db.cursor()
        f = request.form
        days = (
                '0' if 'lunes' in f else '',
                '1' if 'martes' in f else '',
                '2' if 'miercoles' in f else '',
                '3' if 'jueves' in f else '',
                '4' if 'viernes' in f else '',
                '5' if 'sabado' in f else '',
                '6' if 'domingo' in f else '',
            )
        print(''.join(days))
        cursor.execute("INSERT INTO Cursos(nombre, especialidad, dias, hora_inicio, hora_fin) VALUES(%s, %s, %s, %s, %s)", (request.form['nombre'], request.form['id'], ''.join(days), f['hora_inicio'], f['hora_fin']))
        db.commit()
    return redirect('/especialidad?id=' + request.form['id'])
    
@app.route('/estudiante/horario', methods=['GET'])
def horario():
    db = mysql.get_db()
    cursor = db.cursor()
    cursor.execute('SELECT nombre, dias, hora_inicio, hora_fin FROM Inscripciones as i INNER JOIN Cursos as c ON i.curso = c.id WHERE estudiante = %s', session['id'])
    cursos = cursor.fetchall()
    cursos_data = []
    dias = ('Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes', 'Sabado', 'Domingo')
    for i in cursos:
        c = [i[0]]
        d = []
        if i[1]:
            for a in i[1]:
                d.append(dias[int(a)])
        c.append(d)
        if i[2]:
            c.append(strftime("%H:%M",gmtime(i[2].seconds)))
        if i[3]:
            c.append(strftime("%H:%M",gmtime(i[3].seconds)))
        cursos_data.append(c)
    html = render_template("horario.html", nombre = session.get('usuario'),cursos = cursos_data)
    return render_pdf(HTML(string=html))

if __name__ == '__main__':
    app.run(debug=True)
