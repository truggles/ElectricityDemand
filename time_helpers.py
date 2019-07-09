import numpy as np
import helpers
from collections import OrderedDict

# Calculate the annaul averages for each year in our data.
# Some means will not include a full year
def calculate_annaul_averages(hourly_data):
    years = OrderedDict()
    # Get list of all years
    # First value in list tracks number of hours for that year
    # in the data
    for hour in hourly_data:
        if not hour.datetime.year in years.keys():
            years[hour.datetime.year] = [1, hour.value]
        else:
            years[hour.datetime.year][0] += 1
            years[hour.datetime.year][1] += hour.value


    # Add mean values
    for year, vals in years.items():
        vals.append(vals[1]/vals[0])
        if vals[0] < 8760:
            print("WARNING: you are using calculate_annaul_averages with \
                    partial data for year {}".format(year))
    
    return years

# Adjust demand based on annual averages derived from
# calculate_annaul_averages()
def normalize_to_annual_averages(annual_info, hourly_data):
    for hour in hourly_data:
        hour.set_value(hour.value / annual_info[hour.datetime.year][2])


# Scale demand based on monthly averages derived from
# calculate_monthly_averages()
def normalize_to_monthly_averages(monthly_vals, hourly_data):

    # Calc mean for each month over all years
    monthly_means = {}
    for month in range(1, 13):
        monthly_means[month] = [0, 0.]

    for year, month_info in monthly_vals.items():
        for month, val in month_info.items():
            monthly_means[helpers.month_str_to_month_num(month)][0] += 1
            monthly_means[helpers.month_str_to_month_num(month)][1] += val

    for month, vals in monthly_means.items():
        vals.append(vals[1]/vals[0])
        print(month, vals)

    # Normalize based on monthly mean across all years
    for hour in hourly_data:
        hour.set_value(hour.value / monthly_means[hour.datetime.month][2])



# Calculate the seasonal averages for the whole data range
def calculate_seasonal_averages(hourly_data):
    seasons = OrderedDict()
    seasons['Winter'] = [1, 2, 3]
    seasons['Spring'] = [4, 5, 6]
    seasons['Summer'] = [7, 8, 9]
    seasons['Fall'] = [10, 11, 12]

    data_dict = helpers.get_years_in_data(hourly_data)
    for year in data_dict.keys():
        data_dict[year] = OrderedDict()
        for season in seasons.keys():
            data_dict[year][season] = []

    # Loop over all hours and add their demand to the appropriate year and season
    for hour in hourly_data:
        for season, months in seasons.items():
            if hour.month in months:
                data_dict[hour.datetime.year][season].append(hour.value)
                break
    
    # Replace lists with mean value before returning
    for year, seasons in data_dict.items():
        for season in seasons.keys():
            data_dict[year][season] = float(np.mean(data_dict[year][season]))
    return data_dict

# Calculate the monthly averages for the whole data range
def calculate_monthly_averages(hourly_data):
    months = OrderedDict()
    months[1] = 'January'
    months[2] = 'February'
    months[3] = 'March'
    months[4] = 'April'
    months[5] = 'May'
    months[6] = 'June'
    months[7] = 'July'
    months[8] = 'August'
    months[9] = 'September'
    months[10] = 'October'
    months[11] = 'November'
    months[12] = 'December'

    data_dict = helpers.get_years_in_data(hourly_data)
    for year in data_dict.keys():
        data_dict[year] = OrderedDict()
        for month, name in months.items():
            data_dict[year][name] = []

    # Loop over all hours and add their demand to the appropriate year and season
    for hour in hourly_data:
        data_dict[hour.datetime.year][months[hour.datetime.month]].append(hour.value)
    
    # Replace lists with mean value before returning
    for year, months_names in data_dict.items():
        for month in months_names.keys():
            data_dict[year][month] = float(np.mean(data_dict[year][month]))
    return data_dict


# Preps the variance plot info based on output from
# calculate_monthly_averages()
def info_for_monthly_variance(monthly_vals):
    months_means = {}
    for year, month_info in monthly_vals.items():
        for month, info in month_info.items():
            months_means[month] = [0., 0]
        break
    for year, month_info in monthly_vals.items():
        for month, info in month_info.items():
            months_means[month][0] += info
            months_means[month][1] += 1
    for month, vals in months_means.items():
        vals.append(vals[0] / vals[1])
    to_hist_months = []
    
    for year, month_info in monthly_vals.items():
        for month, info in month_info.items():
            to_hist_months.append(info/months_means[month][2])
    return to_hist_months


# Create average 24 hour demand curves for each week
# averaged over multiple years
def get_hourly_info_per_week(hourly_data):

    # Need both for averaging
    hourly_demand_values = np.zeros((52,24))
    hourly_demand_entries = np.zeros((52,24))

    # Fill and get number of entries
    for hour in hourly_data:
        try:
            hourly_demand_values[hour.datetime.isocalendar()[1] - 1][hour.datetime.hour - 1] += hour.value
            hourly_demand_entries[hour.datetime.isocalendar()[1] - 1][hour.datetime.hour - 1] += 1
        except IndexError:
            if hour.datetime.isocalendar()[1] == 53:
                hourly_demand_values[51][hour.datetime.hour - 1] += hour.value
                hourly_demand_entries[51][hour.datetime.hour - 1] += 1

    # Average
    for week in range(52):
        for hour in range(24):
            hourly_demand_values[week][hour] = hourly_demand_values[week][hour] / hourly_demand_entries[week][hour]

    return hourly_demand_values



