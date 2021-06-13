def safe_mean(lst):
    if len(lst):
        return sum(lst) / len(lst)
    return 0
