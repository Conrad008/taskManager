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

    def insert(self, task: Task) -> int:
        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO tasks (title, description, due_date, priority,
                                    category, completed, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (task.title, task.description, task.due_date, task.priority,
                 task.category, int(task.completed), task.created_at),
            )
            return cur.lastrowid
 
    def get_all(self, order_by_priority: bool = False) -> List[Task]:
        query = "SELECT * FROM tasks"
        if order_by_priority:
            # Custom ordering: High -> Medium -> Low
            query += """
                ORDER BY CASE priority
                    WHEN 'High' THEN 1
                    WHEN 'Medium' THEN 2
                    WHEN 'Low' THEN 3
                    ELSE 4 END, id
            """
        else:
            query += " ORDER BY id"
        with self._connect() as conn:
            rows = conn.execute(query).fetchall()
        return [self._row_to_task(r) for r in rows]
 
    def get_by_category(self, category: str) -> List[Task]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM tasks WHERE LOWER(category) = LOWER(?) ORDER BY id",
                (category,),
            ).fetchall()
        return [self._row_to_task(r) for r in rows]
 
    def get_by_id(self, task_id: int) -> Optional[Task]:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        return self._row_to_task(row) if row else None
 
    def update(self, task: Task) -> bool:
        with self._connect() as conn:
            cur = conn.execute(
                """
                UPDATE tasks
                SET title = ?, description = ?, due_date = ?, priority = ?, category = ?
                WHERE id = ?
                """,
                (task.title, task.description, task.due_date, task.priority,
                 task.category, task.id),
            )
            return cur.rowcount > 0
 
    def mark_complete(self, task_id: int) -> bool:
        with self._connect() as conn:
            cur = conn.execute("UPDATE tasks SET completed = 1 WHERE id = ?", (task_id,))
            return cur.rowcount > 0
 
    def delete(self, task_id: int) -> bool:
        with self._connect() as conn:
            cur = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            return cur.rowcount > 0
 
    @staticmethod
    def _row_to_task(row: sqlite3.Row) -> Task:
        return Task(
            id=row["id"],
            title=row["title"],
            description=row["description"] or "",
            due_date=row["due_date"] or "",
            priority=row["priority"] or "Medium",
            category=row["category"] or "General",
            completed=bool(row["completed"]),
            created_at=row["created_at"] or "",
        )