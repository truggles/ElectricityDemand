import datetime



class SimpleContainer:
    """ Class that for a given time slice contains
    a single demand or power factor value

    # Info
    self.datetime
    self.demand
    """

    def __init__(self, uct_time, val):

        self.datetime = datetime.datetime.strptime(uct_time, '%Y%m%dT%HZ')
        self.month = self.datetime.month
        self.value = val
        self.original_value = val

    def set_value(self, new_val):
        self.value = new_val
