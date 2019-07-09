from hourly_data_container import HourlyDataContainer
import csv
import numpy as np
import helpers as helpers
from collections import OrderedDict
from simple_container import SimpleContainer


class RenewablesData :
    """ A class to store the hour-by-hour info for 
    renewable energy capacity factors. """


    def __init__(self, energy):

        assert(energy == 'solar' or energy == 'wind' or energy == 'windSmall'), "Choose 'solar' or 'wind' energy to load"

        self.hourly_data = []
        self.demand_position = 2 # Position of reported demand use
        self.uct_time_position = 1 # Position of UCT time in Dan's current EIA930_BALANCE_[year]_[monts].csv data 

        print ("Loading {}".format(energy))

        with open("data/{}_series_Lei_unnormalized.csv".format(energy), 'r') as f:
            info = list(csv.reader(f, delimiter=","))

        # Continue the hour notation at previous entry
        # and increment by 1 unless it's the first entry
        hour = 0
        for line in info:

            # Ensure demand is listed in expected column and
            # Skip header line
            if 'year' in line:
                if ('year' != line[0] or 'month' != line[1] or 'day' != line[2] 
                        or 'hour' != line[3] or 'capacity' not in line[4]):
                    print("Loading {} and columns are erroneously ordered".format(energy))
                    break
                continue


            # Initialize an HourlyDataContainer for this hour
            # Need to switch csv hour from 1-24 to 0-23
            uct_time = "{year:04d}{month:02d}{day:02d}T{hour:02d}Z".format(
                    year=int(line[0]), month=int(line[1]), day=int(line[2]), hour=int(line[3])-1)
            self.hourly_data.append( SimpleContainer(
                uct_time, float(line[4])) )
            hour += 1
