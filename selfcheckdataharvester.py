#!/usr/bin/env python
####################################################
#
# Python source for project selfcheckdataharvester.
#
# Parses Symphony history logs into database-ready data.
#    Copyright (C) 2015  Andrew Nisbet
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.
#
# Author:  Andrew Nisbet, Edmonton Public Library
# Created: Tue Feb 3 08:02:35 MST 2015
# Rev: 
#          0.0 - Dev. 
#
####################################################

import sys
import getopt
import os

def usage():
    sys.stderr.write('Usage: selfcheckdataharvester.py [-x] -i file\n')
    sys.stderr.write('  -i file input data file in format:\n')
    sys.stderr.write('  -x[h] This help message.\n')
    sys.exit()
    
if __name__ == "__main__":
    # import doctest
    # doctest.testmod()
    inputFile = ''
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hi:x", ["ifile="])
    except getopt.GetoptError:
        usage();
    for opt, arg in opts:
        if opt in ( "-i", "--ifile" ):
            inputFile = arg
        elif opt == '-h':
            usage();
    sys.stderr.write('running file ' + inputFile + '\n')
    if os.path.isfile(inputFile) == False:
        sys.stderr.write('**error: input file "' + inputFile + '" does not exist.\n')
        sys.exit()
    if os.path.getsize(inputFile) == 0:
        sys.stderr.write('**error: input file "' + inputFile + '" is empty.\n')
        sys.exit()
    # Now down to business...
    iFile = open(inputFile, 'r')
    for line in iFile.readlines():
        sys.stderr.write('>>>' + line)
        # top_ten.parse_line(line[:-1])
    iFile.close()

# EOF
