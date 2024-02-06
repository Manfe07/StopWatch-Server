from flask import Blueprint, render_template, Flask, request, jsonify, redirect, url_for, session, flash

import module_users.datahandler as datahandler


users_Blueprint = Blueprint('users', __name__,  template_folder='templates')



def init():
    datahandler.init()

def getSessionUser():
    user = {
        'name': session.get('user_name', None),
        'permission': session.get('permission', 0),
    }
    return user

@users_Blueprint.route('/login', methods=['POST', 'GET'])
def login():
    sessionUser = getSessionUser()
    if request.method == 'POST':
        login = request.form
        userName = login['username']
        password = login['password']

        signedIn, permission, user= datahandler.verify(userName,password)
        if signedIn:
            session['logged_in'] = True
            session['permission'] = permission
            session['user_name'] = userName

        else:
            session['logged_in'] = False
            session['permission'] = 0
            session['user_name'] = None
            flash('wrong password!')
        return redirect(url_for('index'))
    else:
        
        return render_template('users/login.html')





@users_Blueprint.route('/logout')
def logout():
    session['logged_in'] = False
    session['permission'] = 0
    session['user_name'] = None
    return redirect(url_for('index'))


@users_Blueprint.route('/addUser', methods=['POST','GET'])
def add_user():
    sessionUser = getSessionUser()
    if sessionUser.get("permission") >= 3:
        if request.method == 'POST':
            login = request.form

            userName = login['username']
            password = login['password']
            email = login['email']
            permission = login['permission']
            if not datahandler.add_User(userName,password,permission,email):
                flash("Error creating User " + userName)

            return redirect(url_for('users.manageUsers'))

        elif request.method == 'GET':
            return redirect(url_for('users.manageUsers'))
    else:
        return redirect(url_for('index'))


@users_Blueprint.route('/', methods=['GET'])
def manageUsers():
    sessionUser = getSessionUser()
    if sessionUser.get("permission") >= 3:
        return render_template('users/manageUsers.html',users = datahandler.getUsers())
    else:
        return redirect(url_for('index'))

@users_Blueprint.route('/deleteUser', methods=['POST'])
def deleteUser():
    sessionUser = getSessionUser()
    if sessionUser.get("permission") >= 3:
        request_data = request.get_json()
        if 'id' in request_data:
            id = request_data["id"]
            datahandler.deleteUser(id)

        return redirect(url_for('user.manageUsers'))
    else:
        return redirect(url_for('user.login'))
