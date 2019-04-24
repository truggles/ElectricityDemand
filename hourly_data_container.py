



class HourlyDataContainer:
    """ Class that contains a single hour's electric demand.  
    It will contain info and flags as well

    # Info
    self.hour
    self.raw_demand # no substitutions or corrections
    self.demand

    # Flags
    self.outlier
    self.missing
    
    # Comparisons with previous and following points
    self.delta_previous
    self.delta_following
    """

    def __init__(self, hour, daily_hour, date, uct_time, demand):

        self.hour = hour

        ## Set local hour in region, value is reported in this format: "07/01/2015 1:00:00 AM" 
        #hour_info = local_hour.split(' ')
        #pm_adjust = 0 if hour_info[2] == 'AM' else 12
        #self.daily_hour = int(hour_info[1].split(':')[0]) + pm_adjust #- 1 # -1 for python list indexing
        self.daily_hour = int(daily_hour)
        if self.daily_hour > 24: self.daily_hour = 24 # Not sure why, but there are a few errors for date 11/05/2018
        self.month = int(date.split('/')[0])
        # CSV values greater than 1,000 are stored as strings with ',' that need removing
        self.raw_demand = demand.replace(',','')

        self.demand = self.raw_demand
        # Set missing data to a default value
        if self.demand == '':
            self.missing = True
            self.demand = '-99.99'
        else:
            self.missing = False

        self.demand = float(self.demand)

        # Defaults, these will be computed later
        self.outlier = False # Innocent until proven guilty
        self.deltas_valid = False # Must pass check before True
        self.delta_previous = -99.99
        self.delta_following = -99.99
        self.daily_avg = -99.99


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


    def set_outlier(is_outlier):

        assert(type(is_outlier) == type(True))

        self.outlier = is_outlier
        
        return

        
