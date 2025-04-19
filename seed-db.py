import asyncio
import json

import polars as pl
from databases import Database

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


database = Database("mysql+aiomysql://root:foobar@db:3306")
populate_classes_stmt = (
    "insert into finances.classes(name, is_asset) values (:name, :is_asset)"
)

asset_info = [
    {"name": col, "is_asset": col in asset_indicators["assets"]}
    for col in df.columns
    if col != "Date"
]
print(asset_info)


async def main() -> None:
    await database.connect()

    await database.execute_many(query=populate_classes_stmt, values=asset_info)

    rows = await database.fetch_all(query="select * from finances.classes")
    print(f"{rows=}")


# for row in df.iter_rows(named=True):
# TODO: insert into the various tables
# this will be moved into main
#    print(row)

asyncio.run(main())
