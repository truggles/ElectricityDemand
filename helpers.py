from numpy import percentile



def percentiles(x, val):
    q_a, q_b = percentile(x, val), percentile(x, 100-val)
    return [q_a, q_b]

