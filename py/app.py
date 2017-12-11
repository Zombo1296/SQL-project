from flask import Flask, request, send_from_directory, Response, session
from flask_mysqldb import MySQL
from flask_session import Session
import hashlib
import json

app=Flask(__name__, static_url_path='')
app.config.from_object('config')
app.config.from_pyfile('config.py')
mysql = MySQL(app)
Session(app)



@app.route('/')
def root():
    # return app.send_static_file('homepage.html')
    return app.send_static_file('homepage.html')


@app.route('/users/')
def users():
    cur = mysql.connection.cursor()
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

    mysql.connection.start_transaction(isolation_level='SERIALIZABLE')
    cur = mysql.connection.cursor()
    cur.execute('''SELECT uname FROM `User` WHERE uname = "User"''')
    rv = cur.fetchone()
    print(rv)
    mysql.connection.rollback()

    password = password + username

    m = hashlib.sha1()
    m.update(password.encode('utf-8'))
    password = m.hexdigest()
    print(len(password))


    print(username)
    print(password)
    print(nickname)
    print(city)
    print(email)

    t = {'status': 'success', 'error': 'Invalid input'}
    sess = session.get('username', 'not set')
    print(sess)

    return Response(json.dumps(t), mimetype='application/json')


if __name__ == '__main__':
    app.run(port = 5000, debug = True)