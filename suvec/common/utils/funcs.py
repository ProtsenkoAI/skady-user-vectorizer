from typing import Callable, List, Generator, Optional
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


def split(lst: List, step: Optional[int] = None, parts: Optional[int] = None) -> Generator[List, None, None]:
    both_none = step is None and parts is None
    both_not_none = step is not None and parts is not None
    if both_none or both_not_none:
        raise ValueError("Choose step OR parts parameter")

    if parts is not None:
        step = len(lst) // parts

    start_idx = 0
    while start_idx < len(lst):
        yield lst[start_idx: start_idx + step]
        start_idx += step

