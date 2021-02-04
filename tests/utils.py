import time
from logging import Logger
from typing import Callable


def measure_for_tests(f: Callable, iterations: int = 50, logger: Logger = None):
    start_time = time.time()
    for i in range(iterations):
        f()

    delta = (time.time() - start_time) / iterations

    if logger is not None:
        logger.info(f'f: {f.__name__}, delta: {delta:.6f} secs')
    else:
        print(f'f: {f.__name__}, delta: {delta:.6f} secs')

    return delta
