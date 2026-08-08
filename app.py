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

class TaskManagerApp:
 
    MENU = """
    ==================== TASK MANAGER ====================
    1) Add task
    2) View tasks
    3) Edit task
    4) Complete task
    5) Delete task
    6) View tasks
    7) Sort tasks
    8) Export tasks to CSV
    9) Exit
    ========================================================"""
 
    def __init__(self):
        self.db = TaskDatabase()

    def run(self):
        print("Welcome to Task Manager!")
        while True:
            print(self.MENU)
            choice = input("Choose an option (1-9): ").strip()
 
            if choice == "1":
                self.add_task()
            elif choice == "2":
                self.view_tasks()
            elif choice == "3":
                self.edit_task()
            elif choice == "4":
                self.complete_task()
            elif choice == "5":
                self.delete_task()
            elif choice == "6":
                self.view_by_category()
            elif choice == "7":
                self.view_tasks(order_by_priority=True)
            elif choice == "8":
                self.export_csv()
            elif choice == "9":
                print("Goodbye!")
                break
            else:
                print("Invalid choice, please pick a number from 1 to 9.")

    def add_task(self):
        print("\n--- Add New Task ---")
        title = input("Title: ").strip()
        if not title:
            print("Title cannot be empty. Task not added.")
            return
        description = input("Description (optional): ").strip()
        due_date = self._prompt_due_date()
        priority = self._prompt_priority()
        category = input("Category (default 'General'): ").strip() or "General"
 
        task = Task(title=title, description=description, due_date=due_date,
                    priority=priority, category=category)
        new_id = self.db.insert(task)
        print(f"Task added successfully with ID {new_id}.")

    def view_tasks(self, order_by_priority: bool = False):
        tasks = self.db.get_all(order_by_priority=order_by_priority)
        self._print_table(tasks)

    def view_by_category(self):
        category = input("Enter category to filter by: ").strip()
        tasks = self.db.get_by_category(category)
        if not tasks:
            print(f"No tasks found in category '{category}'.")
            return
        self._print_table(tasks)

    def edit_task(self):
        self.view_tasks()
        task_id = self._prompt_int("Enter the ID of the task to edit: ")
        if task_id is None:
            return
        task = self.db.get_by_id(task_id)
        if task is None:
            print(f"No task found with ID {task_id}.")
            return

        print("\n--- Edit Task ---")
        print("Press Enter to keep the current value shown in brackets.\n")
 
        new_title = input(f"Title [{task.title}]: ").strip()
        if new_title:
            task.title = new_title
 
        new_description = input(f"Description [{task.description or '-'}]: ").strip()
        if new_description:
            task.description = new_description
 
        new_due_date = self._prompt_due_date(current=task.due_date)
        task.due_date = new_due_date
 
        new_priority = self._prompt_priority(current=task.priority)
        task.priority = new_priority
 
        new_category = input(f"Category [{task.category}]: ").strip()
        if new_category:
            task.category = new_category
 
        if self.db.update(task):
            print(f"Task {task_id} updated successfully.")
        else:
            print(f"Failed to update task {task_id}.")

    def complete_task(self):
        self.view_tasks()
        task_id = self._prompt_int("Enter the ID of the task to mark complete: ")
        if task_id is None:
            return
        if self.db.mark_complete(task_id):
            print(f"Task {task_id} marked as complete.")
        else:
            print(f"No task found with ID {task_id}.")
 
