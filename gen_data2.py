#!/usr/bin/env python3

import sys
import csv

def skip_headers(fd):
    while fd.readline().strip() != "":
        continue
    return True

def csv2map_from_bp_csv(fil, property):
    fd = open(fil)
    skip_headers(fd)
    rdr = csv.reader(fd)
    header = []
    res = []
    for (idx, row) in enumerate(rdr):
        if idx == 0:
            header = row
            continue
        if len(header) != len(row):
            print("bad data for file %s!" % (fil))
            sys.exit(1)
        dictrow = dict(zip(header, row))
        dictrow['TYPE'] = property
        res.append(dictrow)
    fd.close()
    return res

coal = csv2map_from_bp_csv('data/BP_coal_consumption_mtoe.csv', 'coal')
gas = csv2map_from_bp_csv('data/BP_gas_consumption_mtoe.csv', 'gas')
hydro = csv2map_from_bp_csv('data/BP_hydro_consumption_mtoe.csv', 'hydro')
nuclear = csv2map_from_bp_csv('data/BP_nuclear_consumption_mtoe.csv', 'nuclear')
oil = csv2map_from_bp_csv('data/BP_oil_consumption_mtoe.csv', 'oil')
renewables = csv2map_from_bp_csv('data/BP_other_renewables_consumption_mtoe.csv', 'renewables')
co2 = csv2map_from_bp_csv('data/BP_co2_emissions.csv', 'co2')

coal_prod = csv2map_from_bp_csv('data/BP_coal_production_mtoe.csv', 'coal_prod')
gas_prod = csv2map_from_bp_csv('data/BP_gas_production_mtoe.csv', 'gas_prod')
oil_prod = csv2map_from_bp_csv('data/BP_oil_production_mtoe.csv', 'oil_prod')

all_items = [coal, gas, hydro, nuclear, oil, renewables, co2, coal_prod, gas_prod, oil_prod]

def get_country_codes():
    country_codes = []
    for item in all_items:
        for row in item:
            for k in row.keys():
                if k in country_codes or k == 'YEAR' or k == 'TYPE':
                    continue
                else:
                    country_codes.append(k)
    country_codes.sort()
    return country_codes

def get_flat_values():
    values = []
    for item in all_items:
        for row in item:
            for k in row.keys():
                if k == 'YEAR' or k == 'TYPE':
                    continue
                else:
                    cc = k
                    v = row[k]
                    yr = row['YEAR']
                    typ = row['TYPE']
                    values.append({"group": cc,
                                    "year": yr,
                                    "type": typ,
                                    "value": v})
    return values

flat_values = get_flat_values()
import ipdb; ipdb.set_trace()
print(get_country_codes())

