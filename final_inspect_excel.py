import pandas as pd
excel_path = r'c:\Users\ramya\PycharmProjects\PythonProject\Agentic AI\db\word_list.xlsx'
df = pd.read_excel(excel_path)

# Standardize column labels for analysis
standard_cols = {c.strip().lower(): c for c in df.columns}
print("Original Columns:", df.columns.tolist())

# Check Difficulty Level
diff_col = None
for k in standard_cols:
    if 'difficulty' in k:
        diff_col = standard_cols[k]
        break

# Check List
list_col = None
for k in standard_cols:
    if 'list' in k:
        list_col = standard_cols[k]
        break

if diff_col:
    print(f"\nUnique values in '{diff_col}':")
    print(df[diff_col].dropna().unique().tolist())

if list_col:
    print(f"\nUnique values in '{list_col}':")
    # Show values including potential counts
    print(df[list_col].value_counts(dropna=False))
