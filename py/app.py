from flask import Flask, request, send_from_directory, Response, session
from flask_mysqldb import MySQL
from flask_session import Session
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
    print(password)
    print(nickname)
    print(city)
    print(email)

    t = {'status' : 'error', 'error': 'Haha'}
    sess = session.get('username', 'not set')
    print(sess)

    return Response(json.dumps(t), mimetype='application/json')


if __name__ == '__main__':
    app.run(port = 80, debug = True)