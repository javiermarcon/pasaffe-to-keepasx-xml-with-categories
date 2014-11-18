# Converts Password Exporter Firefox Plugin CSV to KeePassX XML.

import sys
import csv

print '''\
<!DOCTYPE KEEPASSX_DATABASE>
<database>
 <group>
  <title>Firefox</title>
  <icon>8</icon>'''

keys = 'hostname username password submit realm ufield pfield'.split()

sys.stdin.readline() # comment
sys.stdin.readline() # headers
for r in csv.reader(sys.stdin, delimiter=',', quotechar='"'):
    entry = dict()
    for i, k in enumerate(keys):
        entry[k] = r[i]
    print '''\
  <entry>
   <title>{hostname}</title>
   <username>{username}</username>
   <password>{password}</password>
   <url>{hostname}</url>
   <comment>{realm}</comment>
   <icon>3</icon>
   <creation>2014-11-17T23:55:00</creation>
   <lastaccess>2014-11-17T23:55:00</lastaccess>
   <lastmod>2014-11-17T23:55:00</lastmod>
   <expire>Never</expire>
  </entry>'''.format(**entry)

print '''\
 </group>
</database>
'''