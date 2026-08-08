import sqlite3
import csv
import os
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional, List
 
DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tasks.db")
PRIORITIES = ["High", "Medium", "Low"]

@dataclass
class Task:
    id: Optional[int] = None
    title: str = ""
    description: str = ""
    due_date: str = ""          
    priority: str = "Medium"    
    category: str = "General"
    completed: bool = False
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


class TaskDatabase:
 
    def __init__(self, db_path: str = DB_FILE):
        self.db_path = db_path
        self._create_table()
 
    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
 
    def _create_table(self):
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    due_date TEXT,
                    priority TEXT DEFAULT 'Medium',
                    category TEXT DEFAULT 'General',
                    completed INTEGER DEFAULT 0,
                    created_at TEXT
                )
                """
            )