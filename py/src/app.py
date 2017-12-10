from flask import Flask
app=Flask(__name__, static_url_path='')
app.config.from_object('config')
app.config.from_pyfile('config.py')



@app.route('/index/')
def root():
    app.send_static_file('../../dist/homepage.html')



if __name__ == '__main__':
    app.run()