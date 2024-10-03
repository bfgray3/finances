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

for row in df.iter_rows(named=True):
    # TODO: insert into the various tables
    print(row)
