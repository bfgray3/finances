import json

import polars as pl

df = (
    pl.read_csv("balance-sheet.csv")
    .select(pl.exclude("Notes", "Change", "Total"))
    .with_columns(pl.exclude("Date").str.replace_all("[,$]", ""))
    .select(
        pl.col("Date").str.to_date("%-m/%-d/%Y"), pl.exclude("Date").cast(pl.Decimal)
    )
)

assert df.null_count().select(s=pl.sum_horizontal(pl.all())).row(0, named=True) == {
    "s": 0
}

print(df)

with open("names.json") as f:
    asset_indicators = json.load(f)


""" from the docs
from databases import Database
database = Database('sqlite+aiosqlite:///example.db')
await database.connect()

query = "INSERT INTO HighScores(name, score) VALUES (:name, :score)"
values = [
    {"name": "Daisy", "score": 92},
    {"name": "Neil", "score": 87},
    {"name": "Carol", "score": 43},
]
await database.execute_many(query=query, values=values)

query = "SELECT * FROM HighScores"
rows = await database.fetch_all(query=query)
print('High Scores:', rows)
"""

for col in set(df.columns) - {"Date"}:
    is_asset = col in asset_indicators["assets"]
    print(col, is_asset)


for row in df.iter_rows(named=True):
    # TODO: insert into the various tables
    print(row)
