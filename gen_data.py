

import ipdb
from glob import glob
from sets import Set

#desired format:
#year, group_code, coal, gas, hydro

files = [f for f in glob("data/*consumption*.csv")]
resources = [f.split('2014_')[1].split('_consumption')[0] for f in files]

fds = [open(f, 'r') for f in files]

print "year\tcountry_code\t%s" % ("\t".join(resources))

# skip headers
for fd in fds:
  while (fd.readline().strip() != ""):
    continue

fields = [x[1:-1] for x in fds[0].readline().strip().split(",")]
groups = fields[1:]

[fd.readline() for fd in fds[1:]] # skip groups

seengroups = []

while True:
  lines = [fd.readline().strip() for fd in fds]
  if not lines[0]:
    break
  years = [line.split(",")[0] for line in lines]
  lengths_ok = 1 == len(Set([len(line.split(",")) for line in lines]))
  if (not lengths_ok) or len(Set(years)) != 1:
    raise Error('Oops.')
  for group in groups:
    idx = fields.index(group)
    groupdata = [line.split(",")[idx] for line in lines]
    if '"na"' in groupdata and len(Set(groupdata))==1 and (group in seengroups):
      raise Error('Oops.')
    if '"na"' in groupdata and len(Set(groupdata))==1:
      continue
    if '"na"' in groupdata and len(Set(groupdata))>1:
      raise Error('Oops.')
    seengroups.append(group)
    print "%s\t%s\t%s" % (years[0], group, "\t".join(groupdata))

[fd.close() for fd in fds]

