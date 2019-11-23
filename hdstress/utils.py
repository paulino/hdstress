import threading
import os

console_lock = threading.Lock()

# Decorator
def synchronized(func):            
    def synced_func(*args, **kws):
        with console_lock:
            return func(*args, **kws)
    return synced_func

@synchronized
def print_verbose(st, end='\n'):
    print(st, end=end, flush=True)

@synchronized
def print_err(st):
    print(st)

    
def format_human(size):
    if size >= 2 ** 40:
        return "{:.1f}TB".format(size / 2 ** 40)
    elif size >= 2 ** 30:
        return "{:.1f}GB".format(size / 2 ** 30)
    elif size >= 2 ** 20:
        return "{:.1f}MB".format(size / 2 ** 20)
    elif size >= 2 ** 10:
        return "{:.1f}KB".format(size / 2 ** 10)
    return "{:d}B".format(size)


def get_free_space(work_dir):
    disk = os.statvfs(work_dir)
    free = disk.f_bsize * disk.f_bfree
    return free
