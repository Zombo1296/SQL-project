from flask import Flask, request, send_from_directory
from flask_mysqldb import MySQL

app=Flask(__name__, static_url_path='')
app.config.from_object('config')
app.config.from_pyfile('config.py')



@app.route('/')
def root():
    # return app.send_static_file('homepage.html')
    return app.send_static_file('homepage.html')



if __name__ == '__main__':
    app.run()