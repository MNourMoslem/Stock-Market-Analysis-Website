import pandas as pd
import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('./website/db.sqlite3')

# Read the entire table into a DataFrame
df = pd.read_sql('SELECT * FROM stock_stock', conn)

# Close the connection
conn.close()

uni = df['symbol'].unique()

print(df)  # View the first few rows
print(uni)
print(len(uni))