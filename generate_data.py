import pandas as pd

# Create dummy data
data = {
    'Name': ['Alice', 'Bob', 'Charlie', 'David', 'Eva'],
    'Age': [25, 30, 35, 40, 22],
    'City': ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix']
}

# Create DataFrame
df = pd.DataFrame(data)

# Save to Excel
excel_file = 'data.xlsx'
df.to_excel(excel_file, index=False)
print(f"Created {excel_file} with sample data.")
