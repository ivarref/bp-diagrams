#!/usr/bin/python

import json
import sys
from sets import Set
from pprint import pprint

def load_json(fil):
  with open(fil) as f:
    return json.load(f)

countrycodes = {}
countrycodes['BP_OECD'] = 'OECD'
countrycodes['BP_NONOECD'] = 'Non OECD'
countrycodes['BP_EU2'] = 'Eurozone'
countrycodes['BP_FSU'] = 'Total Former Soviet Union'
countrycodes['BP_TAF'] = 'Total Africa'
countrycodes['BP_TAP'] = 'Total Asia-Pacific'
countrycodes['BP_TEE'] = 'Total Europe and Eurasia'
countrycodes['BP_TME'] = 'Total Middle East'
countrycodes['BP_TNA'] = 'Total North America'
countrycodes['BP_TSCA'] = 'Total South and Central America'
countrycodes['BP_WORLD'] = 'World'

for entry in load_json('data/slim-2.json'):
  countrycodes[entry['alpha-2']] = entry['name']

# Goal:
# bp country code friendly lookup table for population

population_lookup = {}
gdp_lookup = {}

def to_cc3(names):
  cc3_data = load_json('data/slim-3.json')
  result = []
  for name in names:
    matches = [code for code in cc3_data if name.lower() == code['name'].lower()]
    if len(matches) != 1:
      raise ValueError('Could not find ' + name + " results was: " + str(matches))
    else:
      result.append(matches[0]['alpha-3'])
  return verify(result)
    
def verify(cc3_names):
  cc3_data = load_json('data/slim-3.json')
  cc3_codes = [x['alpha-3'] for x in cc3_data]
  missing = [x for x in cc3_names if not x in cc3_codes]
  if len(missing) > 0:
    raise ValueError('Missing some country codes: ' + str(missing))
  else:
    return cc3_names

c2_to_c3 = {}
cc2 = load_json('data/slim-2.json')
cc3 = load_json('data/slim-3.json')

for c2 in cc2:
  matches = [x for x in cc3 if x['name'] == c2['name']]
  if len(matches)!=1:
    raise ValueError('Could not find ' + str(c2))
  else:
    c2_to_c3[c2['alpha-2']] = matches[0]['alpha-3']
    
ignoregroups = ['BP_OAF', 'BP_OAP', 'BP_OEE', 'BP_OME', 'BP_OSCA', 'BP_TEU', 'BP_FSU']
ignoregroups.append('TW') # Ignore Taiwan, don't have population data

c2_to_c3['BP_EU2'] = 'EMU'
c2_to_c3['BP_OECD'] = 'OED'
c2_to_c3['BP_TNA'] = 'NAC'
c2_to_c3['BP_TSCA'] = 'LCN'
c2_to_c3['BP_WORLD'] = 'WLD'

from decimal import Decimal

new_groups = {}
def define_group(group_name, cc3s):
  for x in cc3s:
    vals = []
    if x in new_groups:
      vals = new_groups[x]
    if group_name in vals:
      continue
    vals.append(group_name)
    new_groups[x] = vals

#former soviet union
fsu = to_cc3([x.strip().lower() for x in "Armenia| Azerbaijan| Belarus| Estonia| Georgia| Kazakhstan| Kyrgyzstan| Latvia| Lithuania| Moldova, Republic of| Russian Federation| Tajikistan| Turkmenistan| Ukraine| Uzbekistan".split("|")])
define_group('BP_FSU', fsu)
# total africa
define_group('BP_TAF', verify([x.strip() for x in "DZA, AGO, SHN, BEN, BWA, BFA, BDI, CMR, CPV, CAF, TCD, COM, COG, DJI, EGY, GNQ, ERI, ETH, GAB, GMB, GHA, GNB, GIN, CIV, KEN, LSO, LBR, LBY, MDG, MWI, MLI, MRT, MUS, MYT, MAR, MOZ, NAM, NER, NGA, STP, REU, RWA, STP, SEN, SYC, SLE, SOM, ZAF, SHN, SDN, SWZ, TZA, TGO, TUN, UGA, COD, ZMB, TZA, ZWE, SSD, COD".split(",")]))


