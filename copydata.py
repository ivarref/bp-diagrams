#!/usr/bin/python

from glob import glob
import os

for f in glob('../EnergyExportDatabrowser/StaticData/*mtoe.csv'):
  basname = os.path.basename(f)
  basname = basname.replace('_2015_', '_')
  if basname == 'BP_renewables_consumption_mtoe.csv':
    basname = 'BP_other_renewables_consumption_mtoe.csv'
  data_file = os.path.join('data', basname)

  if os.path.exists(data_file):
    print "cp -v %s %s" % (f, data_file)
  else:
    print f

