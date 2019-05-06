from hourly_data_container import HourlyDataContainer
import csv
import numpy as np
import helpers as helpers
from collections import OrderedDict


class DemandData :
    """ A class to store the hour-by-hour info for 
    electric demand.  It will contain info and flags indicating
    relevant info for each hour of demand data """


    def __init__(self, region, year):

        self.region = region
        self.year = year
        self.hourly_data = []
        self.demand_position = 6 # Position of reported demand use in Dan's current EIA930_BALANCE_[year]_[monts].csv data 
        self.uct_time_position = 4 # Position of UCT time in Dan's current EIA930_BALANCE_[year]_[monts].csv data 
        self.hour_position = 2 # Position of local daily hour use in Dan's current EIA930_BALANCE_[year]_[monts].csv data 
        self.date_position = 1 # Position of local date in Dan's current EIA930_BALANCE_[year]_[monts].csv data 

        self.n_hours_surrounding = 24 # Default to do 24 hrs prior and post for running avgs
        self.hourly_demand = OrderedDict() # Can be filled later with set_hourly_demand
        self.hourly_demand_avgs = OrderedDict() # Can be filled later with set_hourly_demand

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
                    if line[self.uct_time_position] != 'UTC Time at End of Hour':
                        print ("\n\nUTC Time at End of Hour listed in unexpected column: region %s, year %s. Break\n\n" % (self.region, self.year))
                        break
                    if line[self.date_position] != 'Data Date':
                        print ("\n\nData Date listed in unexpected column: region %s, year %s. Break\n\n" % (self.region, self.year))
                        break
                    if line[self.hour_position] != 'Hour Number':
                        print ("\n\nHour listed in unexpected column: region %s, year %s. Break\n\n" % (self.region, self.year))
                        break
                    continue
                # Make sure to match region of interest
                if line[0] != self.region:
                    continue

                # Initialize an HourlyDataContainer for this hour
                self.hourly_data.append( HourlyDataContainer(hour, 
                    line[self.hour_position],
                    line[self.date_position],
                    line[self.uct_time_position],
                    line[self.demand_position]) )
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
            q05 = np.percentile(x, 5)
            q95 = np.percentile(x, 95)
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



    def compute_hour_centered_averages(self, iqr_val=25):

        n_hours = len(self.hourly_data)

        # Make list of all hours with missing as -99.99
        running_hours = []
        for d in self.hourly_data:
            if not d.missing:
                running_hours.append(d.demand)
            else:
                running_hours.append(-99.99)

        # Loop over list and compute avgs and iqr avgs
        assert(n_hours == len(running_hours))
        for i in range(len(running_hours)):
            # fill with dummy val if we don't have full range requested
            if i < self.n_hours_surrounding or i > n_hours - self.n_hours_surrounding:
                self.hourly_data[i].set_centered_average(0.)
                self.hourly_data[i].set_centered_iqr_average(0.)
                continue

            # demand for the hours surrounding the current hour giving 2 * self.n_hours_surrounding total
            # +1 extends to n past the current hour
            surrounding_vals = running_hours[i - self.n_hours_surrounding : i + self.n_hours_surrounding] 
            assert(len(surrounding_vals) == 2*self.n_hours_surrounding)

            # Remove missing values
            new_vals = []
            for val in surrounding_vals:
                if val != -99.99:
                    new_vals.append(val) 

            if len(new_vals)>0:
                avg, iqr_avg = helpers.check_avgs(new_vals, iqr_val)
                self.hourly_data[i].set_centered_average(avg)
                self.hourly_data[i].set_centered_iqr_average(iqr_avg)
            else:
                self.hourly_data[i].set_centered_average(0.)
                self.hourly_data[i].set_centered_iqr_average(0.)


    # Create average 24 hour demand curves for different time slices
    # 0 = only annual
    # 1 = seasonal
    # 2 = monthly w/ +/- 1 month for averaging
    def set_hourly_demand(self, time_slice_choice=0, include_outliers=False):
        assert(time_slice_choice in [0, 1, 2, 3]), "time_slice_choice=%i, 0 = only annual, 1 = seasonal, 2 = monthly w/ +/- 1 month for averaging, 3 = monthly" % time_slice_choice

        time_slices = helpers.get_time_slice_thresholds(time_slice_choice)
        hourly_demand_entries = OrderedDict()

        # Initialize to zeros
        for time_slice in time_slices.keys() :
            self.hourly_demand[time_slice] = np.zeros(24)
            hourly_demand_entries[time_slice] = np.zeros(24)  # For averaging

        # Fill and get number of entries
        for d in self.hourly_data:
            if d.missing: continue
            if d.outlier: 
                if not include_outliers:
                    continue
            for time_slice in time_slices.keys() :
                if d.month >= time_slices[time_slice][0] and d.month <= time_slices[time_slice][1]:
                    self.hourly_demand[time_slice][d.daily_hour-1] += d.demand
                    hourly_demand_entries[time_slice][d.daily_hour-1] += 1

        # Average
        for time_slice in time_slices.keys() :
            for i in range(len(self.hourly_demand[time_slice])):
                self.hourly_demand[time_slice][i] = self.hourly_demand[time_slice][i] / hourly_demand_entries[time_slice][i]

        # Set time_slice specific averages
        for time_slice in time_slices.keys() :
            self.hourly_demand_avgs[time_slice] = np.average(self.hourly_demand[time_slice])



    # Use self.hourly_demand[time_slices][24 hours] to set info for each demand hour
    # for expected usage
    def set_24_hourly_demand(self):
        assert(len(self.hourly_demand) > 0), "You must first call set_hourly_demand to build the self.hourly_demand dict"

        time_slice_map = {}
        if 'Annual' in self.hourly_demand.keys():
            for i in range(1, 13):
                time_slice_map[i] = 'Annual'
        elif 'Winter' in self.hourly_demand.keys():
            time_slice_map[1] = 'Winter'
            time_slice_map[2] = 'Winter'
            time_slice_map[3] = 'Winter'
            time_slice_map[4] = 'Spring'
            time_slice_map[5] = 'Spring'
            time_slice_map[6] = 'Spring'
            time_slice_map[7] = 'Summer'
            time_slice_map[8] = 'Summer'
            time_slice_map[9] = 'Summer'
            time_slice_map[10] = 'Fall'
            time_slice_map[11] = 'Fall'
            time_slice_map[12] = 'Fall'
        elif 'January' in self.hourly_demand.keys():
            time_slice_map[1] = 'January'
            time_slice_map[2] = 'February'
            time_slice_map[3] = 'March'
            time_slice_map[4] = 'April'
            time_slice_map[5] = 'May'
            time_slice_map[6] = 'June'
            time_slice_map[7] = 'July'
            time_slice_map[8] = 'August'
            time_slice_map[9] = 'September'
            time_slice_map[10] = 'October'
            time_slice_map[11] = 'November'
            time_slice_map[12] = 'December'
        else:
            print ("Did not align..., set_24_hourly_demand in demand_data.py")
            return

        # For each hour, map the month to the time slice name.
        # Grab the associated self.hourly_demand for that time slice and set it.
        for d in self.hourly_data:
            val = self.hourly_demand[time_slice_map[d.month]][d.daily_hour-1]
            val -= self.hourly_demand_avgs[time_slice_map[d.month]]
            val += d.centered_iqr_average
            d.set_demand_estimate(val)

            if d.hour<self.n_hours_surrounding: continue # b/c no 48 hour centered avg for the first and last day
            if d.hour>(365*24)-self.n_hours_surrounding: continue
            if ((d.demand - d.demand_estimate)/d.demand)<-0.5 or \
                    ((d.demand - d.demand_estimate)/d.demand)>0.5:
                d.set_demand_estimate_outlier(True)



