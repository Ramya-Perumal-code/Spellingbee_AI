from spelling_bee import SpellingBeeGame
import sqlite3

game = SpellingBeeGame()
print("Unique Metadata from Game Object:")
print(game.get_filter_metadata())

conn = sqlite3.connect('my_database.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM bee_words LIMIT 5")
print("\nFirst 5 rows in DB:")
for row in cursor.fetchall():
    print(row)
conn.close()
