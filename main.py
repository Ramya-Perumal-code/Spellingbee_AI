import pandas as pd
import sqlite3
import os

def create_db_from_excel(excel_file, db_file, table_name):
    """
    Reads an Excel file and stores the data into a SQLite database.
    """
    try:
        # Check if Excel file exists
        if not os.path.exists(excel_file):
            print(f"Error: File '{excel_file}' not found.")
            return

        # Read Excel file
        print(f"Reading {excel_file}...")
        df = pd.read_excel(excel_file)

        # Connect to SQLite database
        print(f"Connecting to database {db_file}...")
        conn = sqlite3.connect(db_file)
        
        # Store data to table
        print(f"Saving data to table '{table_name}'...")
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        
        # Verify data
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        print(f"Successfully inserted {len(rows)} rows into '{table_name}'.")
        
        # Close connection
        conn.close()
        print("Done.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Configuration
    EXCEL_FILE = 'bee_words.xlsx'
    DB_FILE = 'my_database.db'
    TABLE_NAME = 'bee_words'

    create_db_from_excel(EXCEL_FILE, DB_FILE, TABLE_NAME)
