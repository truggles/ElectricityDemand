import numpy as np
from collections import OrderedDict


# Return high and low IQR threshold for given val
def percentiles(x, val):
    q_a, q_b = np.percentile(x, val), np.percentile(x, 100-val)
    return [q_a, q_b]

# An ordered dict with the months and their start and stop month
# roughly corresponding to seasons
def get_time_slice_thresholds(time_slice_choice=0): 
    assert(time_slice_choice in [0, 1, 2, 3]), "time_slice_choice=%i, 0 = only annual, 1 = seasonal, 2 = monthly w/ +/- 1 month for averaging, 3 = monthly" % time_slice_choice

    time_slices = OrderedDict()
    # season : min, max month
    if time_slice_choice==0:
        time_slices['Annual'] = [1, 12]
    elif time_slice_choice==1:
        time_slices['Winter'] = [1, 3]
        time_slices['Spring'] = [4, 6]
        time_slices['Summer'] = [7, 9]
        time_slices['Fall'] = [10, 12]
    # +/- 1 month for larger avg
    elif time_slice_choice==2:
        time_slices['January'] = [12, 2]
        time_slices['February'] = [1, 3]
        time_slices['March'] = [2, 4]
        time_slices['April'] = [3, 5]
        time_slices['May'] = [4, 6]
        time_slices['June'] = [5, 7]
        time_slices['July'] = [6, 8]
        time_slices['August'] = [7, 9]
        time_slices['September'] = [8, 10]
        time_slices['October'] = [9, 11]
        time_slices['November'] = [10, 12]
        time_slices['December'] = [11, 1]
    # month for larger avg
    elif time_slice_choice==3:
        time_slices['January'] = [1, 1]
        time_slices['February'] = [2, 2]
        time_slices['March'] = [3, 3]
        time_slices['April'] = [4, 4]
        time_slices['May'] = [5, 5]
        time_slices['June'] = [6, 6]
        time_slices['July'] = [7, 7]
        time_slices['August'] = [8, 8]
        time_slices['September'] = [9, 9]
        time_slices['October'] = [10, 10]
        time_slices['November'] = [11, 11]
        time_slices['December'] = [12, 12]
    return time_slices

# Print "normal" average and average based only on values within defined IQR range
def check_avgs(x, val, name='', verbose=False):
    q_vals = percentiles(x, val)
    x_iqr = [val for val in x if (val > q_vals[0] and val < q_vals[1])]
    if len(x_iqr) == 0:
        return np.average(x), 0.
    if verbose:
        print ("%15s Average: %.1f     IQR %i Average: %.1f    IQR Low: %.1f   IQR High: %.1f" 
                % (name, np.average(x), val, np.average(x_iqr), q_vals[0], q_vals[1]))
    return np.average(x), np.average(x_iqr)

# Loop check_avgs for 5 seasonal scenarios
def check_seasonal_avgs(hourly_data, val, time_slice_choice=0):
    assert(time_slice_choice in [0, 1, 2, 3]), "time_slice_choice=%i, 0 = only annual, 1 = seasonal, 2 = monthly w/ +/- 1 month for averaging, 3 = monthly" % time_slice_choice
    time_slices = get_time_slice_thresholds(time_slice_choice)
    for time_slice in time_slices.keys():
        x = [d.demand for d in hourly_data if (not d.missing and 
                (d.month >= time_slices[time_slice][0] and d.month <= time_slices[time_slice][1]))]
        check_avgs(x, val, time_slice, True)

# Get associated season with monthly input
def month_num_to_season_str(month):
    assert(month in range(1, 13))
    if month in [1, 2, 3]: return 'Winter'
    if month in [4, 5, 6]: return 'Spring'
    if month in [7, 8, 9]: return 'Summer'
    if month in [10, 11, 12]: return 'Fall'

# Get associated season with monthly input
def month_num_to_month_str(month):
    assert(month in range(1, 13))

    if month == 1: return 'January'
    if month == 2: return 'February'
    if month == 3: return 'March'
    if month == 4: return 'April'
    if month == 5: return 'May'
    if month == 6: return 'June'
    if month == 7: return 'July'
    if month == 8: return 'August'
    if month == 9: return 'September'
    if month == 10: return 'October'
    if month == 11: return 'November'
    if month == 12: return 'December'


