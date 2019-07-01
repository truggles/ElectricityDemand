import matplotlib.pyplot as plt
import matplotlib
from matplotlib.pyplot import figure
import numpy as np
from collections import OrderedDict
import helpers as helpers
import matplotlib.dates as mdates # For date formatting


def plot_24_hour_avg(hourly_demand, names, x_label, y_label, title, save):

    matplotlib.rcParams['figure.figsize'] = (6.0, 4.0)

    hours = [i for i in range(1, 25)]

    fig, ax = plt.subplots()
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    plt.title(title)
    for season in hourly_demand.keys() :
        ax.plot(hours, hourly_demand[season], 'o', label=season)
    plt.legend()
    plt.savefig("plots/"+save+".png")
    return hourly_demand


def plot_hist(x, x_label, y_label, title, save, n_bins=100, logY=False, logX=False):

    matplotlib.rcParams['figure.figsize'] = (6.0, 4.0)
    x.sort() # to use for x range
    fig, ax = plt.subplots()
    if len(x) > 0:
        r_low = x[0]
        r_high = x[-1]
    else:
        r_low = 0
        r_high = 10
        n_bins = 10
    n, bins, patches = plt.hist(x, n_bins, range=[r_low, r_high], facecolor='g', alpha=0.75)

    # The commented code below isn't working yet
    ## Adjust ticks and labels if variable binning
    #if type(n_bins) == type([]):
    #    # Set the ticks to be at the edges of the bins.
    #    print(bins)
    #    ax.xaxis.set_major_locator(plt.MultipleLocator( bins ))
    #    #ax.set_xticks(bins)
    #    #print("Ticks: {}".format(ax.get_xticks()))
    #    #ax.set_xticklabels(bins)
    #    # Set the xaxis's tick labels to be formatted with 1 decimal place...
    #    #ax.xaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter('%0.0f'))

    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)
    #plt.text(bins.max()*0.35, n.max()*.95, r'ChiSq / ndof = %.2f' % (chiSq/ len(demand['hour']) ) )
    #plt.axis([-1, 2])
    plt.grid(True)
    if logY:
        plt.yscale('log', nonposy='clip')
    if logX:
        plt.xscale('log', nonposx='clip')
    plt.savefig("plots/"+save+".png")
    return plt


def plot_demand(hourly_data_sets, names, x_label, y_label, title, save, ylim=[]):

    matplotlib.rcParams['figure.figsize'] = (14.0, 6.0)
    months = mdates.MonthLocator()  # every month
    fig, ax = plt.subplots()
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    plt.title(title)

    y_max = 0.
    for hourly_data_set, name in zip(hourly_data_sets, names):
        x = [hour_data.datetime for hour_data in hourly_data_set]
        y = [hour_data.demand for hour_data in hourly_data_set]
        this_max = max(y) if len(y) > 0 else 0
        if this_max > y_max:
            y_max = this_max
        ax.plot(x, y, 'o', label=name)

    if ylim != []:
        ax.set_ylim(ylim[0], ylim[1])
    else:
        old_y_min, old_y_max = ax.get_ylim()
        ax.set_ylim(old_y_min, y_max * 1.1)

    # y-axis commas in thousands if large numbers, with no decimals
    # else 1 decimal place printed
    if y_max > 50:
        ax.yaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
    else:
        ax.yaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter('{x:,.1f}'))

    ax.xaxis.set_minor_locator(months)
    plt.legend()
    plt.grid()
    plt.savefig("plots/"+save+".png")
    return fig, ax

# Add annual means lines over the top
def plot_demand_with_annual_means(fig, ax, x_vals, year_info, save, title='Demand with Annual Means'):
    annual_vals = []
    for k, v in year_info.items():
        for h in range(len(v[1])):
            annual_vals.append(v[2])


    ax.plot(x_vals, annual_vals, 'o', label=title)
    plt.legend()
    plt.grid()
    plt.savefig("plots/"+save+".png")
    return fig, ax


def plot_demand_with_daily(fig, ax, daily_x, daily_y, save, title='24 Hour Avg'):
    ax.plot(daily_x, daily_y, 'o', label=title)
    plt.legend()
    plt.grid()
    plt.savefig("plots/"+save+".png")
    return fig, ax

def plot_demand_comparisons(x_val_vec, y_val_vec, title_vec, name):
    assert(len(x_val_vec) == len(y_val_vec) and len(y_val_vec) == len(title_vec))
    matplotlib.rcParams['figure.figsize'] = (14.0, 6.0)
    fig, ax = plt.subplots()
    ax.set_xlabel('Hour')
    ax.set_ylabel('Demand (MW)')
    plt.title('48 Hr Avg Comparisons')
    
    for x, y, title in zip(x_val_vec, y_val_vec, title_vec):
        ax.plot(x, y, 'o', label=title)
    plt.legend()
    plt.grid()
    plt.savefig("plots/"+name+".png")
    return fig, ax

# Progress along input values and make hist binned in size of missing entries
def histogram_gaps( vals, title, save, n_bins=100, logY=False, logX=False):
    
    gap_recorder = [] # Keep track of the size of the gaps

    previous_entry_was_gap = False
    running_gap_length = 0
    for val in vals:
        if val == -99.99: # Gap detected
            running_gap_length += 1
            previous_entry_was_gap = True
        elif previous_entry_was_gap == True: # Gap is finished, fill entry
            previous_entry_was_gap = False
            gap_recorder.append(running_gap_length)
            running_gap_length = 0
        else: # Complete data previously, complete data now
            continue

    print(gap_recorder)

    plot_hist(gap_recorder, 'Data Gap Size', 'Occurances', title, save, n_bins, logY, logX)
    





