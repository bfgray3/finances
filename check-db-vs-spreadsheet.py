import polars as pl

QUERY = """\
select a.day,
  a.amount,
  c.name
from finances.amounts a
inner join finances.classes c
  on a.class_id = c.id
"""

URI = "mysql://bernie:berniepw@db:3306"

spreadsheet = pl.read_csv("balance-sheet.csv")
db = (
    pl.read_database_uri(query=QUERY, uri=URI)
    .pivot("name", index="day", values="amount")
    .rename({"day": "Date"})
)

pl.testing.assert_frame_equal(
    left=db,
    right=spreadsheet,
    check_row_order=False,
    check_column_order=False,
    check_dtypes=True,
    check_exact=True,
    # rtol=1e-05,
    # atol=1e-08,
)
