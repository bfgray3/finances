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

# TODO: __all__


class NamesDict(TypedDict):
    assets: list[str]
    liabilities: list[str]


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--csv", default="balance-sheet.csv")
    group.add_argument("--sheet")
    parser.add_argument("--names", default="names.json")
    args = parser.parse_args(argv)

    with open(args.names) as f:
        names = json.load(f)

    data = get_data(csv=args.csv, sheet=args.sheet, names=names)
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


def read_data(csv: str | None = None, sheet: str | None = None) -> pl.DataFrame:
    if not (csv is None) ^ (sheet is None):
        ...  # TODO
    if csv is not None:
        return pl.read_csv(csv)
    creds = prepare_creds()
    # error: Argument 1 to "read_data_from_google_sheets" has incompatible type "str | None"; expected "str"  [arg-type]
    return read_data_from_google_sheets(spreadsheet_id=sheet, creds=creds)


def get_data(csv: str | None, sheet: str | None, names: NamesDict) -> pl.DataFrame:
    data = read_data(csv=csv, sheet=sheet)
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
            f.write(creds.to_json())  # TODO: newline???
    return creds


def read_data_from_google_sheets(
    spreadsheet_id: str, creds: Credentials
) -> pl.DataFrame:
    # adapted from https://developers.google.com/sheets/api/quickstart/python
    try:
        result = (
            build("sheets", "v4", credentials=creds)
            .spreadsheets()
            .values()
            .get(spreadsheetId=spreadsheet_id)
            .execute()
        )
    except HttpError as err:
        print(err)  # TODO

    return result["values"]  # TODO: put in a df


if __name__ == "__main__":
    raise SystemExit(main())
