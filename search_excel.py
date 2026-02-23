import pandas as pd
excel_path = r'c:\Users\ramya\PycharmProjects\PythonProject\Agentic AI\db\word_list.xlsx'
df = pd.read_excel(excel_path)

search_terms = ['1B', '2B', '3B', 'Non SS']
for term in search_terms:
    mask = df.stack().astype(str).str.contains(term, case=False, na=False)
    if mask.any():
        matches = df.stack()[mask]
        print(f"\nMatches for '{term}':")
        for idx, val in matches.items():
            row_idx, col_name = idx
            print(f"  Row {row_idx}, Column '{col_name}': {val}")
    else:
        print(f"\nNo matches found for '{term}' in the primary sheet.")

# Print all columns to be sure
print("\nAll columns in sheet:", df.columns.tolist())
