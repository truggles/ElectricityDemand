import matplotlib.pyplot as plt
import matplotlib
from matplotlib.pyplot import figure
import numpy as np
from collections import OrderedDict
import helpers as helpers


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


def plot_hist(x, x_label, y_label, title, save, n_bins=100, logY=False):

    matplotlib.rcParams['figure.figsize'] = (6.0, 4.0)
    x.sort() # to use for x range
    fig, ax = plt.subplots()
    n, bins, patches = plt.hist(x, n_bins, range=[x[0], x[-1]], facecolor='g', alpha=0.75)

    plt.xlabel(x_label)
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


def plot_demand_with_daily(fig, ax, daily_x, daily_y, save, title='24 Hour Avg'):
    ax.plot(daily_x, daily_y, 'o', label=title)
    plt.legend()
    plt.grid()
    plt.savefig("plots/"+save+".png")
    return fig, ax

def plot_demand_comparisons(x_val_vec, y_val_vec, title_vec, name):
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

