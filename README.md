# TBP Membership Calculator

Simple python script for calculating TBP's membership classes.

## Dependencies
- `Python 3.4` or above

## Usage

`calc_membership_status.py [-h] [-c CONFIG] [-p PREADJUSTMENT_OUT] input output`

Calculates Active/DA/PA Statuses from TBP website hours `input` CSV. Outputs a file to `output` with delta values for each requirement.
Delta values indicate the difference between the required hour credits and earned hour credits. A negative delta indicates an unmet requirement.

Supply a config `.json` to manipulate requirements for the supplied CSV, as requirements can be different for different members. Four stock
configurations are supplied in this repo.

Supply a preadjustment `preadjustment_out` CSV to output requirement deltas prior to the service hour adjustment, where missing requirements are
alternatively fulfilled by extra service hours.

```
positional arguments:
  input                 input csv from TBP website to read from
  output                output csv to write delta values to

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        supplied configuration for requirements
  -p PREADJUSTMENT_OUT, --preadjustment_out PREADJUSTMENT_OUT
                        writes delta values before service-hours adjustment to csv
```

Example: `python3 calc_membership_status.py ActiveProgress.csv ActiveDeltas.csv -c active.json -p ActivePreadjust.csv`
