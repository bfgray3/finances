import polars as pl
from polars.testing import assert_frame_equal

URI = "mysql://bernie:berniepw@db:3306"
QUERY = """\
select a.day,
  a.amount,
  c.name
from finances.amounts a
inner join finances.classes c
  on a.class_id = c.id
"""

spreadsheet = (
    pl.read_csv("balance-sheet.csv")
    .select(pl.exclude("Notes", "Change", "Total"))
    .with_columns(pl.exclude("Date").str.replace_all("[,$]", ""))
    .select(
        pl.col("Date").str.to_date("%-m/%-d/%Y"), pl.exclude("Date").cast(pl.Float64)
    )
)

db = (
    pl.read_database_uri(query=QUERY, uri=URI)
    .pivot("name", index="day", values="amount")
    .rename({"day": "Date"})
)

assert_frame_equal(
    left=db,
    right=spreadsheet,
    check_row_order=False,
    check_column_order=False,
    check_dtypes=True,
    check_exact=True,
)
