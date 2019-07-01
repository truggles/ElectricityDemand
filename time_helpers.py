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
            years[hour.datetime.year] = [1, []]
        else:
            years[hour.datetime.year][0] += 1


    # Loop over all hours and add their demand to the appropriate year
    for hour in hourly_data:
        for year, vals in years.items():
            if hour.datetime.year == year:
                vals[1].append(hour.value)

    # Add mean values
    for year, vals in years.items():
        vals.append(np.mean(vals[1]))
        if vals[0] < 8760:
            print("WARNING: you are using calculate_annaul_averages with \
                    partial data for year {}".format(year))
    
    return years

## Adjust demand based on annual averages derived from
## calculate_annaul_averages()
#def normalize_to_annual_averages(self, annual_info):
#    for hour in self.hourly_data:
#        hour.set_demand(hour.value / annual_info[hour.datetime.year][2])


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
