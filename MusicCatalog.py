from flask import Flask, render_template, request, redirect, jsonify
from flask import url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup1 import Base, MusicType, MusicName, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
import webbrowser

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Music Catalogue Application"

engine = create_engine('sqlite:///musicitemcatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
@app.route('/music/')
def showMusic():
    music = session.query(MusicType).order_by(asc(MusicType.id))
    return render_template('music.html', Music=music)


@app.route('/music_type_id/<int:musictype_id>/')
def showMusic_type(musictype_id):
    musicitem = session.query(MusicName).filter_by(
        musicname_id=musictype_id).all()
    musicname = session.query(MusicType).filter_by(id=musictype_id).one()
    return render_template('musictype.html',
                           musicitem=musicitem, tmusictype=musicname)


@app.route('/newmusic_type/<int:musictype_id>/')
def shownewMusic_type(musictype_id):
    musicitem = session.query(MusicName).filter_by(
        musicname_id=musictype_id).all()
    musicname = session.query(MusicType).filter_by(id=musictype_id).one()
    return render_template('newmusictype.html',
                           musicitem=musicitem, tmusictype=musicname)


@app.route('/newmusic/')
def shownewMusic():
    musictype = session.query(MusicType).order_by(asc(MusicType.id))
    return render_template('afmusic.html', music=musictype)


@app.route('/newmusic/new/', methods=['GET', 'POST'])
def newmusic():
    if 'username' not in login_session:
        return redirect('/login')

    elif request.method == 'POST':
        newmusic = MusicType(name=request.form['name'],
                             user_id=login_session['user_id'])
        session.add(newmusic)
        session.commit()
        return redirect(url_for('shownewMusic'))
    else:
        return render_template('newtype.html')


@app.route('/newmusic/<int:musictype_id>/delete/',
           methods=['GET', 'POST'])
def deletetype(musictype_id):
    typeToDelete = session.query(
        MusicType).filter_by(id=musictype_id).one()
    typemusic = session.query(MusicName).filter_by(
        musicname_id=musictype_id).all()
    if 'username' not in login_session:
        return redirect('/login')
    if typeToDelete.user_id != login_session['user_id']:
        return "<script>function myFunction() \
        {alert('You are not authorized to delete this type. \
        Please create your own type in order to delete.');\
        setTimeout(function() \
        {window.location.href = '/newmusic/';}, 1000);}\
        </script><body onload='myFunction()'>"
    if request.method == 'POST':
        for i in typemusic:
            session.delete(i)
            session.commit()
        session.delete(typeToDelete)
        session.commit()
        return redirect(url_for('shownewMusic'))
    else:
        return render_template('deletetype.html', music=typeToDelete)


@app.route('/music/<int:musictype_id>/edit', methods=['GET', 'POST'])
def edittype(musictype_id):
    editedtype = session.query(MusicType).filter_by(id=musictype_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if editedtype.user_id != login_session['user_id']:
        return "<script>function myFunction() \
        {alert('You are not authorized to edit this type. \
        Please create your own type in order to edit.');\
        setTimeout(function() \
        {window.location.href = '/newmusic/';}, 1000);}\
        </script><body onload='myFunction()'>"
    if request.method == 'POST':
        if request.form['name']:
            editedtype.name = request.form['name']
            return redirect(url_for('shownewMusic'))
    else:
        return render_template('edittype.html', type=editedtype)


@app.route('/newmusic/<int:musictype_id>/new', methods=['GET', 'POST'])
def addnewMusic(musictype_id):
    musicitem = session.query(MusicName).filter_by(
        musicname_id=musictype_id).all()
    musicname = session.query(MusicType).filter_by(
        id=musictype_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if musicname.user_id != login_session['user_id']:
        return "<script>function myFunction() \
        {alert('You are not authorized to add Music.');\
        setTimeout(function()\
        {window.location.href = '/newmusic/';}, 1000);}</script>\
        <body onload='myFunction()'>"
    if request.method == 'POST':
        newmusic = MusicName(name=request.form['name'],
                             releaseyear=request.form['releaseyear'],
                             artist=request.form['artist'],
                             musicname_id=musictype_id)
        session.add(newmusic)
        session.commit()
        return redirect(url_for('shownewMusic_type',
                                musictype_id=musictype_id))
    else:
        return render_template('addnewmusic.html',
                               Musicitem=musicitem,
                               tmusictype=musicname)


@app.route('/newmusic/<int:musictype_id>/<int:music_id>/edit',
           methods=['GET', 'POST'])
def editMusic(musictype_id, music_id):
    type = session.query(MusicType).filter_by(id=musictype_id).one()
    editmusic = session.query(MusicName).filter_by(id=music_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if type.user_id != login_session['user_id']:
        return "<script>function myFunction() \
        {alert('You are not authorized to edit this Music. \
        Please create your own Music in order to edit.');\
        setTimeout(function()\
        {window.location.href = '/newmusic/';}, 1000);}</script>\
        <body onload='myFunction()'>"
    if request.method == 'POST':
        if request.form['name']:
            editmusic.name = request.form['name']
        if request.form['releaseyear']:
            editmusic.releaseyear = request.form['releaseyear']
        if request.form['artist']:
            editmusic.artist = request.form['artist']
        session.add(editmusic)
        session.commit()
        return redirect(url_for('shownewMusic_type',
                                musictype_id=musictype_id))
    else:
        return render_template('editmusicitem.html',
                               type=type, editMusic=editmusic)


@app.route('/newmusic/<int:musictype_id>/<int:music_id>/delete',
           methods=['GET', 'POST'])
def deletemusic(musictype_id, music_id):
    type = session.query(MusicType).filter_by(id=musictype_id).one()
    musicToDelete = session.query(MusicName).filter_by(id=music_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if type.user_id != login_session['user_id']:
        return "<script>function myFunction() \
        {alert('You are not authorized to delete this Music. Please create \
        your own Music in order to delete.');\
        setTimeout(function() \
        {window.location.href = '/newmusic/';}, 1000);}</script><body \
        onload='myFunction()'>"
    if request.method == 'POST':
        session.delete(musicToDelete)
        session.commit()
        return redirect(url_for('shownewMusic_type',
                                musictype_id=musictype_id))
    else:
        return render_template('deletemusic.html',
                               music=musicToDelete, type=type)


@app.route('/musictype/<int:musictype_id>/music/JSON')
def TypemusicJSON(musictype_id):
    type = session.query(MusicType).filter_by(id=musictype_id).all()
    mov = session.query(MusicName).filter_by(
            id=musictype_id).all()
    return jsonify(musicitem=[i.serialize for i in mov])


@app.route('/musictype/<int:musictype_id>/<int:music_id>/JSON')
def musicJSON(musictype_id, music_id):
    music = session.query(MusicName).filter_by(id=music_id).all()
    return jsonify(Menu_Item=[r.serialize for r in music])


@app.route('/music/JSON')
def musictypeJSON():
    type = session.query(MusicType).all()
    return jsonify(Genre=[r.serialize for r in type])


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


# GConnect
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code, now compatible with Python3
    request.get_data()
    code = request.data.decode('utf-8')

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    # Submit request, parse response - Python3 compatible
    h = httplib2.Http()
    response = h.request(url, 'GET')[1]
    str_response = response.decode('utf-8')
    result = json.loads(str_response)

    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;\
    border-radius: 150px;-webkit-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    return output

# User Helper Functions


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

# DISCONNECT - Revoke a current user's token and reset their login_session


@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        # Reset the user's sesson.
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        # response = make_response(json.dumps('Successfully disconnected.)
        # response.headers['Content-Type'] = 'application/json'
        response = redirect(url_for('showMusic'))
        flash("You are now logged out.")
        return response
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
