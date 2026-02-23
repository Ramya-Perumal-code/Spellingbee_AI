import sqlite3
conn = sqlite3.connect('my_database.db')
count = conn.execute("SELECT COUNT(*) FROM bee_words").fetchone()[0]
print(f"Total words in database: {count}")
conn.close()
