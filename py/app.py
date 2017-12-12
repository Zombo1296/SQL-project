from flask import Flask, request, send_from_directory, Response, session, render_template
from flaskext.mysql import MySQL
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

@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)



@app.route('/api/insert_update_rating/', methods=['POST'])
def api_insert_update_rating():
    username = session.get('username', None)
    if username == None:
        t = {'status': 'error', 'error': 'Login'}
        return Response(json.dumps(t), mimetype='application/json')
    rating = int(request.form.get('rating'))
    tid = request.form.get('tid')
    if (rating < 0 or rating > 45 or len(tid) != 22):
        t = {'status': 'error', 'error': 'Invalid input'}
        return Response(json.dumps(t), mimetype='application/json')
    print (username)
    print (rating)
    print (tid)
    conn = mysql.connect()
    cur = conn.cursor()
    # cur.execute("SET SESSION TRANSACTION ISOLATION LEVEL SERIALIZABLE")
    # cur.execute("START TRANSACTION")
    # cur.execute('''SELECT tid FROM `Rating` WHERE tid = %s''', (tid))
    # rv = cur.fetchone()
    # if rv == None:
    cur.execute(''' INSERT INTO `Rating` (uid, tid, rate)
                    SELECT uid, %s, %s FROM User WHERE uname = %s ON DUPLICATE KEY
                    UPDATE rate = VALUES(rate), time = VALUES(time)''' ,
                (tid, rating, username))
    cur.execute('''COMMIT;''')
    cur.close()
    conn.close()
    t = {'status': 'success'}
    return Response(json.dumps(t), mimetype='application/json')
# else:
    
#     cur.close()
#     conn.rollback()
#     conn.close()
#     t = {'status': 'error', 'error': 'Username already exists.'}
#     return Response(json.dumps(t), mimetype='application/json')


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


        #cur.execute('''SELECT tid, title, duration, by_aname FROM `Track` WHERE alid = %s''', (id))
        cur.execute('''SELECT T_R.tid, title, duration, COALESCE(rate,0) AS rate, by_aname 
                        From Track, 
                            (SELECT T.tid,rate FROM

                                (SELECT tid 
                                    FROM Track WHERE alid = %s) AS T 

                                LEFT JOIN 

                                (SELECT rate,tid 
                                    FROM Rating 
                                    WHERE uid = '2') AS R

                            ON R.tid = T.tid) AS T_R 

                        WHERE Track.tid = T_R.tid''',(id)); 

        tracksinfo = cur.fetchall()
        cur.close()
        conn.close()
        tracksinfoList = []
        for row in tracksinfo:
            tracksinfoList.append({'tid' : row[0], 'title' : row[1], 'duration' : row[2], 'rating' : row[3], 'artist': row[4]})

        t = {'status': 'success', 'title': albuminfo[0], 'time': str(albuminfo[1]), 'tracks' : tracksinfoList}
    return Response(json.dumps(t), mimetype='application/json')


@app.route('/api/getnewtracks/', methods=['GET'])
def api_get_new_tracks():
    username = session.get('username', None)
    if username == None:
        t = {'status': 'error', 'error': 'Login'}
    else:
        conn = mysql.connect()
        cur = conn.cursor()
        cur.execute('''SELECT tid, title, duration, aname, alid FROM Track, Likes, User
                            WHERE Track.by_aname = Likes.aname
                            AND Likes.uid = User.uid
                            AND User.uname = %s
                            LIMIT 7;''', (username))
        tracksinfo = cur.fetchall()
        cur.close()
        conn.close()
        tracksinfoList = []
        for row in tracksinfo:
            tracksinfoList.append({'tid': row[0], 'title': row[1], 'duration': row[2], 'artist': row[3], 'album': row[4]})
        t = {'status': 'success', 'tracks': tracksinfoList}
    return Response(json.dumps(t), mimetype='application/json')


@app.route('/api/getmyplaylists/', methods=['GET'])
def api_get_my_playlists():
    username = session.get('username', None)
    if username == None:
        t = {'status': 'error', 'error': 'Login'}
    else:
        conn = mysql.connect()
        cur = conn.cursor()
        cur.execute('''SELECT plid, title, time, count FROM Playlist, User
                        WHERE Playlist.by_uid = User.uid
                        AND uname = %s;''', (username))
        playlists = cur.fetchall()
        cur.close()
        conn.close()
        playlistsList = []
        for row in playlists:
            playlistsList.append({'plid': row[0], 'title': row[1], 'time': str(row[2]), 'count': row[3]})
        t = {'status': 'success', 'playlists': playlistsList}
    return Response(json.dumps(t), mimetype='application/json')


@app.route('/api/getmyrelatedplaylists/', methods=['GET'])
def api_get_my_related_playlists():
    username = session.get('username', None)
    if username == None:
        t = {'status': 'error', 'error': 'Login'}
    else:
        conn = mysql.connect()
        cur = conn.cursor()
        cur.execute('''SELECT plid, title, Playlist.time, count, u2.uname FROM Playlist, User u1, Follow, User u2
                        WHERE Playlist.by_uid = Follow.f_uid
                        AND Follow.uid = u1.uid
                        AND u1.uname = %s
                        AND u2.uid = Follow.f_uid''', (username))
        playlists = cur.fetchall()
        cur.close()
        conn.close()
        playlistsList = []
        for row in playlists:
            playlistsList.append({'plid': row[0], 'title': row[1], 'time': str(row[2]), 'count': row[3], 'uname': row[4]})
        t = {'status': 'success', 'playlists': playlistsList}
    return Response(json.dumps(t), mimetype='application/json')


