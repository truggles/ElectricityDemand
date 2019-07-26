import pandas as pd
import numpy as np
import csv
import subprocess
import os
from glob import glob
from shutil import copy2



# Use Pandas to retrieve the output values b/c it handles
# fully populated tables well
def get_cap_and_costs(path, file_name):
    return get_all_cap_and_costs(path+'/'+file_name)

def get_all_cap_and_costs(file_name):
    dta = pd.read_csv(file_name,
                   dtype={
                        'case name':np.str,
                        'problem status':np.str,
                        'system cost ($/kW/h)':np.float64,
                        'capacity natgas (kW)':np.float64,
                        'capacity solar (kW)':np.float64,
                        'capacity wind (kW)':np.float64,
                        'dispatch unmet demand (kW)':np.float64,
                       })

    return dta


# Use normal python csv functions b/c this is a sparsely populated
# csv file
def get_SEM_csv_file(file_name):

    with open(file_name, 'r') as f:
        info = list(csv.reader(f, delimiter=","))
    
    return info


# For nat gas, this is added after initial optimization sets cap values.
# It needs to add a new field to the case file
def set_cap_natgas(cfg, cap_natgas):

    new_cfg = []

    cnt = 1
    for line in cfg:
        if cnt == 134:
            line.append('CAPACITY_NATGAS')
        if cnt == 136:
            line.append(cap_natgas)
        cnt += 1
        new_cfg.append(line)

    return new_cfg


# For nat gas, this is added after initial optimization sets cap values.
# It needs to add a new field to the case file
def set_var_cost_unmet_demand(cfg, cost_unmet):

    new_cfg = []

    cnt = 1
    for line in cfg:
        if cnt == 136:
            line[29] = cost_unmet
        cnt += 1
        new_cfg.append(line)

    return new_cfg

# These can be set for each and every run
def set_vals(cfg, case_name, start_year, end_year, cap_solar, cap_wind):

    new_cfg = []

    cnt = 1
    for line in cfg:
        if cnt == 136:
            line[0] = case_name
            line[1] = start_year
            line[3] = end_year
            line[27] = cap_wind
            line[28] = cap_solar
            print(line)
        cnt += 1
        new_cfg.append(line)

    return new_cfg

def write_file(file_name, cfg):

    with open(file_name, 'w') as f:
        for line in cfg:
            to_write = ''
            for val in line:
                to_write += str(val)+','
            f.write(to_write+'\n')
        f.close()


def get_output_file_names(path):

    files = glob(path+'*.csv')
    if len(files) > 1:
        print("Too many files: {}".format(files))
    return files

def get_results(files):

    results = {}

    keys = []
    for f in files:
        info = get_all_cap_and_costs(f)
        keys.append(info['case name'].values[0])
        results[info['case name'].values[0]] = [
                       info['problem status'].values[0],
                       info['system cost ($/kW/h)'].values[0],
                       info['capacity natgas (kW)'].values[0],
                       info['capacity solar (kW)'].values[0],
                       info['capacity wind (kW)'].values[0],
                       info['dispatch unmet demand (kW)'].values[0]
        ]

    keys = sorted(keys)
    print('case name,problem status,system cost ($/kW/h),capacity natgas (kW),capacity solar (kW),capacity wind (kW),dispatch unmet demand (kW)')
    for key in keys:
        to_print = ''
        for info in results[key]:
            to_print += str(info)+','
        print(key, to_print)

if '__main__' in __name__:

    reliability_values = [0.0000, 0.0001, 0.0003, 0.001, 0.01, 0.1]
    wind_values = [0.0, 0.25, 0.5, 0.75, 1.0]
    solar_values = [0.0, 0.25, 0.5, 0.75, 1.0]
    years = {
            '15-16' : [2015, 2016],
            '16-17' : [2016, 2017],
            '17-18' : [2017, 2018],
    }

    input_file = 'y_case_input_base_190716.csv'
    path = 'Output_Data/tests_Jul25_v1'
    results = path+'/results'

    #for reliability in reliability_values:
    #    for solar in solar_values:
    #        for wind in wind_values:

    #            solar_str = 'solar_'+str(round(solar,2)).replace('.','p')
    #            wind_str = 'wind_'+str(round(wind,2)).replace('.','p')
    #            reliability_str = 'rel_'+str(round(reliability,4)).replace('.','p')

    #            # 1st Step
    #            cfg = get_SEM_csv_file(input_file)
    #            case_name = reliability_str+'_'+wind_str+'_'+solar_str+'_15-16'
    #            case_file = case_name+'.csv'
    #            cfg = set_vals(cfg, case_name, 2015, 2016, solar, wind)
    #            cfg = set_var_cost_unmet_demand(cfg, 0.0)
    #            write_file(case_file, cfg)
    #            os.environ["UNMET_DEMAND_SET_VALUE"] = str(reliability)
    #            subprocess.call(["python", "Simple_Energy_Model.py", case_file])

    #            files = get_output_file_names(path+'/tests_Jul25_v1_2019')

    #            # Copy output file
    #            if not os.path.exists(results):
    #                os.makedirs(results)
    #            copy2(files[-1], results)

    #            # Read results
    #            f_name = files[-1].split('/')[-1]
    #            dta = get_cap_and_costs(path, f_name)

    #            # Get new copy of SEM cfg
    #            case_name = reliability_str+'_'+wind_str+'_'+solar_str+'_16-17'
    #            case_file = case_name+'.csv'
    #            cfg = get_SEM_csv_file(input_file)
    #            cfg = set_vals(cfg, case_name, 2016, 2017, solar, wind)
    #            cfg = set_var_cost_unmet_demand(cfg, 1.0)
    #            cfg = set_cap_natgas(cfg, float(dta['capacity natgas (kW)']))
    #            write_file(case_file, cfg)

    #            # Delete results files
    #            os.remove(files[-1])
    #            
    #            os.environ["UNMET_DEMAND_SET_VALUE"] = "999"
    #            subprocess.call(["python", "Simple_Energy_Model.py", case_file])


    #            # 2nd set results, Copy output file, Delete results files
    #            files = get_output_file_names(path+'/tests_Jul25_v1_2019')
    #            copy2(files[-1], results)
    #            os.remove(files[-1])


    #            # Get new copy of SEM cfg
    #            case_name = reliability_str+'_'+wind_str+'_'+solar_str+'_17-18'
    #            case_file = case_name+'.csv'
    #            cfg = get_SEM_csv_file(input_file)
    #            cfg = set_vals(cfg, case_name, 2017, 2018, solar, wind)
    #            cfg = set_var_cost_unmet_demand(cfg, 1.0)
    #            cfg = set_cap_natgas(cfg, float(dta['capacity natgas (kW)']))
    #            write_file(case_file, cfg)
    #            subprocess.call(["python", "Simple_Energy_Model.py", case_file])

    #            # 3rd set results, Copy output file, Delete results files
    #            files = get_output_file_names(path+'/tests_Jul25_v1_2019')
    #            copy2(files[-1], results)
    #            os.remove(files[-1])

    files = get_output_file_names(results+'/tests_Jul25_v1_2019')
    get_results(files)
