"""Stores huge number of ints in different objects and measures memory usage"""

import guppy
import numpy as np


def _measure_memory_usage(func):
    def wrapped(*args, **kwargs):
        memory_checker = guppy.hpy()
        memory_usage_before = memory_checker.heap().size

        res = func(*args, **kwargs)

        memory_used = memory_checker.heap().size - memory_usage_before
        nice_mem_use_mb = round(memory_used / (1024 ** 2), 2)

        print(f"Memory used by {func.__name__}: {nice_mem_use_mb} MB")
        return res
    return wrapped


@_measure_memory_usage
def store_in_list(nb_users):
    users = list(range(nb_users))
    return users


@_measure_memory_usage
def store_in_set(nb_users):
    users = list(range(nb_users))
    users = set(users)
    return users


@_measure_memory_usage
def store_in_arr(nb_users):
    users = list(range(nb_users))
    users = np.array(users, dtype=np.int32)
    return users


if __name__ == "__main__":
    n_users = 10 ** 7
    store_in_list(n_users)
    store_in_set(n_users)
    store_in_arr(n_users)
