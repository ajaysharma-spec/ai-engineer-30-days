import sqlite3

conn = sqlite3.connect("demo.db")
cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS users (name TEXT, age INT)")
cursor.execute("INSERT INTO users VALUES ('Ajay', 23)")

conn.commit()

cursor.execute("SELECT * FROM users")
print(cursor.fetchall())

conn.close()
