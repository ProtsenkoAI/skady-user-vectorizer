"""Module to run vk_api_main periodically"""
from vk_api_main import run
import os
from time import time, sleep

import sys
sys.stdout = open(f'./resources/logs/schedule_main_runs_stdout_{int(time())}.txt', 'w')
sys.stderr = open(f'./resources/logs/schedule_main_runs_stderr_{int(time())}.txt', 'w')

print('test')


def run_main_every(n_hours):
    while True:
        start_time = time()
        run()
        time_passed = time() - start_time

        need_to_wait = n_hours * 60 ** 2 - time_passed
        print("Sleep for", need_to_wait)
        sleep(need_to_wait)


if __name__ == "__main__":
    run_main_every(24)
