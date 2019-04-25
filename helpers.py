import numpy as np
from collections import OrderedDict


# Return high and low IQR threshold for given val
def percentiles(x, val):
    q_a, q_b = np.percentile(x, val), np.percentile(x, 100-val)
    return [q_a, q_b]

# An ordered dict with the months and their start and stop month
# roughly corresponding to seasons
def get_seasons_thresholds(do_all_seasons=False): 
    seasons = OrderedDict()
    # season : min, max month
    seasons['Annual'] = [1, 12]
    if do_all_seasons:
        seasons['Winter'] = [1, 3]
        seasons['Spring'] = [4, 6]
        seasons['Summer'] = [7, 9]
        seasons['Fall'] = [10, 12]
    return seasons

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
def check_seasonal_avgs(hourly_data, val, do_all_seasons=False):
    seasons = get_seasons_thresholds(do_all_seasons)
    for season in seasons.keys():
        x = [d.demand for d in hourly_data if (not d.missing and 
                (d.month >= seasons[season][0] and d.month <= seasons[season][1]))]
        check_avgs(x, val, season, True)

    
