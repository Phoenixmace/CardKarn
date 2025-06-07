import sqlite3

from util.data_util import data_util



def get_cursor(filename='cards.db', timeout=300):
    db_path = data_util.get_data_path(filename, subfolder='sql', allow_not_existing=True)
    conn = sqlite3.connect(db_path, timeout=timeout)
    cursor = conn.cursor()
    conn.execute('PRAGMA journal_mode=WAL;')
    conn.commit()
    return conn, cursor