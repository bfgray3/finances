import argparse
import json
from collections.abc import Sequence
from typing import TypedDict

import polars as pl
import seaborn.objects as so


class NamesDict(TypedDict):
    assets: list[str]
    liabilities: list[str]


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", default="balance-sheet.csv")
    parser.add_argument("--names", default="names.json")
    args = parser.parse_args(argv)

    with open(args.names) as f:
        names = json.load(f)

    data = read_data(args.csv, names)
    so.Plot(data, "Date", "Total").add(so.Line()).save("total")
    so.Plot(data, "Date", "Change").add(so.Line()).save("change")
    so.Plot(data, "Date", "PctChange").add(so.Line()).save("pct-change")

    (
        so.Plot(
            data.melt(
                id_vars="Date",
                value_vars=names["assets"],
            ),
            "Date",
            "value",
            color="variable",
        )
        .add(so.Area(), so.Stack())
        .label(color="Asset class")
    ).save("stacked", bbox_inches="tight")
    return 0


def read_data(csv: str, names: NamesDict) -> pl.DataFrame:
    return (
        pl.read_csv(csv)
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
    raise SystemExit(main())
