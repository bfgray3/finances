import json

import polars as pl
import seaborn.objects as so

with open("names.json") as f:
    names = json.load(f)


def read_data() -> pl.DataFrame:
    return (
        pl.read_csv("balance-sheet.csv")
        .select(
            pl.col("Date").str.to_date("%m/%d/%Y"),
            pl.exclude("Date", "Total", "Change", "Notes")
            .str.replace_all("[$,]", "")
            .cast(pl.Float64),  # str.to_decimal() messes up converting to pandas
        )
        .with_columns(
            Total=pl.sum_horizontal(pl.exclude("Date", *names["liabilities"]))
            - pl.sum_horizontal(pl.col(names["liabilities"]))
        )
        .with_columns(
            PctChange=pl.col("Total").pct_change(),
            Change=pl.col("Total").diff(),
        )
    )


if __name__ == "__main__":
    data = read_data()
    so.Plot(data, "Date", "Total").add(so.Line()).save("total")
    so.Plot(data, "Date", "Change").add(so.Line()).save("change")

    (
        so.Plot(
            data.melt(
                id_vars="Date",
                value_vars=names["assets"],
            ),
            "Date",
            "value",
            color="variable",
        ).add(so.Area(), so.Stack())
    ).save("stacked")