# asia pacific
define_group('BP_TAP', to_cc3([x.strip().lower() for x in "Brunei Darussalam| Cambodia| China| Hong Kong| Indonesia| Japan| Lao People's Democratic Republic| Macao| Malaysia| Mongolia| Korea, Republic of| Philippines| Singapore| Afghanistan| Bangladesh| India| Myanmar| Nepal| Pakistan| Sri Lanka| Korea, Democratic People's Republic of| Taiwan, Province of China| Thailand| Viet Nam| Australia| New Zealand| Papua New Guinea".split("|")]))
define_group('BP_TAP', verify([x.strip() for x in "ASM, AUS, NZL, COK, FJI, PYF, GUM, KIR, MNP, MHL, FSM, UMI, NRU, NCL, NZL, NIU, NFK, PLW, PNG, MNP, SLB, TKL, TON, TUV, VUT, UMI, WLF, WSM, TLS".split(",")]))

# Europe & Eurasia
# TODO add kosovo?
europe_cc3 = verify([x.strip() for x in "ALB, AND, AUT, BLR, BEL, BIH, BGR, HRV, CYP, CZE, DNK, EST, FRO, FIN, FRA, DEU, GIB, GRC, HUN, ISL, IRL, ITA, LVA, LIE, LTU, LUX, MKD, MLT, MDA, MCO, NLD, NOR, POL, PRT, ROU, RUS, SMR, SRB, SVK, SVN, ESP, SWE, CHE, UKR, GBR, VAT, IMN, MNE".split(",")])
define_group('BP_TEE', europe_cc3)
define_group('BP_TEE', fsu)

# Middle east
define_group('BP_TME', to_cc3([x.strip().lower() for x in "Yemen| Oman| Qatar| Bahrain| Kuwait| Saudi Arabia| Iran, Islamic Republic of| Iraq| Israel| Jordan| Lebanon| Syrian Arab Republic".split("|")]))


for x in load_json('data/population.json'):
  cc = x['Country Code'] 
  year = x['Year']
  key = cc + "-" + year
  value = Decimal(x['Value'])
  population_lookup[key] = value
  if cc in new_groups:
    for group in new_groups[cc]:
      group_key = group + "-" + year
      group_value = Decimal(0)
      if group_key in population_lookup:
        group_value = population_lookup[group_key]
      population_lookup[group_key] = group_value + value

for x in load_json('data/gdp.json'):
  cc = x['Country Code'] 
  year = x['Year']
  key = cc + "-" + year
  value = Decimal(x['Value'])
  gdp_lookup[key] = value
  if cc in new_groups:
    for group in new_groups[cc]:
      group_key = group + "-" + year
      group_value = Decimal(0)
      if group_key in gdp_lookup:
        group_value = gdp_lookup[group_key]
      gdp_lookup[group_key] = group_value + value

for k in [x for x in population_lookup.keys() if x.startswith('WLD-')]:
  year = k.split('-')[1]

  wld_value = population_lookup[k]
  oed_value = population_lookup['OED-' + year]
  population_lookup['BP_NONOECD-' + year] = wld_value - oed_value

  wld_value = gdp_lookup[k]
  oed_value = gdp_lookup['OED-' + year]
  gdp_lookup['BP_NONOECD-' + year] = wld_value - oed_value

files =[
"data/BP_coal_consumption_mtoe.csv",
"data/BP_gas_consumption_mtoe.csv",
"data/BP_hydro_consumption_mtoe.csv", 
"data/BP_nuclear_consumption_mtoe.csv", 
"data/BP_oil_consumption_mtoe.csv", 
"data/BP_other_renewables_consumption_mtoe.csv",
"data/BP_solar_consumption_mtoe.csv",
"data/BP_wind_consumption_mtoe.csv",
"data/BP_co2_emissions.csv"]

resources = ['coal', 'gas', 'hydro', 'nuclear', 'oil', 'other_renewables', 'solar', 'wind', 'co2']

def skip_headers(fd):
  while (fd.readline().strip() != ""):
    continue
  return True

def production_key(group, resource, year):
  return group + "-" + resource + "-" + year

production = {}

prodfiles = ["data/BP_coal_production_mtoe.csv", 
"data/BP_oil_production_mtoe.csv",
"data/BP_gas_production_mtoe.csv"]

