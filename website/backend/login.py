from flask import Blueprint, request, jsonify, make_response, redirect, url_for, render_template
from util.database.sql_util import get_cursor


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
            url = url_for('user_bp.user_profile', username=sql_result[1])
            return jsonify({'message': 'login successful', 'redirect_url': url,'currentUser': sql_result[1]}), 200
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
            url = url_for('user_bp.user_profile', username=username)
            return jsonify({'message': 'login successful', 'redirect_url': url,'user':{'username': username}}), 200
    except Exception as e:
        print(e)
        return make_response(jsonify({'message': 'error registering', 'error': str(e)}), 500)

