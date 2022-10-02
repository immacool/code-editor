
import sqlite3

connection = sqlite3.connect('test.db')
cursor = connection.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY, name TEXT, value INTEGER)")
cursor.execute("INSERT INTO test VALUES (1, 'test', 1)")
cursor.execute("INSERT INTO test VALUES (2, 'test', 2)")
cursor.execute("INSERT INTO test VALUES (3, 'test', 3)")
cursor.execute("INSERT INTO test VALUES (4, 'test', 4)")
cursor.execute("INSERT INTO test VALUES (5, 'test', 5)")

connection.commit()
connection.close()