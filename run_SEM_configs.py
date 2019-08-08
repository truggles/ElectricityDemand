import pandas as pd
import numpy as np
import csv
import subprocess
import os
from glob import glob
from shutil import copy2
from collections import OrderedDict



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
        print("This many files were found matching {}*.csv: {}".format(path, len(files)))
    return files

def get_results(files):

    results = {}

    keys = []
    for f in files:
        info = get_all_cap_and_costs(f)
        keys.append(info['case name'].values[0])
        results[info['case name'].values[0]] = [
                       info['problem status'].values[0],
                       float(info['case name'].values[0].split('_')[1].replace('p','.')), # reliability value
                       info['system cost ($/kW/h)'].values[0],
                       info['capacity natgas (kW)'].values[0],
                       info['capacity solar (kW)'].values[0],
                       info['capacity wind (kW)'].values[0],
                       info['dispatch unmet demand (kW)'].values[0]
        ]

    print('Writing results to "Results.txt"')
    ofile = open('Results.txt', 'w')
    keys = sorted(keys)
    ofile.write('case name,problem status,target reliability,system cost ($/kW/h),capacity natgas (kW),capacity solar (kW),capacity wind (kW),dispatch unmet demand (kW)\n')
    for key in keys:
        to_print = ''
        for info in results[key]:
            to_print += str(info)+','
        ofile.write("{},{}\n".format(key, to_print))
    ofile.close()
    return results

# Get info from file, so we don't have to repeat get_results
# many many times
def simplify_results(results_file, reliability_values, wind_values, solar_values):
    ifile = open(results_file, 'r')

    simp = {}
    for reliability in reliability_values:
        simp[reliability] = {}
        for solar in solar_values:
            simp[reliability][solar] = {}
            for wind in wind_values:
                simp[reliability][solar][wind] = [0.0, 0]

    for line in ifile:
        if 'case name' in line: continue # skip hearder line
        info = line.split(',')
        reli = float(info[2])
        solar = float(info[5])
        wind = float(info[6])
        unmet = float(info[7])

        # Remove entries which were from Step 1 which calculated
        # capacities with a target reliability
        if round(reli, 10) == round(unmet, 10): continue

        if reli == 0.0: continue # TMP FIXME
        to_add = abs(unmet/reli - 1.)
        simp[reli][solar][wind][0] += to_add
        simp[reli][solar][wind][1] += 1

    for reli in reliability_values:
        for solar in solar_values:
            for wind in wind_values:
                if simp[reli][solar][wind][1] == 0: continue
                simp[reli][solar][wind][0] = simp[reli][solar][wind][0]/simp[reli][solar][wind][1] # np.sqrt(simp[reli][solar][wind])

    return simp


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

    #results = '/Users/truggles/IDrive-Sync/Carnegie/SEM-1.2/Output_Data/tests_Jul25_v1/results'
    #files = get_output_file_names(results+'/tests_Jul25_v1_2019')
    #results = get_results(files)
    results = simplify_results("Results.txt", reliability_values, wind_values, solar_values)

    ## Take 2D container from get_hourly_info_per_week()
    ## and plot results
    #def plot_daily_over_weeks_surface(hourly_info, save, angle_z=30, angle_plane=50):

    import matplotlib
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D

    # Make data.
    X = wind_values
    Y = solar_values
    X, Y = np.meshgrid(X, Y)


    for reliability in reliability_values:
        if reliability == 0.0: continue
        Z = np.zeros((len(wind_values),len(solar_values)))
        for solar in solar_values:
            for wind in wind_values:
                Z[solar_values.index(solar)][wind_values.index(wind)] = results[reliability][solar][wind][0] * 100.

        print(reliability)
        print(Z)

        fig, ax = plt.subplots()
        im = ax.imshow(Z,interpolation='none',extent=[-0.125,1.125,-0.125,1.125],origin='lower', vmin=0.)

        plt.xticks(wind_values, wind_values)
        plt.yticks(wind_values, wind_values)
        plt.xlabel("Wind Capacity w.r.t Dem. Mean")
        plt.ylabel("Solar Capacity w.r.t Dem. Mean")
        plt.title("Reliability Uncert. for Target Unmet Demand: {:.2f}%".format(reliability*100))
        cbar = ax.figure.colorbar(im)
        cbar.ax.set_ylabel("Relative reliability uncert. (%)")
        plt.savefig("reliability_uncert_for_target_{}.png".format(str(reliability).replace('.','p')))
        plt.clf()


    # Make some plots of a single fraction over reliability range
    techs = OrderedDict()
    techs[(0.0, 0.0)] = ["Wind Zero, Solar Zero", []]
    techs[(0.5, 0.5)] = ["Wind 0.5, Solar 0.5", []]
    techs[(1.0, 0.0)] = ["Wind 1.0, Solar 0.0", []]
    techs[(0.0, 1.0)] = ["Wind 0.0, Solar 1.0", []]
    techs[(1.0, 1.0)] = ["Wind 1.0, Solar 1.0", []]

    inverted = sorted(reliability_values, reverse=True)
    inverted.remove(0.0)
    for reli in inverted:
        for solar in solar_values:
            for wind in wind_values:
                for name, vals in techs.items():
                    if name[0] == wind and name[1] == solar:
                        vals[1].append(results[reli][wind][solar][0] * 100)



    fig, ax = plt.subplots()
    for name, vals in techs.items():
        print(name, vals)
        ax.plot(inverted, vals[1], 'o-', label=vals[0])

    plt.xlabel("Target Unmet Demand: 1 - (annual delivered/annual demand)")
    plt.ylabel("abs[(unmet dem. - target unmet dem.)/target unmet dem.] (%)")
    plt.title("Uncertainty in Achieving Annual Reliability Targets")
    plt.xscale('log', nonposx='clip')
    ax.legend()
    plt.savefig("reliability_uncert_comparison.png")
    
