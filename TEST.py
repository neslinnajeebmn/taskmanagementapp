import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('tasks.db')
c = conn.cursor()

# Query to get the table schema
c.execute("PRAGMA table_info(tasks)")
tasks_columns = c.fetchall()
print("Tasks Table Schema:")
for column in tasks_columns:
    print(column)

c.execute("PRAGMA table_info(users)")
users_columns = c.fetchall()
print("\nUsers Table Schema:")
for column in users_columns:
    print(column)

conn.close()