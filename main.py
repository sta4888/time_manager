import tkinter as tk
from tkinter import messagebox
import sqlite3
from plyer import notification
import schedule
import time
import threading
import os
from pystray import Icon, MenuItem as item, Menu
from PIL import Image


class TaskSchedulerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Task Scheduler")

        self.conn = sqlite3.connect('tasks.db')
        self.cursor = self.conn.cursor()
        self.create_db()

        self.setup_gui()
        self.start_tray()

    def create_db(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_name TEXT NOT NULL,
                start_time TEXT NOT NULL
            )
        ''')
        self.conn.commit()

    def setup_gui(self):
        self.task_name_var = tk.StringVar()
        self.start_time_var = tk.StringVar()

        tk.Label(self.root, text="Task Name:").pack()
        tk.Entry(self.root, textvariable=self.task_name_var).pack()

        tk.Label(self.root, text="Start Time (HH:MM):").pack()
        tk.Entry(self.root, textvariable=self.start_time_var).pack()

        tk.Button(self.root, text="Add Task", command=self.add_task).pack()
        tk.Button(self.root, text="Start", command=self.start_tasks).pack()

    def add_task(self):
        task_name = self.task_name_var.get()
        start_time = self.start_time_var.get()

        self.cursor.execute('INSERT INTO tasks (task_name, start_time) VALUES (?, ?)', (task_name, start_time))
        self.conn.commit()
        messagebox.showinfo("Task Added", f"Task '{task_name}' scheduled for {start_time}")

    def start_tasks(self):
        self.cursor.execute('SELECT * FROM tasks')
        tasks = self.cursor.fetchall()
        for task in tasks:
            schedule.every().day.at(task[2]).do(self.notify_task, task[1])

        threading.Thread(target=self.run_scheduler, daemon=True).start()

    def notify_task(self, task_name):
        notification.notify(
            title="Task Reminder",
            message=f"Time to start: {task_name}",
            timeout=10
        )

    def run_scheduler(self):
        while True:
            schedule.run_pending()
            time.sleep(1)

    def start_tray(self):
        image = Image.open("icon.png")
        menu = Menu(item('Quit', self.quit_app))
        self.icon = Icon("TaskScheduler", image, "Task Scheduler", menu)
        threading.Thread(target=self.icon.run, daemon=True).start()

    def quit_app(self, icon, item):
        self.icon.stop()
        self.root.quit()


if __name__ == "__main__":
    root = tk.Tk()
    app = TaskSchedulerApp(root)
    root.mainloop()
