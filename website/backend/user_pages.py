from flask import Blueprint, request, jsonify, make_response, redirect, url_for, render_template, session
from util.database.sql_util import get_cursor
from flask import current_app
import os
import config
from website.backend.backend_util.images import card_images
user_bp = Blueprint('user_bp', __name__)
UPLOAD_FOLDER = os.path.join(config.data_folder_path, 'website', 'user_uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@user_bp.route('/collection')
def user_collection(username=None):
    user = session.get('user')
    print(user)
    if not user:
        return render_template('index.html')
    else:
        return render_template('collection.html', username=username,user=user)
@user_bp.route('/profile/<username>')
def user_profile(username):
    user = session.get('user')
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
@user_bp.route('/api/update_profile', methods=['POST'])
def update_profile():
    user = session.get('user')
    # Extract form data
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    profile_picture = request.files.get('profile_picture')

    upload_folder = current_app.config['UPLOAD_FOLDER'] + os.sep + 'profile_pictures'
    if profile_picture:
        filename = str(user['id']) + '.png'
        user_url = os.path.join(upload_folder, filename)
        profile_picture.save(os.path.join(upload_folder, filename))
        session['user']['profile_picture'] = user_url
    else:
        user_url = None


    return jsonify({
        'message': 'Profile updated successfully',
        'profile_picture_url': filename if profile_picture and os.path.exists(user_url) else None
    })

@user_bp.route('/api/upload_collection', methods=['POST'])
def upload_collection():
    user = session.get('user')
    data = request.get_json()
    collection = data['csv_text']
    card_list = []
    for row in collection.split('\n')[:50]:
        try:
            path = card_images.get_image_path(row.split(',')[10])
            if path:
                card_list.append({'id':path.split(os.sep)[-1], 'name':row.split(',')[2], 'number': row.split(',')[8]})
        except:
            pass
    connector, cursor = get_cursor(filename='users.db')
    cursor.execute("UPDATE users SET collection = ? WHERE username = ?;", (str(card_list), user['name']))
    connector.commit()
    connector.close()
    return jsonify({
        'message': 'upload successful',
        'cards': card_list
    }), 200

@user_bp.route('/api/display_collection', methods=['POST'])
def display_collection():
    data = request.get_json()
    collection = data['sort_by']
    return jsonify({
        'message': 'upload successful',
        'cards': 'card_list'
    }), 200