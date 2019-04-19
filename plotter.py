import matplotlib.pyplot as plt
import matplotlib
from matplotlib.pyplot import figure
import numpy as np


def plot_24_hour_avg(hourly_data_set, names, x_label, y_label, title, save):

    matplotlib.rcParams['figure.figsize'] = (6.0, 4.0)

    hourly_demand = np.zeros(24)
    hourly_demand_entries = np.zeros(24) # For averaging
    for d in hourly_data_set:
        if d.missing: continue
        hourly_demand[d.daily_hour] += d.demand
        hourly_demand_entries[d.daily_hour] += 1
    for i in range(len(hourly_demand)):
        hourly_demand[i] = hourly_demand[i] / hourly_demand_entries[i]
    hours = [i for i in range(1, 25)]

    fig, ax = plt.subplots()
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    plt.title(title)
    ax.plot(hours, hourly_demand, 'o', label='Hourly Average')
    plt.legend()
    plt.savefig("plots/"+save+".png")


def plot_hist(x, x_label, y_label, title, save, n_bins=100, logY=False):

    matplotlib.rcParams['figure.figsize'] = (6.0, 4.0)
    x.sort() # to use for x range
    n, bins, patches = plt.hist(x, n_bins, range=[x[0], x[-1]], facecolor='g', alpha=0.75)

    plt.xlabel(x_labell)
    plt.ylabel(y_label)
    plt.title(title)
    #plt.text(bins.max()*0.35, n.max()*.95, r'ChiSq / ndof = %.2f' % (chiSq/ len(demand['hour']) ) )
    #plt.axis([-1, 2])
    plt.grid(True)
    if logY:
        plt.yscale('log', nonposy='clip')
    plt.savefig("plots/"+save+".png")
    return plt


def plot_demand(hourly_data_sets, names, x_label, y_label, title, save, ylim=[]):

    matplotlib.rcParams['figure.figsize'] = (14.0, 6.0)
    fig, ax = plt.subplots()
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    plt.title(title)

    y_max = 0.
    for hourly_data_set, name in zip(hourly_data_sets, names):
        x = [hour_data.hour for hour_data in hourly_data_set]
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

    plt.legend()
    plt.grid()
    plt.savefig("plots/"+save+".png")
    return fig, ax


def plot_demand_with_daily(fig, ax, daily_x, daily_y, save):
    ax.plot(daily_x, daily_y, 'o', label='24 Hour Avg')
    plt.legend()
    plt.grid()
    plt.savefig("plots/"+save+".png")
    return fig, ax
