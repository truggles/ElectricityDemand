from hourly_data_container import HourlyDataContainer
import csv
from numpy import percentile


class DemandData :
    """ A class to store the hour-by-hour info for 
    electric demand.  It will contain info and flags indicating
    relevant info for each hour of demand data """


    def __init__(self, region, year):

        self.region = region
        self.year = year
        self.hourly_data = []
        self.demand_position = 6 # Position of reported demand use in Dan's current EIA930_BALANCE_[year]_[monts].csv data 

        print (self.region, self.year)

        with open("EIA_demand_data/EIA930_BALANCE_%s_Jan_Jun.csv" % self.year, 'r') as f:
            info1 = list(csv.reader(f, delimiter=","))
        with open("EIA_demand_data/EIA930_BALANCE_%s_Jul_Dec.csv" % self.year, 'r') as f:
            info2 = list(csv.reader(f, delimiter=","))

        # Continue the hour notation at previous entry
        # and increment by 1 unless it's the first entry
        hour = 0
        for info in [info1, info2]:
            for line in info:

                # Ensure demand is listed in expected column and
                # Skip header line
                if 'Balancing Authority' in line:
                    if line[self.demand_position] != 'Demand (MW)':
                        print ("\n\nDemand listed in unexpected column: region %s, year %s. Break\n\n" % (self.region, self.year))
                        break
                    continue
                # Make sure to match region of interest
                if line[0] != self.region:
                    continue

                # Initialize an HourlyDataContainer for this hour
                self.hourly_data.append( HourlyDataContainer(hour, line[self.demand_position]) )
                hour += 1

        # For all hourly data, make delta comparisons
        # Skip first and last hours
        for i in range(1, len(self.hourly_data)-1):
            self.hourly_data[i].compute_deltas(self.hourly_data[i-1], self.hourly_data[i+1])

        print ("Length of hourly data: %i" % len(self.hourly_data))


    # Currently using a modified IQR method with much broader range.
    # This currently only targets single hour outliers where the
    # delta is large compared to the previous and following hour.
    # Skip analyzing previous or following if they are 'missing'
    def find_hourly_outliers(self):

        x = [d.delta_previous for d in self.hourly_data if not d.missing]
        if len(x) > 0:
            q05 = percentile(x, 5)
            q95 = percentile(x, 95)
            iqr = q95 - q05
            
            cut_off = iqr * 1.5
            lower = q05 - cut_off
            upper = q95 + cut_off

            for d in self.hourly_data:
                if ((d.delta_previous < lower or d.delta_previous > upper) and 
                        (d.delta_following < lower or d.delta_following > upper) and
                        d.deltas_valid):
                    d.outlier = True


    # Calculate the 24 hour running average for each hour.
    # This should give insight into how large of an effect multi-day
    # weather patters are. Missing data is treated as a gap in data
    # instead of -99.99. 
    # Skip outliers.
    def compute_daily_averages(self):

        twenty_four_hours = []
        for d in self.hourly_data:
            # Add new value
            if len(twenty_four_hours) < 24:
                to_append = d.demand if not d.outlier else -99.99
                twenty_four_hours.append(to_append)
            total = 0.
            n_good_hours = 0
            if len(twenty_four_hours) == 24:
                for h in twenty_four_hours:
                    if h != -99.99:
                        total += h
                        n_good_hours += 1
                # Pop off oldest hourly value
                twenty_four_hours.pop(0)
            if n_good_hours > 0:
                d.daily_avg = total / n_good_hours
            else:
                d.daily_avg = 0.
            if len(twenty_four_hours) >= 24:
                print ("Error, len == %i" % len(twenty_four_hours))







