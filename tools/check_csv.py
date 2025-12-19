import pandas as pd
from pathlib import Path
p = Path('data') / 'Restaurant reviews.csv'
print('CSV path:', p.resolve())
df = pd.read_csv(p)
print('Rows:', len(df))
print('Columns:', list(df.columns)[:10])
print('First review sample:', df.iloc[0].to_dict())
