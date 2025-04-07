import sqlite3
import json
from datetime import datetime

class DatabaseHandler:
    def __init__(self, db_path='data/measurements.db'):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS objects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    width REAL NOT NULL,
                    height REAL NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    is_in_range BOOLEAN NOT NULL,
                    measurement_mode TEXT NOT NULL
                )
            ''')
            conn.commit()

    def add_measurement(self, width, height, is_in_range, measurement_mode):
        # Check for duplicates within a small tolerance (0.1 cm)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id FROM objects 
                WHERE ABS(width - ?) < 0.1 
                AND ABS(height - ?) < 0.1 
                AND is_in_range = ?
                AND timestamp >= datetime('now', '-1 minute')
            ''', (width, height, is_in_range))
            
            if cursor.fetchone() is None:
                cursor.execute('''
                    INSERT INTO objects (width, height, is_in_range, measurement_mode)
                    VALUES (?, ?, ?, ?)
                ''', (width, height, is_in_range, measurement_mode))
                conn.commit()
                return True
            return False

    def get_recent_measurements(self, limit=50):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT width, height, timestamp, is_in_range, measurement_mode
                FROM objects
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
            return cursor.fetchall()

    def clear_old_measurements(self, days=7):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM objects
                WHERE timestamp < datetime('now', '-? days')
            ''', (days,))
            conn.commit() 