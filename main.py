import polars as pl


def read_data() -> pl.DataFrame:
    return pl.read_csv("balance-sheet.csv").select(
        pl.col("Date").str.to_date("%m/%d/%Y"),
        pl.exclude("Date", "Total", "Change", "Notes")
        .str.replace_all("[$,]", "")
        .str.to_decimal(),
    )


print(read_data())
print(read_data().columns)
