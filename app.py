######################################
# author Jeffrey Mu jmu22@csa2.bu.edu
# Edited by: Baichuan Zhou (baichuan@bu.edu) and Craig Einstein <einstein@bu.edu>
######################################
# Some code adapted from 
# CodeHandBook at http://codehandbook.org/python-web-application-development-using-flask-and-mysql/
# and MaxCountryMan at https://github.com/maxcountryman/flask-login/
# and Flask Offical Tutorial at  http://flask.pocoo.org/docs/0.10/patterns/fileuploads/
# see links for further understanding
###################################################

import flask
from flask import Flask, Response, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
import flask.ext.login as flask_login

# for image uploading
# from werkzeug import secure_filename
import os, base64

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'super secret string'  # Change this!

# These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'hello'
app.config['MYSQL_DATABASE_DB'] = 'photoshare'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

# begin code used for login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
cursor.execute("SELECT email FROM Users")
users = cursor.fetchall()

def getUserList():
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM Users")
    return cursor.fetchall()

def getFriendList(uid1):
    cursor = conn.cursor()
    query = ("SELECT Fname, Lname, user_id FROM Friendship INNER JOIN Users ON user_id = UID2 WHERE UID1 = uid1".format(uid1))
    cursor.execute(query)
    return cursor.fetchall()

def getUsersPhotosfromAlb(aid, uid):
    cursor = conn.cursor()
    cursor.execute("SELECT imgdata, picture_id, caption FROM Pictures WHERE album_id = '{0}' AND user_id = '{1}'".format(aid, uid))
    return cursor.fetchall()

def getUsersPhotos(uid):
    cursor = conn.cursor()
    cursor.execute("SELECT imgdata, picture_id, caption FROM Pictures WHERE user_id = '{0}'".format(uid))
    return cursor.fetchall()  # NOTE list of tuples, [(imgdata, pid), ...]

def getUsersAlbums(uid):
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM Albums WHERE user_id = '{0}'".format(uid))
    return cursor.fetchall()

def getAlbumIDFromAlbum(albumm):
    cursor = conn.cursor()
    cursor.execute("SELECT album_id FROM Albums WHERE name = '{0}'".format(albumm))
    return cursor.fetchone()[0]


def GetUniquePic(pid):
    cursor = conn.cursor()
    cursor.execute("SELECT imgdata, picture_id, caption FROM Pictures WHERE picture_id = '{0}'".format(pid))
    return cursor.fetchall()

def getMatch(email1):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Users WHERE email = '{0}'".format(email1))
    return cursor.fetchall()  # NOTE list of tuples, [(imgdata, pid), ...]

def getUserIdFromEmail(email):
    cursor = conn.cursor()
    cursor.execute("SELECT user_id  FROM Users WHERE email = '{0}'".format(email))
    return cursor.fetchone()[0]

def isEmailUnique(email):
    # use this to check if a email has already been registered
    cursor = conn.cursor()
    if cursor.execute("SELECT email  FROM Users WHERE email = '{0}'".format(email)):
        # this means there are greater than zero entries with that email
        return False
    else:
        return True

def getTagPhoto(tag):
    cursor = conn.cursor()
    cursor.execute("SELECT imgdata, picture_id, caption FROM Pictures INNER JOIN Associate ON pid = picture_id "
                   "WHERE tid='{0}'".format(tag))
    return cursor.fetchall()

def getTagID(tag):
    cursor = conn.cursor()
    cursor.execute("SELECT tid FROM Tag WHERE tag_name = '{0}'".format(tag))
    return cursor.fetchone()[0]

class User(flask_login.UserMixin):
    pass

@login_manager.user_loader
def user_loader(email):
    users = getUserList()
    if not (email) or email not in str(users):
        return
    user = User()
    user.id = email
    return user

@login_manager.request_loader
def request_loader(request):
    users = getUserList()
    email = request.form.get('email')
    if not (email) or email not in str(users):
        return
    user = User()
    user.id = email
    cursor = mysql.connect().cursor()
    cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email))
    data = cursor.fetchall()
    pwd = str(data[0][0])
    user.is_authenticated = request.form['password'] == pwd
    return user

@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'GET':
        return '''
			   <form action='login' method='POST'>
				<input type='text' name='email' id='email' placeholder='email'></input>
				<input type='password' name='password' id='password' placeholder='password'></input>
				<input type='submit' name='submit'></input>
			   </form></br>
		   <a href='/'>Home</a>
			   '''
    # The request method is POST (page is recieving data)
    email = flask.request.form['email']
    cursor = conn.cursor()
    # check if email is registered
    if cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email)):
        data = cursor.fetchall()
        pwd = str(data[0][0])
        if flask.request.form['password'] == pwd:
            user = User()
            user.id = email
            flask_login.login_user(user)  # okay login in user
            return flask.redirect(flask.url_for('protected'))  # protected is a function defined in this file

    # information did not match
    return "<a href='/login'>Try again</a>\
			</br><a href='/register'>or make an account</a>"