for f in prodfiles:
  seengroups = []
  fd = open(f, 'r')
  skip_headers(fd)
  fields = [x[1:-1] for x in fd.readline().strip().split(",")]
  groups = fields[1:]
  resource = f.split('BP_')[1].split('_')[0]
  for line in fd.readlines():
    line = line.strip()
    parts = line.split(",")
    for (idx,group) in enumerate(groups):
      value = None
      try:
        value = Decimal(parts[idx+1])
      except:
        if group in seengroups:
          if group == 'BP_FSU':
            continue
          raise ValueError('Group %s already seen, but had NA in data...' % (group))
      if value != None:
        if group not in seengroups:
          seengroups.append(group)
        production[production_key(group, resource, parts[0])] = value
  fd.close()

fds = [open(f, 'r') for f in files]

[skip_headers(fd) for fd in fds]

fields = [x[1:-1] for x in fds[0].readline().strip().split(",")]
groups = fields[1:]

print groups

[fd.readline() for fd in fds[1:]] # skip groups

seengroups = []

output_filename = "data/data.tsv"
group_filter_fn = lambda x: True

if "--filter" in sys.argv:
  output_filename = 'data/country/' + sys.argv[-1] + '.tsv'
  group_filter_fn = lambda x: x == sys.argv[-1]

with open(output_filename, 'w') as out:
  out.write("year\tcountry\tcountry_code\tpopulation\tgdp\t%s\tcoal_production\toil_production\tgas_production\n" % ("\t".join(resources)))
  while True:
    lines = [fd.readline().strip() for fd in fds]
    if not lines[0]:
      break
    years = [line.split(",")[0] for line in lines]
    lengths_ok = 1 == len(Set([len(line.split(",")) for line in lines]))
    if (not lengths_ok) or len(Set(years)) != 1:
      raise ValueError('Oops.')
    for group in groups:
      year = years[0]
      if group in ignoregroups:
        continue
      #print "Process group %s for year %s" % (group, year)
      idx = fields.index(group)
      groupdata = [line.split(",")[idx] for line in lines]
      gd = []
      for d in groupdata:
        if d == '"na"':
          d = "0"
        gd.append(d)
      groupdata = gd
      #if '"na"' in groupdata and len(Set(groupdata))==1 and (group in seengroups) and group=='BP_FSU' and year >= '1985':
        #continue
      #if '"na"' in groupdata and len(Set(groupdata))==1 and (group in seengroups):
        #raise ValueError("Missing data for seen group %s and year %s" % (group, year))
      #if '"na"' in groupdata and len(Set(groupdata))==1:
        #print "Skipping group %s for year %s" % (group, year)
        #continue
      #if '"na"' in groupdata and len(Set(groupdata))==2 and '0.0' in groupdata:
        #print "Skipping group %s for year %s" % (group, year)
        #continue
      #if '"na"' in groupdata and len(Set(groupdata))>1:
        #print "group is %s, year is %s" % (group, year)
        #print "groupdata: %s" % (str(groupdata))
        #raise ValueError('Oops.')
      group_sum = [Decimal(x) for x in groupdata]
      if Decimal(0) == sum(group_sum) and group not in seengroups:
        continue # drop data starting with zero
      #print 'seen group %s' % (group)
      #print groupdata
      seengroups.append(group)
      translated_key = group # default to no translation
      if group in c2_to_c3:
        translated_key = c2_to_c3[group]

      # search backwards in population data if missing data
      keys = [translated_key + "-" + str(int(year)-x) for x in range(0, 5)]
      gdp_key = translated_key + "-" + str(int(year))
      matches = [key for key in keys if key in population_lookup]
      if len(matches)==0:
        raise ValueError("Missing keys [" + str(keys) + "] group was " + group)
      key = matches[0]
      gdp = "NA"
      if gdp_key in gdp_lookup:
        gdp = gdp_lookup[gdp_key]
      #key_gdp = matches_gdp[0]
      def get_production(resource_type):
        prod_key = production_key(group, resource_type, year)
        if prod_key in production:
          return production[prod_key]
        else:
          return 0
      if (group_filter_fn(group)):
        print "writing row for group %s for year %s" %  (group, year)
        out.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (year, countrycodes[group], group, population_lookup[key], gdp, "\t".join(groupdata), get_production('coal'), get_production('oil'), get_production('gas')))

[fd.close() for fd in fds]


