#!/usr/bin/python
# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
# Converts Pasaffe DB format to KeePassX XML.
### BEGIN LICENSE
# Copyright (C) 2014 Leandro Lucarella <llucax@gmail.com>
# Based on work by Jamie Strandboge <jamie@canonical.com> which was
# based on work by Marc Deslauriers <marc.deslauriers@canonical.com>
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 3, as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranties of
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.
### END LICENSE

import getpass
import sys
import os
import struct
import time
import xml.etree.ElementTree as et
from datetime import datetime
from optparse import OptionParser

import gettext
from gettext import gettext as _
gettext.textdomain('pasaffe')

# Add project root directory (enable symlink and trunk execution)
PROJECT_ROOT_DIRECTORY = os.path.abspath(
    os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0]))))

python_path = []
if os.path.abspath(__file__).startswith('/opt'):
    syspath = sys.path[:] # copy to avoid infinite loop in pending objects
    for path in syspath:
        opt_path = path.replace('/usr', '/opt/extras.ubuntu.com/pasaffe')
        python_path.insert(0, opt_path)
        sys.path.insert(0, opt_path)
if (os.path.exists(os.path.join(PROJECT_ROOT_DIRECTORY, 'pasaffe'))
    and PROJECT_ROOT_DIRECTORY not in sys.path):
    python_path.insert(0, PROJECT_ROOT_DIRECTORY)
    sys.path.insert(0, PROJECT_ROOT_DIRECTORY)
if python_path:
    os.putenv('PYTHONPATH', "%s:%s" % (os.getenv('PYTHONPATH', ''), ':'.join(python_path))) # for subprocesses

from pasaffe_lib import readdb

parser = OptionParser()
parser.add_option("-f", "--file", dest="filename",
                  help="specify alternate GPass database file", metavar="FILE")

(options, args) = parser.parse_args()

if os.environ.has_key('XDG_DATA_HOME'):
    db_filename = os.path.join(os.environ['XDG_DATA_HOME'], 'pasaffe/pasaffe.psafe3')
else:
    db_filename = os.path.join(os.environ['HOME'], '.local/share/pasaffe/pasaffe.psafe3')

if options.filename != None:
    db_filename = options.filename

if not os.path.exists(db_filename):
    sys.stderr.write("\n\nERROR: Could not locate database file!\n")
    sys.exit(1)

sys.stderr.write("WARNING: this will display all password entries.\n")

count = 0
max_tries = 3
while count < max_tries:
    count += 1
    master = getpass.getpass("Password> ")
    try:
        passfile = readdb.PassSafeFile(db_filename, master)
        break
    except ValueError:
        sys.stderr.write("Sorry, try again.\n")

    if count >= max_tries:
        sys.stderr.write("%d incorrect password attempts.\n" % (count))
        sys.exit(1)

db = et.Element('database')
grp = et.SubElement(db, 'group')
et.SubElement(grp, 'title').text = 'Pasaffe'
et.SubElement(grp, 'icon').text = '51'

for record in sorted(passfile.records, key=lambda entry: entry[3].lower()):
    def field(label, default=''):
        d = dict(
            title    = 3,
            username = 4,
            comment  = 5,
            password = 6,
            url      = 13, # a lock
        )
        return record.get(d[label], default).decode('UTF-8')

    entry = et.SubElement(grp, 'entry')
    et.SubElement(entry, 'title').text = field('title') or field('url')
    et.SubElement(entry, 'username').text = field('username')
    et.SubElement(entry, 'password').text = field('password')
    et.SubElement(entry, 'url').text = field('url')
    et.SubElement(entry, 'comment').text = field('comment')
    et.SubElement(entry, 'icon').text = '51' # a lock
    now = datetime.now().isoformat()
    for n in 'creation lastaccess lastmod'.split():
        et.SubElement(entry, n).text = now
    et.SubElement(entry, 'expire').text = 'Never'

sys.stdout.write('<!DOCTYPE KEEPASSX_DATABASE>\n')
xml_tree = et.ElementTree(db)
xml_tree.write(sys.stdout, xml_declaration=False, encoding='UTF-8')
