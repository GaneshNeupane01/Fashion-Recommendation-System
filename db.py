import sqlite3

conn = sqlite3.connect("users.db")
c = conn.cursor()
c.execute("SELECT * FROM users")
users = c.fetchall()
conn.close()

for user in users:
    print(user)  # Print all users (username, password, email)
