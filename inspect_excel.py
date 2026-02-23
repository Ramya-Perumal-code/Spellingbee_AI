import pandas as pd
excel_path = r'c:\Users\ramya\PycharmProjects\PythonProject\Agentic AI\db\word_list.xlsx'
df = pd.read_excel(excel_path)
print("Columns:", df.columns.tolist())
print("First 5 rows:")
print(df.head())
unique_years = df['Year'].unique().tolist() if 'Year' in df.columns else []
unique_lists = df['List'].unique().tolist() if 'List' in df.columns else []
unique_difficulty = df['Difficulty'].unique().tolist() if 'Difficulty' in df.columns else []
print("\nUnique Years:", unique_years)
print("Unique Lists:", unique_lists)
print("Unique Difficulty:", unique_difficulty)
