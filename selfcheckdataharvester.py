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
from datetime import datetime, timedelta, date # to compute delta of time slices.

# Transaction class contains the customer's transaction summary.
# Each transaction has a customer, and a series of transactions
# (history records) that have a definitive start and end time,
# and an idle time. This roughly corresponds with a record in 
# a/the database.
class Transaction:
    def __init__(self, user, time, delimiter='|'):
        self.user       = user
        self.start_time = time
        self.last_time  = time 
        self.stop_time  = time
        self.renewals = 0
        self.checkouts= 0
        self.checkins = 0
        self.d = delimiter
        
    ## Setters
    # param:  time of the transaction
    # return: none
    def set_renewals(self, time):
        self.last_time = time
        self.renewals += 1
    
    # param:  time of the transaction
    # return: none
    def set_checkouts(self, time):
        self.last_time = time
        self.checkouts += 1
        
    # param:  time of the transaction
    # return: none
    def set_checkins(self, time):
        self.last_time = time
        self.checkins += 1
    
    # Signals a transaction that it has ended.
    # param:  time of the transaction
    # return: none    
    def end_transaction(self, time):
        self.stop_time = time
    
    ## Getters
    # param:  none
    # return: count of the number of renewals in the local transaction collection.
    def get_renewals(self):
        return self.renewals
        
    # param:  none
    # return: count of the number of checkouts in the local transaction collection.
    def get_checkouts(self):
        return self.checkouts
        
    # param:  none
    # return: count of the number of checkins in the local transaction collection.
    def get_checkins(self):
        return self.checkins
        
    # param:  none
    # return: duration of idle-ness, how long the machine was idle before someone else used it in seconds.
    def get_idle_duration(self):
        """
        >>> t=Transaction('21221012345678', '20150102073840')
        >>> t.set_renewals('20150102073841')
        >>> t.set_checkouts('20150102073842')
        >>> t.set_checkins('20150102073845')
        >>> t.end_transaction('20150102073851')
        >>> print str(t.get_idle_duration())
        0:00:06
        """
        end   = datetime.strptime(self.stop_time, "%Y%m%d%H%M%S")
        start = datetime.strptime(self.last_time, "%Y%m%d%H%M%S")
        return (end - start)
    
    # param:  none
    # return: duration of transaction, how long the machine was idle before someone else used it in seconds.
    def get_transaction_duration(self):
        """
        >>> t=Transaction('21221012345678', '20150102073840')
        >>> t.set_renewals('20150102073841')
        >>> t.set_checkouts('20150102073842')
        >>> t.set_checkins('20150102073845')
        >>> t.end_transaction('20150102073850')
        >>> print str(t.get_idle_duration())
        0:00:05
        """
        start = datetime.strptime(self.start_time, "%Y%m%d%H%M%S")
        end   = datetime.strptime(self.last_time, "%Y%m%d%H%M%S")
        return (end - start)
        
    def __str__(self):
        """
        >>> t=Transaction('21221012345678', '20150102073840')
        >>> t.set_renewals('20150102073841')
        >>> t.set_checkouts('20150102073842')
        >>> t.set_checkins('20150102073845')
        >>> t.end_transaction('20150102073850')
        >>> print t
        21221012345678|2015-01-02 07:38:40|0:00:05|0:00:05|1|1|1|
        """
        ret_s = self.user + self.d + str(datetime.strptime(self.start_time, "%Y%m%d%H%M%S")) + self.d + str(self.get_transaction_duration()) + self.d + str(self.get_idle_duration()) + self.d + str(self.checkouts) + self.d + str(self.renewals) + self.d + str(self.checkins) + self.d
        return ret_s

# Station is a model of the self-checkout machine. It contains 
# transactions.
class Station:
    def __init__(self, name):
        self.name = name
        self.transactions = {}
        self.previous_transaction = None
    
    def _set_transaction_(self, user_id, timestamp, command):
        pass
            
        
    # Method to output station contents.
    # param:  none
    # return: none
    def show(self):
        pass
        
        
