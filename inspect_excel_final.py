import pandas as pd
excel_path = r'c:\Users\ramya\PycharmProjects\PythonProject\Agentic AI\db\word_list.xlsx'
df = pd.read_excel(excel_path)
print("Columns:", df.columns.tolist())
print("\nFirst 10 rows:")
print(df.head(10))

for col in df.columns:
    unique_vals = df[col].dropna().unique().tolist()
    print(f"\nColumn '{col}' Unique Values (non-null):", unique_vals[:20])
