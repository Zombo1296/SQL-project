from flask import Flask, request, send_from_directory
from flask_mysqldb import MySQL

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
    return app.send_static_file('logged_in.html')





if __name__ == '__main__':
    app.run()