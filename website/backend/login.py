from flask import Blueprint, request, jsonify, make_response, redirect, current_app, url_for, render_template, session
from util.database.sql_util import get_cursor
import config
import os

login_bp = Blueprint('login_bp', __name__)

@login_bp.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()

        input = data['identifier']
        if '@' in input:
            search_field = 'email'
        else:
            search_field = 'username'
        password = str(data['password'])
        connector, cursor  = get_cursor(filename='users.db')
        cursor.execute(f'SELECT password, username FROM users WHERE {search_field} = ?', (input,))
        sql_result = cursor.fetchone()
        if len(sql_result) == 0:
            return make_response(jsonify({'message': 'user not found'}), 404)
        elif password == sql_result[0]:
            username = sql_result[1]
            return successful_login(username)

        else:
            return make_response(jsonify({'message': 'login failed'}), 401)

    except Exception as e:
        print(e)
        return make_response(jsonify({'message': 'error loging in', 'error': str(e)}), 500)

@login_bp.route('/api/register', methods=['POST'])
def register():
    from website.app import db
    try:
        data = request.get_json()
        username = data['name']
        mail = data['email']
        password = str(data['password'])
        connector, cursor  = get_cursor(filename='users.db')
        cursor.execute('SELECT username, password FROM users WHERE username = ? or email = ?', (username,mail))
        result = cursor.fetchall()
        if result and len(result) > 0:
            existing_var = 'username' if result[0] == username else 'email'
            return make_response(jsonify({'message': f'{existing_var} already exists'}), 409)
        else:
            cursor.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', (username, mail, password))
            connector.commit()
            connector.close()
            return successful_login(username)
    except Exception as e:
        print(e)
        return make_response(jsonify({'message': 'error registering', 'error': str(e)}), 500)
@login_bp.route('/api/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    return jsonify({'message': 'logout successful','redirect_url': '/'}), 200

def successful_login(username):
    connector, cursor = get_cursor(filename='users.db')
    cursor.execute('SELECT email, collection, decks, phone_number, id FROM users WHERE username = ?', (username,))
    response = cursor.fetchone()
    upload_folder = current_app.config['UPLOAD_FOLDER'] + os.sep + 'profile_pictures'
    filename = str(response[4]) + '.png'
    user_url = os.path.join(upload_folder, filename)
    if os.path.exists(user_url):
        profile_picture = filename
    else:
        profile_picture = None
    session['user'] = {'name': username, 'email': response[0], 'phone': response[3], 'profile_picture':profile_picture, 'collection':["example.png"], 'decks':response[2], 'id':response[4]}
    url = url_for('user_bp.user_profile', username=username)
    return jsonify({
        'message': 'login successful',
        'redirect_url': url
    }), 200
