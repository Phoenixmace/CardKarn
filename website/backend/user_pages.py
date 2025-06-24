from flask import Blueprint, request, jsonify, make_response, redirect, url_for, render_template, session
from util.database.sql_util import get_cursor


user_bp = Blueprint('user_bp', __name__)

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