@app.route('/api/search/', methods=['GET'])
def api_search():
    username = session.get('username', None)
    q = request.args.get('q')
    if username == None:
        t = {'status': 'error', 'error': 'Login'}
    elif q == None or len(q) > 20:
        t = {'status': 'error', 'error': 'Invalid input'}
    else:
        conn = mysql.connect()
        cur = conn.cursor()
        cur.execute('''SELECT title, by_aname, alid FROM Track
                        WHERE (MATCH(title)
                        AGAINST (%s IN BOOLEAN MODE))
                        ORDER BY MATCH(title)
                        AGAINST (%s IN BOOLEAN MODE) DESC
                        LIMIT 3;''', (q + '*', q + '*'))
        tracks = cur.fetchall()

        cur.execute('''SELECT title, alid FROM Album
                        WHERE (MATCH(title)
                        AGAINST (%s IN BOOLEAN MODE))
                        ORDER BY MATCH(title)
                        AGAINST (%s IN BOOLEAN MODE) DESC
                        LIMIT 3;''', (q + '*', q + '*'))
        albums = cur.fetchall()

        cur.execute('''SELECT aname, aid FROM Artist
                        WHERE (MATCH(aname, description)
                        AGAINST (%s IN BOOLEAN MODE))
                        ORDER BY
                        MATCH(aname, description)
                        AGAINST (%s IN BOOLEAN MODE) DESC
                        LIMIT 3;''', (q + '*', q + '*'))
        artists = cur.fetchall()

        cur.execute('''SELECT uname, nickname FROM User WHERE uname LIKE %s LIMIT 5''', (q + '%'))
        users = cur.fetchall()

        cur.close()
        conn.close()

        trackList = []
        for row in tracks:
            trackList.append({'title': row[0], 'description': row[1], 'album': row[2]})
        category1 = {'name': "Tracks", 'results' : trackList}

        artistList = []
        for row in artists:
            artistList.append({'title': row[0], 'aid': row[1]})
        category2 = {'name': "Artists", 'results': artistList}

        albumList = []
        for row in albums:
            albumList.append({'title': row[0], 'aid': row[1]})
        category3 = {'name': "Albums", 'results': albumList}

        userList = []
        for row in users:
            userList.append({'title': row[0], 'description': row[1], 'url' : '/user/' + row[0]})
        category4 = {'name': "Users", 'results': userList}

        results = {'category1': category1, 'category2': category2, 'category3': category3, 'category4': category4}
        t = {'status': 'success', 'results': results}
    return Response(json.dumps(t), mimetype='application/json')

@app.route('/api/getplaylists/', methods=['GET'])
def api_get_playlists():
    uname = request.args.get('username')
    if (uname == None or len(uname) > 45):
        t = {'status': 'error', 'error': 'Invalid username'}
    username = session.get('username', None)
    if username == None:
        t = {'status': 'error', 'error': 'Login'}
    else:
        conn = mysql.connect()
        cur = conn.cursor()
        cur.execute('''SELECT plid, title, time, count FROM Playlist, User
                        WHERE Playlist.by_uid = User.uid
                        AND uname = %s;''', (uname))
        playlists = cur.fetchall()
        cur.close()
        conn.close()
        playlistsList = []
        for row in playlists:
            playlistsList.append({'plid': row[0], 'title': row[1], 'time': str(row[2]), 'count': row[3]})
        t = {'status': 'success', 'playlists': playlistsList}
    return Response(json.dumps(t), mimetype='application/json')

@app.route('/api/getuser/', methods=['GET'])
def api_get_user():
    uname = request.args.get('username')
    username = session.get('username', None)
    if username == None:
        t = {'status': 'error', 'error': 'Login'}
        return Response(json.dumps(t), mimetype='application/json')
    if (uname == None or len(uname) > 45):
        uname = username
    conn = mysql.connect()
    cur = conn.cursor()
    cur.execute('''SELECT uname, nickname, email, city FROM User WHERE uname = %s;''', (uname))
    user = cur.fetchone()
    cur.execute('''SELECT COUNT(*) FROM `Follow`, User WHERE User.uid = Follow.f_uid AND uname = %s;''', (uname))
    count = cur.fetchone()
    cur.close()
    conn.close()
    if user == None:
        t = {'status': 'error', 'error': "No such user"}
    else:
        t = {'status': 'success', 'username': user[0], 'nickname': user[1], 'email' : user[2], 'city' : user[3],
             'followers' : count[0]}
    return Response(json.dumps(t), mimetype='application/json')

@app.route('/api/getfollowstatus/', methods=['GET'])
def api_get_follow_status():
    uname = request.args.get('username')
    username = session.get('username', None)
    if username == None:
        t = {'status': 'error', 'error': 'Login'}
        return Response(json.dumps(t), mimetype='application/json')
    if (uname == None or len(uname) > 45):
        t = {'status': 'error', 'error': 'Invalid uname'}
        return Response(json.dumps(t), mimetype='application/json')
    conn = mysql.connect()
    cur = conn.cursor()
    cur.execute('''SELECT COUNT(Follow.uid) FROM Follow, User u1, User u2
                    WHERE Follow.uid = u1.uid AND Follow.f_uid = u2.uid AND
                    u1.uname = %s AND u2.uname = %s; ''', (username, uname))
    followcount = cur.fetchone()
    cur.close()
    conn.close()
    t = {'status': 'success', 'followstatus': followcount[0]}

    return Response(json.dumps(t), mimetype='application/json')


if __name__ == '__main__':
    app.run(port = 5000, debug = True)