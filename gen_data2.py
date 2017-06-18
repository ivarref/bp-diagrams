#!/usr/bin/env python3

import sys
import csv
import json
from decimal import Decimal

def skip_headers(fd):
    while fd.readline().strip() != "":
        continue
    return True

def load_json(fil):
    with open(fil) as f:
        return json.load(f)

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

def get_c3_to_c2_map():
    res = {}
    cc2 = load_json('data/slim-2.json')
    cc3 = load_json('data/slim-3.json')

    for c2 in cc2:
        matches = [x for x in cc3 if x['name'] == c2['name']]
        if len(matches)!=1:
            raise ValueError('Could not find ' + str(c2))
        else:
            c3 = matches[0]['alpha-3']
            res[c3] = c2['alpha-2']
    return res

c3_to_c2 = get_c3_to_c2_map()

coal = csv2map_from_bp_csv('data/BP_coal_consumption_mtoe.csv', 'coal')
oil = csv2map_from_bp_csv('data/BP_oil_consumption_mtoe.csv', 'oil')
gas = csv2map_from_bp_csv('data/BP_gas_consumption_mtoe.csv', 'gas')
nuclear = csv2map_from_bp_csv('data/BP_nuclear_consumption_mtoe.csv', 'nuclear')
hydro = csv2map_from_bp_csv('data/BP_hydro_consumption_mtoe.csv', 'hydro')
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
                if k in country_codes or k == 'YEAR' or k == 'TYPE' or k.startswith('BP_'):
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
    wb_data = [('data/population.json', 'population'), ('data/gdp.json', 'gdp')]
    for (fil, typ) in wb_data:
        for row in load_json(fil):
            cc = row['Country Code']
            year = row['Year']
            if cc in c3_to_c2:
                values.append({"group": c3_to_c2[cc],
                               "year": year,
                               "type": typ,
                               "value": row['Value']})
    return values

flat_values = get_flat_values()

def data_group_year(group, year):
    properties = dict([(x['type'], x['value']) for x in flat_values if x['year'] == str(year) and x['group'] == group])
    properties['group'] = group
    properties['year'] = str(year)
    return properties

# def make_group(group):
#     print("Making group %s ..." % (group))
#     vals = []
#     for year in range(1965, 1+max([int(x['year']) for x in flat_values])):
#         properties = dict([(x['type'], x['value']) for x in flat_values if x['year'] == str(year) and x['group'] == group])
#         properties['group'] = group
#         properties['year'] = str(year)
#         expected_properties = ['coal', 'oil', 'gas', 'hydro', 'nuclear', 'renewables', 'coal_prod', 'gas_prod', 'oil_prod', 'gdp', 'population', 'co2']
#         missing_properties = [x for x in expected_properties if not x in properties.keys()]
#         if len(missing_properties) > 0:
#             print("Group %s year %s => missing %d properties => %s" % (group, str(year), len(missing_properties), str(missing_properties)))
#         vals.append(properties)
#     return vals
    #print("Making group %s ... year %s => %s" % (group, year, str(len(properties.keys()))))

print(data_group_year('IQ', '2016'))

#import ipdb; ipdb.set_trace()
print(get_country_codes())

