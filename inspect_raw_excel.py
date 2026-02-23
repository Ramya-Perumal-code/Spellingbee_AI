import pandas as pd
excel_path = r'c:\Users\ramya\PycharmProjects\PythonProject\Agentic AI\db\word_list.xlsx'
df_raw = pd.read_excel(excel_path, header=None)
print("Raw Data (First 20 rows):")
print(df_raw.head(20).to_string())

# Check all unique values across the entire dataframe to see where 1B/2B/3B/Non SS might be hiding
all_values = set()
for col in df_raw.columns:
    all_values.update(df_raw[col].dropna().unique().tolist())

print("\nAll Unique Values Hiding in File:")
print(sorted([str(v) for v in all_values if v]))
