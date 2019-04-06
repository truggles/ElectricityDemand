



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

    def __init__(self, hour, demand):

        self.hour = hour
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

        
