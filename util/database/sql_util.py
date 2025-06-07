import sqlite3

from util.data_util import data_util



def get_cursor(filename='cards.db'):
    db_path = data_util.get_data_path(filename, subfolder='sql', allow_not_existing=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    return conn, cursor