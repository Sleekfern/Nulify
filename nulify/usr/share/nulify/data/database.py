import sqlite3
import os
from datetime import datetime

class ObjectDatabase:
    def __init__(self):
        data_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(data_dir, 'objects.db')
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS objects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    width REAL NOT NULL,
                    height REAL NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    mode TEXT NOT NULL,
                    hash TEXT UNIQUE NOT NULL
                )
            ''')
            conn.commit()

    def add_object(self, width, height, mode):
        # Create a unique hash based on dimensions (rounded to 1 decimal place)
        # This helps prevent duplicates of the same object
        object_hash = f"{round(width, 1)}_{round(height, 1)}"
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR IGNORE INTO objects (width, height, mode, hash)
                    VALUES (?, ?, ?, ?)
                ''', (width, height, mode, object_hash))
                conn.commit()
                return cursor.rowcount > 0  # Returns True if inserted, False if ignored
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False

    def get_recent_objects(self, limit=10):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT width, height, timestamp, mode
                    FROM objects
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (limit,))
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []

    def get_all_objects(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT width, height, timestamp, mode
                    FROM objects
                    ORDER BY timestamp DESC
                ''')
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []

    def clear_database(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM objects')
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False 