# The harvest class outputs aggregate results for transactions
# on self-check machines. The input looks like:
# E201501020703491702R|S05IYFWSIPCHKMNA4|UO21221022794249|
# E201501020703551702R|S08CVFWSIPCHKMNA4|UO21221022794249|
# E201501020703551702R|S11CVFWSIPCHKMNA4|UO21221022794249|
# E201501020703561702R|S14CVFWSIPCHKMNA4|UO21221022794249|
# E201501020704071702R|S18IYFWSIPCHKMNA4|UO21221010698170|
# E201501020704131702R|S21CVFWSIPCHKMNA4|UO21221010698170|
# E201501020738261702R|S28IYFWSIPCHKMNA4|UO21221018267523|
# E201501020738331702R|S40CVFWSIPCHKMNA4|UO21221018267523|
# E201501020738331702R|S43CVFWSIPCHKMNA4|UO21221018267523|
# E201501020738471698R|S14IYFWSIPCHKMNA1|UO21221002219449|
# E201501020738331702R|S40CVFWSIPCHKMNA4|UO21221018267523|
# ... 
# Within this data we need to output the following:
# station_library  = 'MNA'
# date_time        = '2015-01-02 07:03:49'
# user_command     = 'IY'=New Transaction, 'CV'=Checkout, 'RV'=renew items, 'EV'=Checkin
# session_duration = computed
# idle_duration    = computed
# user_id          = '21221018267523'
# chk_ins          = count
# chk_outs         = count
# renewals         = count
# station_id       = 'SIPCHKMNA1'
class Harvester:
    def __init__(self, debug=False):
        self.DEBUG = debug
        self.lineno = 1
        self.stations = {}
    
    # puts the date and time into a recognized format.
    # param:  field string like 'E201501020738471698R'
    def _get_datetime_(self, field):
        """
        >>> s='E201501020738471698R'
        >>> h=Harvester()
        >>> print h._get_datetime_(s)
        20150102073847
        """
        return field[1:15]
        
    # Captures the station library
    # param:  string like 'S05IYFWSIPCHKMNA4'
    # return: station library.
    def _get_station_lib_(self, field):
        """
        >>> s='S05IYFWSIPCHKMNA4'
        >>> h=Harvester()
        >>> print h._get_station_lib_(s)
        MNA
        """
        return field[13:16]
        
    # Captures the station library
    # param:  string like 'S05IYFWSIPCHKMNA4'
    # return: station library.
    def _get_station_id_(self, field):
        """
        >>> s='S05IYFWSIPCHKMNA4'
        >>> h=Harvester()
        >>> print h._get_station_id_(s)
        SIPCHKMNA4
        """
        return field[7:17]
        
    # Captures the User id
    # param:  string like 'UO21221022794249'
    # return: user id.
    def _get_user_id_(self, field):
        """
        >>> s='UO21221022794249'
        >>> h=Harvester()
        >>> print h._get_user_id_(s)
        21221022794249
        """
        return field[2:]
        
    # Captures the User's activity
    # param:  string like 'S05IYFWSIPCHKMNA4'
    # return: user id.
    def _get_user_command_(self, field):
        """
        >>> s='S05IYFWSIPCHKMNA4'
        >>> h=Harvester()
        >>> print h._get_user_command_(s)
        IY
        """
        return field[3:5]
        
    # Gets a named station, or if one doesn't exist 
    # creates one in the Stations dictionary and then returns it.
    # param:  name - string of the station name.
    # return: the named station.
    def _get_station_(self, name):
        try:
            return self.stations[name]
        except KeyError:
            self.stations[name] = Station(name)
            return self.stations[name]
            
    # This method parses a line that looks like:
    # 'E201501020703491702R|S05IYFWSIPCHKMNA4|UO21221022794249|'
    # param:  string line of pipe delimited fields as above.
    # return: ?
    def parse_line(self, line):
        # Get date time stamp
        fields = line.split('|')
        if len(fields) != 4:
            sys.stderr.write('*error on line ' + str(self.lineno) + ': "' + line + '"')
        self.lineno += 1
        timestamp   = self._get_datetime_(fields[0])
        station_lib = self._get_station_lib_(fields[1])
        station_id  = self._get_station_id_(fields[1])
        user_id     = self._get_user_id_(fields[2])
        command     = self._get_user_command_(fields[1])
        # That's all the simple data. Now we have to do some computation.
        # Since all the data is an aggregate of the user's session, and it 
        # is possible that other sessions for a given machine will be interupted
        # by history recordings from other checkouts, we need to organize the
        # data by station name.
        # session_duration = not sure yet.
        # idle_duration = not sure yet
        # chk_ins
        # chk_outs
        # renewals
        # But for now let's see if there is a station by this name and add the data to it and if not 
        # create one.
        station = self._get_station_(station_id)
        station._set_transaction_(user_id, timestamp, command)
    
    # Outputs the Stations
    # param:  none
    # return: none
    def to_string(self):
        for station in self.stations:
            station.show()
# Displays help message and always exits.
# param:  none
# return: none
def usage():
    sys.stderr.write('Usage: selfcheckdataharvester.py [-x] -i file\n')
    sys.stderr.write('  -i file input data file in format:\n')
    sys.stderr.write('  -x[h] This help message.\n')
    sys.exit()
    
if __name__ == "__main__":
    import doctest
    doctest.testmod()
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
    harvester = Harvester()
    for line in iFile.readlines():
        harvester.parse_line(line[:-1])
    iFile.close()

# EOF
