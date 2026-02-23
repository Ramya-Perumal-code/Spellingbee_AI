import pandas as pd
excel_path = r'c:\Users\ramya\PycharmProjects\PythonProject\Agentic AI\db\word_list.xlsx'
xl = pd.ExcelFile(excel_path)
print("Sheet Names:", xl.sheet_names)

for sheet in xl.sheet_names:
    print(f"\n--- Sheet: {sheet} ---")
    df = pd.read_excel(excel_path, sheet_name=sheet)
    print("Columns:", df.columns.tolist())
    for col in df.columns:
        unique_vals = df[col].dropna().unique().tolist()
        if unique_vals:
            print(f"Column '{col}' Unique (Top 10):", unique_vals[:10])
