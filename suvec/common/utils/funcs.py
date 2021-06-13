from typing import Callable
import signal


def safe_mean(lst):
    if len(lst):
        return sum(lst) / len(lst)
    return 0


def shield_from_termination(func: Callable):
    _need_to_stop = False

    def wrapped(*args, **kwargs):
        signal.signal(signal.SIGTERM, _wait_till_func_end)
        res = func(*args, **kwargs)
        if _need_to_stop:
            signal.raise_signal(signal.SIGTERM)
        return res

    def _wait_till_func_end():
        nonlocal _need_to_stop
        _need_to_stop = True

    return wrapped
