#!/bin/bash

set -ex

cd data

./pull-population.py
./explode_csv.py population.csv population.json

./pull-gdp.py
./explode_csv.py gdp.csv gdp.json

cd ..
./gen_data.py

