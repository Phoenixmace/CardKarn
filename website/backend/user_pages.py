from flask import Blueprint, request, jsonify, make_response, redirect, url_for, render_template, session
from util.database.sql_util import get_cursor
import os
import config
user_bp = Blueprint('user_bp', __name__)
UPLOAD_FOLDER = os.path.join(config.data_folder_path, 'website', 'user_uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@user_bp.route('/collection/<username>')
def user_collection(username):
    return render_template('collection.html', username=username)
@user_bp.route('/profile/<username>')
def user_profile(username):
    user = session.get('user')
    print(user)
    if not user or user['name'] != username:
        return redirect(url_for('login_bp.login'))
    return render_template('profile.html', user=user)



@user_bp.route('/upload', methods=['POST'])
def upload_file():
    if 'csvFile' not in request.files:
        return 'Keine Datei gefunden', 400

    file = request.files['csvFile']
    if file.filename == '':
        return 'Leere Datei', 400

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)
    return f'Datei {file.filename} erfolgreich gespeichert!', 200
@user_bp.route('/update_profile', methods=['POST'])
def update_profile():
    print('hello')

