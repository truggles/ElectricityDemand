import numpy as np
import datetime



class HourlyDataContainer:
    """ Class that contains a single hour's electric demand.  
    It will contain info and flags as well

    # Info
    self.hour
    self.daily_hour
    self.raw_demand # no substitutions or corrections
    self.demand

    # Flags
    self.outlier
    self.missing
    
    # Comparisons with previous and following points
    self.delta_previous
    self.delta_following

    # Different averages
    self.daily_avg
    self.centered_average
    self.centered_iqr_average
    self.demand_estimate
    self.demand_estimate_outlier
    """

    def __init__(self, hour, uct_time, demand):

        self.hour = hour

        ## Set local hour in region, value is reported in this format: "07/01/2015 1:00:00 AM" 
        #hour_info = local_hour.split(' ')
        #pm_adjust = 0 if hour_info[2] == 'AM' else 12
        #self.daily_hour = int(hour_info[1].split(':')[0]) + pm_adjust #- 1 # -1 for python list indexing
        uct = datetime.datetime.strptime(uct_time, '%Y%m%dT%HZ')
        self.uct_string = uct_time
        self.daily_hour = uct.hour
        self.month = uct.month
        self.demand = demand
        # Set missing data to a default value
        if self.demand == 'MISSING' or self.demand == 'EMPTY':
            self.missing = True
            self.demand = -99.99
        else:
            self.missing = False

        self.demand = float(self.demand)

        # Defaults, these will be computed later
        self.outlier = False # Innocent until proven guilty
        self.deltas_valid = False # Must pass check before True
        self.delta_previous = -99.99
        self.delta_following = -99.99
        self.daily_avg = -99.99
        self.centered_average = -99.99
        self.centered_iqr_average = -99.99
        self.demand_estimate = -99.99
        self.demand_estimate_outlier = False

    # Print all values
    def __str__(self):
        return ("HourlyDataContainer: hour %i, raw_demand %s, demand %.1f, missing %s, outlier %s, deltas_valid %s, delta_prev %.1f, delta_follow %.1f" % \
                (self.hour, self.raw_demand, self.demand, self.missing, self.outlier, self.deltas_valid, self. delta_previous, self.delta_following))

    # Compute demand deltas by comparing to previous and following hours
    def compute_deltas(self, previous_data, following_data):
        
        assert(type(previous_data) == type(self))
        assert(type(following_data) == type(self))

        # Check sequential
        assert(previous_data.hour + 1 == self.hour)
        assert(following_data.hour - 1 == self.hour)

        # Comparisons only valid if data is available
        if not previous_data.missing and not following_data.missing:
            self.deltas_valid = True
        else:
            self.deltas_valid = False
            return

        self.delta_previous = self.demand - previous_data.demand
        self.delta_following = self.demand - following_data.demand
        return


    def set_outlier(self, is_outlier):

        assert(type(is_outlier) == type(True))
        self.outlier = is_outlier
        return

        
    def set_centered_average(self, val):

        assert(type(val) == float or type(val) == np.float64)
        self.centered_average = val
        return


    def set_centered_iqr_average(self, val):

        assert(type(val) == float or type(val) == np.float64)
        self.centered_iqr_average = val
        return


    def set_demand_estimate(self, val):

        assert(type(val) == float or type(val) == np.float64)
        self.demand_estimate = val
        return


    def set_demand_estimate_outlier(self, outlier=True):

        assert(type(outlier) == type(True))
        self.demand_estimate_outlier = outlier
        return





