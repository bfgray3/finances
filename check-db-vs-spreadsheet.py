import polars as pl
from polars.testing import assert_frame_equal

URI = "mysql://bernie:berniepw@db:3306"
QUERY = """\
select d.day as Date,
  a.amount,
  cl.name,
  co.comments as Notes
from finances.amounts a
inner join finances.classes cl
  on a.class_id = cl.id
inner join finances.dates d
  on d.id = a.day_id
inner join finances.comments as co
  on d.id = co.day_id
"""

spreadsheet = (
    pl.read_csv("balance-sheet.csv")
    .select(pl.exclude("Change", "Total"))
    .with_columns(pl.exclude("Date").str.replace_all("[,$]", ""))
    .select(
        "Notes",
        pl.col("Date").str.to_date("%-m/%-d/%Y"),
        pl.exclude("Date", "Notes").cast(pl.Float64),
    )
)

db = pl.read_database_uri(query=QUERY, uri=URI).pivot(
    "name", index=("Date", "Notes"), values="amount"
)

assert_frame_equal(
    left=db,
    right=spreadsheet,
    check_row_order=False,
    check_column_order=False,
    check_dtypes=True,
    check_exact=True,
)
