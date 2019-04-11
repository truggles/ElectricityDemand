import matplotlib.pyplot as plt
import matplotlib
from matplotlib.pyplot import figure


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

    matplotlib.rcParams['figure.figsize'] = (20.0, 4.0)
    fig, ax = plt.subplots()
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    if ylim != []:
        ax.set_ylim(ylim[0], ylim[1])
    plt.title(title)

    for hourly_data_set, name in zip(hourly_data_sets, names):
        x = [hour_data.hour for hour_data in hourly_data_set]
        y = [hour_data.demand for hour_data in hourly_data_set]
        ax.plot(x, y, 'o', label=name)

    plt.legend()
    plt.grid()
    plt.savefig("plots/"+save+".png")

