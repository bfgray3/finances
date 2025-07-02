import asyncio
import json
import logging

import polars as pl
from databases import Database

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

POPULATE_CLASSES_STMT = (
    "insert into finances.classes(name, is_asset) values (:name, :is_asset)"
)
POPULATE_AMOUNTS_STMT = "insert into finances.amounts(day_id, amount, class_id) values (:day_id, :amount, :class_id)"
POPULATE_DATES_STMT = "insert into finances.dates(day) values (:day)"
POPULATE_COMMENTS_STMT = (
    "insert into finances.comments(day_id, comments) values (:day_id, :comments)"
)

df = (
    pl.read_csv("balance-sheet.csv")
    .select(pl.exclude("Change", "Total"))
    .with_columns(pl.exclude("Date").str.replace_all("[,$]", ""))
    .select(
        "Notes",
        pl.col("Date").str.to_date("%-m/%-d/%Y"),
        pl.exclude("Date", "Notes").cast(pl.Decimal),
    )
)

non_date_cols = [c for c in df.columns if c not in frozenset(("Date", "Notes"))]

if df.drop("Notes").null_count().select(s=pl.sum_horizontal(pl.all())).row(
    0, named=True
) != {"s": 0}:
    raise AssertionError

with open("names.json") as f:
    asset_indicators = json.load(f)


asset_info = [
    {"name": col, "is_asset": col in asset_indicators["assets"]}
    for col in non_date_cols
]
date_info = [{"day": d} for d in df["Date"]]


async def main() -> None:
    async with Database("mysql+aiomysql://bernie:berniepw@db:3306") as db:
        # classes and dates
        await asyncio.gather(
            db.execute_many(query=POPULATE_CLASSES_STMT, values=asset_info),
            db.execute_many(query=POPULATE_DATES_STMT, values=date_info),
        )
        logging.info("populated classes and dates tables")

        rows_classes = await db.fetch_all(query="select id, name from finances.classes")
        class_ids = {r["name"]: r["id"] for r in rows_classes}

        rows_dates = await db.fetch_all(query="select id, day from finances.dates")
        dates_ids = {r["day"]: r["id"] for r in rows_dates}

        # amounts and comments
        amount_info = [
            [
                {
                    "day_id": dates_ids[r["Date"]],
                    "amount": r[c],
                    "class_id": class_ids[c],
                }
                for c in non_date_cols
            ]
            for r in df.iter_rows(named=True)
        ]
        flattened_amount_info = [entry for entries in amount_info for entry in entries]

        comment_info = [
            {"day_id": dates_ids[r["Date"]], "comments": r["Notes"]}
            for r in df.iter_rows(named=True)
        ]

        await asyncio.gather(
            db.execute_many(query=POPULATE_AMOUNTS_STMT, values=flattened_amount_info),
            db.execute_many(query=POPULATE_COMMENTS_STMT, values=comment_info),
        )
        logging.info("populated amounts and comments tables")


if __name__ == "__main__":
    asyncio.run(main())
