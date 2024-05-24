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
    plot(data, names["assets"])
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


###### from https://developers.google.com/sheets/api/quickstart/python

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
SAMPLE_RANGE_NAME = "Class Data!A2:E"


    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("sheets", "v4", credentials=creds)

        sheet = service.spreadsheets()
        result = (
            sheet.values()
            .get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME)
            .execute()
        )
        values = result.get("values", [])

        for row in values:
            print(f"{row[0]}, {row[4]}")
    except HttpError as err:
        print(err)


######

if __name__ == "__main__":
    raise SystemExit(main())