@app.route('/logout')
def logout():
    flask_login.logout_user()
    return render_template('hello.html', message='Logged out')

@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('unauth.html')

# you can specify specific methods (GET/POST) in function header instead of inside the functions as seen earlier
@app.route("/register", methods=['GET'])
def register():
    return render_template('register.html', supress='True')

@app.route("/register", methods=['POST'])
def register_user():
    try:
        email = request.form.get('email')
        password = request.form.get('password')
        Fname = request.form.get('Fname')
        Lname = request.form.get('Lname')
        Hometown = request.form.get('Hometown')
        gender = request.form.get('gender')
        DOB = request.form.get('DOB')
    except:
        print(
            "couldn't find all tokens")  # this prints to shell, end users will not see this (all print statements go to shell)
        return flask.redirect(flask.url_for('register'))
    cursor = conn.cursor()
    test = isEmailUnique(email)
    if test:
        print(cursor.execute("INSERT INTO Users (email, password, Fname, Lname, Hometown, gender, DOB) "
                             "VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}')".format(email, password, Fname, Lname, Hometown, gender, DOB)))

        conn.commit()
        # log user in
        user = User()
        user.id = email
        flask_login.login_user(user)
        return render_template('hello.html', name=email, message='Account Created!')
    else:
        print("couldn't find all tokens")
        return flask.redirect(flask.url_for('register'))

# end login code

@app.route('/profile')
@flask_login.login_required
def protected():
    uid = getUserIdFromEmail(flask_login.current_user.id)
    return render_template('hello.html', name=flask_login.current_user.id, message="Here's your profile", photos=getUsersPhotos(uid))

# begin photo uploading code
# photos uploaded using base64 encoding so they can be directly embeded in HTML 
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/viewfriends')
@flask_login.login_required
def view_friends():
    uid1 = getUserIdFromEmail(flask_login.current_user.id)
    return render_template('friendlist.html', list=getFriendList(uid1))

@app.route('/addfriends', methods=['GET', 'POST'])
@flask_login.login_required
def search_friends():
    cursor = conn.cursor()
    if request.method == 'POST':
        if flask.request.form['email1']:
            email1 = flask.request.form['email1']
            query1 = "SELECT * FROM Users WHERE email = '{0}'".format(email1)

            if cursor.execute(query1):
                conn.commit()
                return render_template('friendinfo.html', matches = getMatch(email1))
            else:
                return render_template('addfriends.html')
        elif flask.request.form['email2']:
             email2 = flask.request.form['email2']
             uid1 = getUserIdFromEmail(flask_login.current_user.id)
             uid2 = getUserIdFromEmail(email2)
             query2 = "INSERT INTO Friendship (UID1, UID2) VALUES ('{0}', '{1}' )".format(uid1, uid2)
             if cursor.execute(query2):
                 conn.commit()
                 return render_template('friendlist.html', list=getFriendList(uid1))
             else:
                 return render_template('addfriends.html')
    else:
        return render_template('addfriends.html')

@app.route('/upload', methods=['GET', 'POST'])
@flask_login.login_required
def upload_file():
    if request.method == 'POST':
        uid = getUserIdFromEmail(flask_login.current_user.id)
        imgfile = request.files['photo']
        caption = request.form.get('caption')
        tag = request.form.get('tag')
        taglist = tag.split(' ')
        print(caption)
        photo_data = base64.standard_b64encode(imgfile.read())
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Pictures (imgdata, user_id, caption) VALUES ('{0}', '{1}', '{2}' )".format(photo_data, uid, caption))
        conn.commit()
        photo_id = cursor.lastrowid
        for x in taglist:
            if (x != ""):
                cursor.execute("INSERT INTO Tag (tag_name) VALUES ('{0}')".format(x))
                conn.commit()
                tagid = cursor.lastrowid
                cursor.execute("INSERT INTO Associate(pid, tid) VALUES ('{0}','{1}')".format(photo_id, tagid))
                conn.commit()
        return render_template('hello.html', name=flask_login.current_user.id, message='Photo uploaded!',
                               photos=getUsersPhotos(uid))
    # The method is GET so we return a  HTML form to upload the a photo.
    else:
        return render_template('upload.html')


# end photo uploading code
#Create an album


#look through an album
@app.route('/checkalbums', methods=['POST'])
@flask_login.login_required
def look_album():
    aname = flask.request.form['alname']
    uid = getUserIdFromEmail(flask_login.current_user.id)
    aid = getAlbumIDFromAlbum(aname)
    return render_template('albumx.html', allpics = getUsersPhotosfromAlb(aid, uid), album = aname)


@app.route('/createalbum', methods=['GET'])
@flask_login.login_required
def newalbum():
    uid = getUserIdFromEmail(flask_login.current_user.id)
    return render_template('newalbum.html')


