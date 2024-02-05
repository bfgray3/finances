## finances

this is an in-progress tool to track my personal finances.

## usage

```bash
pip install .
finances
```

the `finances` tool has the following cli:
```
usage: main.py [-h] [--csv CSV] [--names NAMES]

options:
  -h, --help     show this help message and exit
  --csv CSV
  --names NAMES
```

in the working directory there should be two files:
* a csv...
* a json file with the names of which columns are assets and which are liabilities


```json
{
    "assets": ["Savings", "Checking"],
    "liabilities": ["SomeLoan"]
}
```
