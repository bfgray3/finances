import polars as pl


def read_data() -> pl.DataFrame:
    return (
        pl.read_csv("balance-sheet.csv")
        .select(
            pl.col("Date").str.to_date("%m/%d/%Y"),
            pl.exclude("Date", "Total", "Change", "Notes")
            .str.replace_all("[$,]", "")
            .str.to_decimal(),
        )
        .with_columns(
            Total=pl.sum_horizontal(pl.exclude("StudentLoans", "CreditCards", "Date"))
            - pl.sum_horizontal(pl.col(["StudentLoans", "CreditCards"]))
        )
        .with_columns(
            PctChange=pl.col("Total").pct_change().alias("PctChange"),
            Change=pl.col("Total").diff(),
        )
    )


print(read_data())
print(read_data().columns)
