import asyncio
import json

import polars as pl
from databases import Database

POPULATE_CLASSES_STMT = (
    "insert into finances.classes(name, is_asset) values (:name, :is_asset)"
)
POPULATE_AMOUNTS_STMT = "insert into finances.amounts(day, amount, class_id) values (:day, :amount, :class_id)"

df = (
    pl.read_csv("balance-sheet.csv")
    .select(pl.exclude("Notes", "Change", "Total"))
    .with_columns(pl.exclude("Date").str.replace_all("[,$]", ""))
    .select(
        pl.col("Date").str.to_date("%-m/%-d/%Y"), pl.exclude("Date").cast(pl.Decimal)
    )
)

non_date_cols = [c for c in df.columns if c != "Date"]

assert df.null_count().select(s=pl.sum_horizontal(pl.all())).row(0, named=True) == {
    "s": 0
}

with open("names.json") as f:
    asset_indicators = json.load(f)


asset_info = [
    {"name": col, "is_asset": col in asset_indicators["assets"]}
    for col in non_date_cols
]


async def main() -> None:
    async with Database("mysql+aiomysql://bernie:berniepw@db:3306") as db:
        await db.execute_many(query=POPULATE_CLASSES_STMT, values=asset_info)
        rows = await db.fetch_all(query="select * from finances.classes")
        class_ids = {r.name: r.id for r in rows}
        amount_info = [
            [
                {"day": r["Date"], "amount": r[c], "class_id": class_ids[c]}
                for c in non_date_cols
            ]
            for r in df.iter_rows(named=True)
        ]
        flattened_amount_info = [entry for entries in amount_info for entry in entries]
        await db.execute_many(query=POPULATE_AMOUNTS_STMT, values=flattened_amount_info)


asyncio.run(main())