@app.route('/createalbum', methods=['POST'])
@flask_login.login_required
def registernewalbum():
    uid = getUserIdFromEmail(flask_login.current_user.id)
    albname = flask.request.form['albname']
    cursor.execute("INSERT INTO Albums (name, user_id) VALUES ('{0}', '{1}')".format(albname, uid))
    conn.commit()
    return render_template('hello.html')

#see all albums
@app.route('/checkalbums')
@flask_login.login_required
def lookalbums():
    uid = getUserIdFromEmail(flask_login.current_user.id)
    return render_template('allalbums.html', albums=getUsersAlbums(uid))

#add photo to album
@app.route('/addtoalbum', methods=['GET'])
@flask_login.login_required
def newpage():
    return render_template('addpic.html')

@app.route('/addtoalbum', methods=['POST'])
@flask_login.login_required
def addtoalb():
    pid = flask.request.form['picname']
    aname = flask.request.form['aname']
    uid = getUserIdFromEmail(flask_login.current_user.id)
    aid = getAlbumIDFromAlbum(aname)
    cursor.execute("UPDATE Pictures SET album_id=%s WHERE user_id=%s AND picture_id=%s", (aid,uid,pid))
    conn.commit()
    return render_template('photoadded.html', Pic=GetUniquePic(pid), album = aname)



#delete a pic from an album
@app.route('/deletefromalbum', methods=['GET'])
@flask_login.login_required
def delpage():
    return render_template('deletepic.html')

@app.route('/deletefromalbum', methods=['POST'])
@flask_login.login_required
def delfromalb():
    pid = flask.request.form['picname']
    aname = flask.request.form['aname']
    uid = getUserIdFromEmail(flask_login.current_user.id)
    aid = getAlbumIDFromAlbum(aname)
    cursor.execute("UPDATE Pictures SET album_id=NULL WHERE user_id=%s AND picture_id=%s", (uid,pid))
    conn.commit()
    return render_template('photodeleted.html', album = aname)


#delete an album with pics in it

@app.route('/delalbum', methods=['GET'])
@flask_login.login_required
def directpage():
    return render_template('deletealbum.html')


@app.route('/delalbum', methods=['POST'])
@flask_login.login_required
def deletealbum():
    uid = getUserIdFromEmail(flask_login.current_user.id)
    aname = flask.request.form['Delalb']
    aid = getAlbumIDFromAlbum(aname)
    cursor.execute("UPDATE Pictures SET album_id=NULL WHERE user_id=%s AND album_id=%s", (uid, aid))
    cursor.execute("DELETE FROM Albums WHERE  user_id=%s AND album_id=%s", (uid, aid))
    conn.commit()
    return render_template('allalbums.html', albums=getUsersAlbums(uid))

#search by tag
@app.route('/searchbytag', methods=['POST', 'GET'])
def searchtag():
    if request.method == 'POST':
        tag= request.form.get('tag')
        tagid = getTagID(tag)
        return render_template('showtagphotos.html', tagged=getTagPhoto(tagid), tag = tag)
    return render_template('searchtag.html')

#look through all MY photos
@app.route('/allmyphotos', methods=['GET'])
@flask_login.login_required
def browsallmypics():
    uid = getUserIdFromEmail(flask_login.current_user.id)
    return render_template('hello.html', photos=getUsersPhotos(uid))

@app.route('/findpeople',methods=['GET'])
def findpeople():
    return render_template('findpeople.html')

@app.route('/findpeople',methods=['POST'])
def people():
    id = flask.request.form['userid']
    return render_template('hello.html', photos=getUsersPhotos(id))

#like a picture
@app.route('/likepicture', methods=['GET'])
@flask_login.login_required

def likepic():
    return render_template('likepage.html')

def getNameFromID(uid):
    cursor = conn.cursor()
    cursor.execute("SELECT Fname FROM Users WHERE user_id = '{0}'".format(uid))
    return cursor.fetchone()[0]

def getIDfromPicID(picid):
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM Pictures WHERE picture_id ='{0}'".format(picid))
    return cursor.fetchone()[0]

def getListLikers(picid):
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM Likes WHERE picture_id='{0}'".format(picid))
    return cursor.fetchall()

@app.route('/likepicture', methods=['POST'])
@flask_login.login_required
def likepc():
    PicID = flask.request.form['picid']
    OwnID = flask.request.form['ownid']
    Fname = getNameFromID(OwnID)
    otherID = getIDfromPicID(PicID)
    cursor.execute("INSERT INTO Likes (picture_id, name) VALUES ('{0}', '{1}')".format(PicID, Fname))
    conn.commit()
    return render_template('hello.html', photos = getUsersPhotos(otherID), likes = getListLikers(PicID) )
# default page
@app.route("/", methods=['GET'])
def hello():
    return render_template('hello.html', message='Welcome to Photoshare')


if __name__ == "__main__":
    # this is invoked when in the shell  you run
    # $ python app.py
    app.run(port=5000, debug=True)
