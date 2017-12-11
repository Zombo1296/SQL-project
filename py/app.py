from flask import Flask, request, send_from_directory, Response, session
from flaskext.mysql import MySQL
from flask_session import Session
import hashlib
import json

app=Flask(__name__, static_url_path='')
app.config.from_object('config')
app.config.from_pyfile('config.py')
mysql = MySQL()
mysql.init_app(app)
Session(app)



@app.route('/')
def root():
    # return app.send_static_file('homepage.html')
    return app.send_static_file('homepage.html')


@app.route('/users/')
def users():
    conn = mysql.connect()
    cur = conn.cursor()
    cur.execute('''SELECT * FROM `Artist` WHERE aname = "Adele"''')
    rv = cur.fetchall()
    return str(rv)

@app.route('/me/')
def me():
    return app.send_static_file('me.html')


@app.route('/signup/')
def signup():
    return app.send_static_file('signup.html')

@app.route('/login/')
def login():
    return app.send_static_file('login.html')




@app.route('/api/addUser/', methods=['POST'])
def add_user():
    username = request.form.get('username')
    password = request.form.get("password")
    nickname = request.form.get("nickname")
    city = request.form.get("city")
    email = request.form.get("email")

    print(username)
    print(len(password))
    print(nickname)
    print(city)
    print(email)

    if(username == None or password == None or len(password) != 40 or nickname != None and len(nickname) > 45
       or city != None and len(city) > 45 or email != None and len(email) > 45):
        t = {'status': 'error', 'error': 'Invalid input'}
        return Response(json.dumps(t), mimetype='application/json')

    password = password + username
    m = hashlib.sha1()
    m.update(password.encode('utf-8'))
    password = m.hexdigest()

    conn = mysql.connect()
    cur = conn.cursor()
    cur.execute("SET SESSION TRANSACTION ISOLATION LEVEL SERIALIZABLE")
    cur.execute("START TRANSACTION")
    cur.execute('''SELECT uname FROM `User` WHERE uname = "User"''')
    rv = cur.fetchone()
    if rv == None:
        cur.execute(''' INSERT INTO User(uname, nickname, email, password, city) VALUES (%s, %s, %s, %s, %s)''' ,
                    (username, nickname, email, password, city))
        conn.commit()
        cur.close()
        conn.close()
        t = {'status': 'success'}
        return Response(json.dumps(t), mimetype='application/json')
    else:
        cur.close()
        conn.rollback()
        conn.close()
        t = {'status': 'success', 'error': 'Invalid input'}
        return Response(json.dumps(t), mimetype='application/json')


if __name__ == '__main__':
    app.run(port = 5000, debug = True)