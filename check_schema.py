import sqlite3
conn = sqlite3.connect('my_database.db')
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(bee_words)")
columns = cursor.fetchall()
print("Columns in bee_words:")
for col in columns:
    print(col)
conn.close()
