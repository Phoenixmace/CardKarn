from website.app import app
from flask import Flask, request, jsonify, make_response
from util.database.sql_util import get_cursor
from flask import render_template


@app.route('/api/register', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data['name']
        password = str(data['password'])
        connector, cursor  = get_cursor(filename='users.db')
        cursor.execute('SELECT password FROM users WHERE name = ?', (username,))
        sql_result = cursor.fetchone()
        if len(sql_result) == 0:
            return make_response(jsonify({'message': 'user not found'}), 404)
        elif password == sql_result[0]:
            return make_response(jsonify({'message': 'login successful'}), 200)
        else:
            return make_response(jsonify({'message': 'login failed'}), 401)

    except Exception as e:
        return make_response(jsonify({'message': 'error loging in', 'error': str(e)}), 500)

@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        username = data['name']
        mail = data['email']
        password = str(data['password'])
        connector, cursor  = get_cursor(filename='users.db')
        cursor.execute('SELECT password FROM users WHERE name = ?', (username,))

        if len(cursor.fetchall()) > 0:
            return make_response(jsonify({'message': 'user already exists'}), 409)
        else:
            cursor.execute('INSERT INTO users (name, email, password) VALUES (?, ?, ?)', (username, mail, password))
            connector.commit()
            connector.close()
            return make_response(jsonify({'message': 'registration successful'}), 201)
    except Exception as e:
        return make_response(jsonify({'message': 'error registering', 'error': str(e)}), 500)