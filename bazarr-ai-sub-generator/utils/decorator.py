import time
from datetime import timedelta

def measure_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        duration = end_time - start_time
        human_readable_duration = str(timedelta(seconds=duration))
        print(f"Function '{func.__name__}' executed in: {human_readable_duration}")
        return result
    return wrapper
