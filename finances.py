import argparse
import json
import os.path
from collections.abc import Sequence
from typing import TypedDict

import polars as pl
import seaborn.objects as so
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

__all__ = ("get_data", "plot")


class NamesDict(TypedDict):
    assets: list[str]
    liabilities: list[str]


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    # TODO: need to handle # rows to skip
    parser.add_argument("--src")
    parser.add_argument("--names", default="names.json")
    args = parser.parse_args(argv)

    with open(args.names) as f:
        names = json.load(f)

    data = get_data(src=args.src, names=names)
    plot(df=data, asset_names=names["assets"])
    return 0


def plot(df: pl.DataFrame, asset_names: list[str]) -> None:
    so.Plot(df, "Date", "Change").add(so.Line()).scale(
        y=so.Continuous().label(like="${x:,g}")
    ).save("change")
    so.Plot(df, "Date", "PctChange").add(so.Line()).scale(
        y=so.Continuous().label(like="{x:.0%}")
    ).label(y="Percent change").save("pct-change")

    (
        so.Plot(
            df.melt(
                id_vars="Date",
                value_vars=asset_names,
            ),
            "Date",
            "value",
            color="variable",
        )
        .add(so.Area(alpha=0.9), so.Stack())
        .scale(
            y=so.Continuous().label(like="${x:,g}"),
        )
        .label(color="Asset class", y="Amount")
    ).save("stacked", bbox_inches="tight")


def read_data(src: str) -> pl.DataFrame:
    if src.endswith(".csv"):
        return pl.read_csv(src)
    creds = prepare_creds()
    return read_data_from_google_sheets(sheet=src, creds=creds)


def get_data(src: str, names: NamesDict) -> pl.DataFrame:
    data = read_data(src=src)
    return (
        data.select(
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


def prepare_creds(
    token_file: str = "token.json",
    creds_file: str = "credentials.json",
    scopes: tuple[str, ...] = (
        "https://www.googleapis.com/auth/spreadsheets.readonly",
    ),
) -> Credentials:
    # adapted from https://developers.google.com/sheets/api/quickstart/python
    if existing_creds := os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, scopes)
    if not existing_creds or not creds.valid:
        if existing_creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_file, scopes)
            creds = flow.run_local_server(port=0)
        with open(token_file, "w") as f:
            f.write(creds.to_json())
            f.write("\n")
    return creds


def read_data_from_google_sheets(sheet: str, creds: Credentials) -> pl.DataFrame:
    # adapted from https://developers.google.com/sheets/api/quickstart/python
    try:
        result = (
            build("sheets", "v4", credentials=creds)
            .spreadsheets()
            .values()
            .get(spreadsheetId=sheet)
            .execute()
        )
    except HttpError as e:
        raise RuntimeError("error reading Google sheet") from e

    return result["values"]  # TODO: put in a df


if __name__ == "__main__":
    raise SystemExit(main())
