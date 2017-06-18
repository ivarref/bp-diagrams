#!/usr/bin/env python3

import csv
import sys

def tsv2map(f):
    res = []
    with open(f) as csvfile:
        rdr = csv.reader(csvfile, delimiter='\t')
        header = []
        for (idx, row) in enumerate(rdr):
            if (idx == 0):
                header = row
                continue
            if (len(header) != len(row)):
                print("bad data!")
                sys.exit(1)
            dictrow = dict(zip(header, row))
            res.append(dictrow)
    return res

country_codes = set([x['country_code'] for x in tsv2map('data/data.tsv')])

for cc in country_codes:
    if "--cmd" in sys.argv:
        print("./gen_data.py --filter %s" % (cc))
    else:
        print(cc)
