## finances

this is an in-progress tool to track my personal finances.

## usage

```console
$ pip install .
$ finances
usage: finances [-h] [--src SRC] [--names NAMES]

options:
  -h, --help     show this help message and exit
  --src SRC      source for the data. can be a Google sheet or a local CSV
  --names NAMES  JSON file with the names of which columns are assets and which are liabilities
```

in the working directory there should be two files:
* a csv (by default `balance-sheet.csv`) ...
* a json file (by default `names.json`) with the names of which columns are assets and which are liabilities

```json
{
    "assets": ["Savings", "Checking"],
    "liabilities": ["SomeLoan"]
}
```
