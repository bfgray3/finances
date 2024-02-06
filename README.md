## finances

this is an in-progress tool to track my personal finances.

## usage

```console
$ pip install .
$ finances
usage: main.py [-h] [--csv CSV] [--names NAMES]

options:
  -h, --help     show this help message and exit
  --csv CSV
  --names NAMES
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
