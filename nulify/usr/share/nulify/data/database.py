import sqlite3
import os
from datetime import datetime
import logging

class ObjectDatabase:
    def __init__(self):
        # Use user's home directory for database storage
        self.db_dir = os.path.expanduser('~/.nulify')
        self.db_path = os.path.join(self.db_dir, 'objects.db')
        self._init_db()

    def _init_db(self):
        try:
            # Create directory if it doesn't exist
            os.makedirs(self.db_dir, exist_ok=True)
            
            # Set proper permissions for the directory
            os.chmod(self.db_dir, 0o755)
            
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
                
            # Set proper permissions for the database file
            if os.path.exists(self.db_path):
                os.chmod(self.db_path, 0o644)
                
        except (sqlite3.Error, OSError) as e:
            logging.error(f"Database initialization error: {str(e)}")
            raise

    def add_object(self, width, height, mode):
        try:
            # Create a unique hash based on dimensions (rounded to 1 decimal place)
            object_hash = f"{round(width, 1)}_{round(height, 1)}"
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR IGNORE INTO objects (width, height, mode, hash)
                    VALUES (?, ?, ?, ?)
                ''', (width, height, mode, object_hash))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            logging.error(f"Error adding object to database: {str(e)}")
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
            logging.error(f"Error retrieving recent objects: {str(e)}")
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
            logging.error(f"Error retrieving all objects: {str(e)}")
            return []

    def clear_database(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM objects')
                conn.commit()
                return True
        except sqlite3.Error as e:
            logging.error(f"Error clearing database: {str(e)}")
            return False 