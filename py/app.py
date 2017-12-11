from flask import Flask, request, send_from_directory, Response
from flask_mysqldb import MySQL
import json

app=Flask(__name__, static_url_path='')
app.config.from_object('config')
app.config.from_pyfile('config.py')
mysql = MySQL(app)



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




@app.route('/addUser/', methods=['POST'])
def add_user():
    uname = request.args.get("uname")
    password = request.args.get("password")
    nickname = request.args.get("nickname")
    city = request.args.get("city")
    t = {'a' : 'test'}
    return Response(json.dumps(t), mimetype='application/json')





if __name__ == '__main__':
    app.run()