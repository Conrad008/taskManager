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
 