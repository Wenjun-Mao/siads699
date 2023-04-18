# What are the top 3 stores
# What is the top selling product
# What is the name of the top selling product
# What is the name of the top selling product and how much did it sell
# How many sales did the tampa store have
# What was the count of invoices at the tampa store
# Who was the top customer
# Who bought the most products
# What was the worst selling product
# What is the capital of Texas
# who will win the super bowl

import pandas as pd

df = pd.read_csv('assets/Online_Retail_1000_v2.csv')
df['Sales'] = df['Quantity'] * df['UnitPrice']

# print(df.head())

# What are the top 3 stores
print(df['Store'].value_counts().head(3))

# What are the top 3 stores and their sales dollars
print(df.groupby('Store')['Sales'].sum().sort_values(ascending=False).head(3))

# What is the name of the top selling product
print(df.groupby('Description')['Sales'].sum().sort_values(ascending=False).head(1))

# What is the name of the top selling product and how much did it sell
print(df.groupby('Description')['Sales'].sum().sort_values(ascending=False).head(1))

# How many sales did the tampa store have
print(df[df['Store'] == 'Tampa']['InvoiceNo'].nunique())

# What was the count of invoices at the tampa store
print(df[df['Store'] == 'Tampa']['InvoiceNo'].nunique())

# Who was the top customer
print(df.groupby('CustomerID')['Sales'].sum().sort_values(ascending=False).head(1))

# Who bought the most products
print(df.groupby('CustomerID')['Quantity'].sum().sort_values(ascending=False).head(1))

# What was the worst selling product
print(df.groupby('Description')['Sales'].sum().sort_values(ascending=True).head(1))

# What is the capital of Texas
# No code generated

# who will win the super bowl
# No code generated
