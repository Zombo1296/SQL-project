from flask import Flask, request, send_from_directory, Response, session
from flask_mysqldb import MySQL
from flask_session import Session
import hashlib
import json
import os
import datetime

app=Flask(__name__, static_url_path='')

app.config['SESSION_TYPE'] = 'filesystem'

app.config.from_object('config')

app.secret_key = os.urandom(24)
app.permanent_session_lifetime = datetime.timedelta(seconds=10*60)
Session(app)


mysql = MySQL()
mysql.init_app(app)




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

@app.route('/album/')
def album():
    return app.send_static_file('album.html')




@app.route('/api/addUser/', methods=['POST'])
def api_add_user():
    username = request.form.get('username')
    password = request.form.get("password")
    nickname = request.form.get("nickname")
    city = request.form.get("city")
    email = request.form.get("email")

    print (username)
    print (password)
    print (nickname)
    print (city)
    print (email)

    if(username == None or password == None or len(username) > 45 or
               len(password) != 40 or nickname != None and len(nickname) > 45
       or city != None and len(city) > 45 or email != None and len(email) > 45):
        t = {'status': 'error', 'error': 'Invalid input'}
        return Response(json.dumps(t), mimetype='application/json')

    username = username.lower()

    password = password + username
    m = hashlib.sha1()
    m.update(password.encode('utf-8'))
    password = m.hexdigest()

    conn = mysql.connect()
    cur = conn.cursor()
    cur.execute("SET SESSION TRANSACTION ISOLATION LEVEL SERIALIZABLE")
    cur.execute("START TRANSACTION")
    cur.execute('''SELECT uname FROM `User` WHERE uname = %s''', (username))
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
        t = {'status': 'error', 'error': 'Username already exists.'}
        return Response(json.dumps(t), mimetype='application/json')


@app.route('/api/login/', methods=['POST'])
def api_login():
    username = request.form.get('username')
    password = request.form.get("password")

    # print (username)
    # print (password)

    if(username == None or password == None or len(username) > 45 or
               len(password) != 40):
        t = {'status': 'error', 'error': 'Invalid input'}
        return Response(json.dumps(t), mimetype='application/json')

    username = username.lower()
    password = password + username
    m = hashlib.sha1()
    m.update(password.encode('utf-8'))
    password = m.hexdigest()

    conn = mysql.connect()
    cur = conn.cursor()
    cur.execute('''SELECT password FROM `User` WHERE uname = %s''', (username))
    rv = cur.fetchone()
    conn.rollback()
    conn.close()
    if rv == None:
        t = {'status': 'error', 'error': 'Invalid username or password'}
    else:
        if password == rv[0]:
            t = {'status': 'success'}
            session.permanent = True
            session['username'] = username
        else:
            t = {'status': 'error', 'error': 'Invalid username or password'}
    return Response(json.dumps(t), mimetype='application/json')

@app.route('/api/logout/', methods=['POST'])
def api_logout():
    session.pop('username', None)
    t = {'status': 'success'}
    return Response(json.dumps(t), mimetype='application/json')

@app.route('/api/getAlbum/', methods=['GET'])
def api_get_album():
    id = request.args.get('id')
    if(len(id) != 22):
        t = {'status': 'error', 'error': 'Invalid id'}
    else:
        conn = mysql.connect()
        cur = conn.cursor()
        cur.execute('''SELECT title, time FROM `Album` WHERE alid = %s''', (id))
        albuminfo = cur.fetchone()
        cur.execute('''SELECT tid, title, duration, by_aname FROM `Track` WHERE alid = %s''', (id))
        tracksinfo = cur.fetchall()
        cur.close()
        conn.close()
        tracksinfoList = []
        for row in tracksinfo:
            tracksinfoList.append({'tid' : row[0], 'title' : row[1], 'duration' : row[2], 'artist': row[3]})

        t = {'status': 'success', 'title': albuminfo[0], 'time': str(albuminfo[1]), 'tracks' : tracksinfoList}
    return Response(json.dumps(t), mimetype='application/json')


if __name__ == '__main__':
    app.run(port = 5000, debug = True)